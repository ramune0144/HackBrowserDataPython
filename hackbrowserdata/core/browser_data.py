"""
Browser data container and output manager
"""
import json
import csv
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from core.types import DataType

class BrowserData:
    """Container for extracted browser data"""
    
    def __init__(self):
        self.data: Dict[DataType, List[Dict[str, Any]]] = {}
        
    def add_data(self, data_type: DataType, items: List[Dict[str, Any]]):
        """Add data for a specific type"""
        if data_type not in self.data:
            self.data[data_type] = []
        self.data[data_type].extend(items)
    
    def get_data(self, data_type: DataType) -> List[Dict[str, Any]]:
        """Get data for a specific type"""
        return self.data.get(data_type, [])
    
    def has_data(self) -> bool:
        """Check if any data exists"""
        return any(items for items in self.data.values())
    
    def get_total_items(self) -> int:
        """Get total number of items across all types"""
        return sum(len(items) for items in self.data.values())
    
    def save_to_file(self, output_dir: str, browser_name: str, output_format: str = 'json'):
        """Save data to files"""
        if not self.has_data():
            return
            
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for data_type, items in self.data.items():
            if not items:
                continue
                
            # Generate filename
            type_name = data_type.name.lower().replace('_', '')
            filename = f"{browser_name}_{type_name}.{output_format}"
            filepath = os.path.join(output_dir, filename)
            
            try:
                if output_format == 'json':
                    self._save_json(filepath, items)
                elif output_format == 'csv':
                    self._save_csv(filepath, items)
                    
            except Exception as e:
                print(f"Error saving {filepath}: {e}")
    
    def _save_json(self, filepath: str, items: List[Dict[str, Any]]):
        """Save data as JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False, default=str)
    
    def _save_csv(self, filepath: str, items: List[Dict[str, Any]]):
        """Save data as CSV"""
        if not items:
            return
            
        # Get all unique keys
        all_keys = set()
        for item in items:
            all_keys.update(item.keys())
        
        fieldnames = sorted(all_keys)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in items:
                # Convert all values to strings for CSV
                csv_item = {k: str(v) if v is not None else '' for k, v in item.items()}
                writer.writerow(csv_item)
    
    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert to dictionary for JSON serialization"""
        return {
            data_type.name: items 
            for data_type, items in self.data.items()
        }
