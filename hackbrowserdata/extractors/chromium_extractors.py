"""
Base extractor interface and implementations
"""
import sqlite3
import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.types import DataType
from utils.crypto_utils import safe_sqlite_connect, time_epoch_to_datetime, clean_url

class BaseExtractor(ABC):
    """Base class for data extractors"""
    
    def __init__(self, data_type: DataType):
        self.data_type = data_type
        self.data: List[Dict[str, Any]] = []
    
    @abstractmethod
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract data from file"""
        pass
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Get extracted data"""
        return self.data
    
    def clear_data(self):
        """Clear extracted data"""
        self.data = []

class ChromiumPasswordExtractor(BaseExtractor):
    """Extract passwords from Chromium-based browsers"""
    
    def __init__(self):
        super().__init__(DataType.CHROMIUM_PASSWORD)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract passwords from Login Data file"""
        self.data = []
        
        conn = safe_sqlite_connect(file_path)
        if not conn:
            return self.data
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT origin_url, action_url, username_element, username_value, 
                       password_element, password_value, date_created, date_last_used
                FROM logins
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    from utils.crypto_utils import decrypt_chromium_password
                    
                    password = ""
                    if row[5]:  # password_value exists
                        password = decrypt_chromium_password(row[5], master_key)
                    
                    item = {
                        'origin_url': clean_url(row[0] or ""),
                        'action_url': clean_url(row[1] or ""),
                        'username_element': row[2] or "",
                        'username': row[3] or "",
                        'password_element': row[4] or "",
                        'password': password,
                        'date_created': time_epoch_to_datetime(row[6] or 0),
                        'date_last_used': time_epoch_to_datetime(row[7] or 0)
                    }
                    
                    # Only add entries if they have meaningful data
                    if item['origin_url'] or item['username'] or item['password']:
                        self.data.append(item)
                        
                except Exception:
                    continue
                    
        except sqlite3.Error:
            pass
        finally:
            conn.close()
        
        return self.data

class ChromiumCookieExtractor(BaseExtractor):
    """Extract cookies from Chromium-based browsers"""
    
    def __init__(self):
        super().__init__(DataType.CHROMIUM_COOKIE)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract cookies from Cookies file"""
        self.data = []
        
        conn = safe_sqlite_connect(file_path)
        if not conn:
            return self.data
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT host_key, name, value, path, expires_utc, is_secure, 
                       is_httponly, creation_utc, last_access_utc
                FROM cookies
                ORDER BY creation_utc DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    item = {
                        'host': row[0] or "",
                        'name': row[1] or "",
                        'value': row[2] or "",
                        'path': row[3] or "",
                        'expires': time_epoch_to_datetime(row[4] or 0),
                        'is_secure': bool(row[5]),
                        'is_httponly': bool(row[6]),
                        'created': time_epoch_to_datetime(row[7] or 0),
                        'last_accessed': time_epoch_to_datetime(row[8] or 0)
                    }
                    
                    if item['host'] and item['name']:  # Only add if has meaningful data
                        self.data.append(item)
                        
                except Exception:
                    continue
                    
        except sqlite3.Error:
            pass
        finally:
            conn.close()
        
        return self.data

class ChromiumHistoryExtractor(BaseExtractor):
    """Extract browsing history from Chromium-based browsers"""
    
    def __init__(self):
        super().__init__(DataType.CHROMIUM_HISTORY)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract history from History file"""
        self.data = []
        
        conn = safe_sqlite_connect(file_path)
        if not conn:
            return self.data
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_time
                FROM urls
                ORDER BY last_visit_time DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    item = {
                        'url': clean_url(row[0] or ""),
                        'title': row[1] or "",
                        'visit_count': row[2] or 0,
                        'last_visit_time': time_epoch_to_datetime(row[3] or 0)
                    }
                    
                    if item['url']:  # Only add if has URL
                        self.data.append(item)
                        
                except Exception:
                    continue
                    
        except sqlite3.Error:
            pass
        finally:
            conn.close()
        
        return self.data

class ChromiumBookmarkExtractor(BaseExtractor):
    """Extract bookmarks from Chromium-based browsers"""
    
    def __init__(self):
        super().__init__(DataType.CHROMIUM_BOOKMARK)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract bookmarks from Bookmarks file"""
        self.data = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                bookmarks_data = json.load(f)
            
            # Extract from bookmark tree
            self._extract_bookmark_folder(bookmarks_data.get('roots', {}))
            
        except Exception:
            pass
        
        return self.data
    
    def _extract_bookmark_folder(self, folder_data: dict, folder_path: str = ""):
        """Recursively extract bookmarks from folder"""
        if not isinstance(folder_data, dict):
            return
            
        for key, value in folder_data.items():
            if isinstance(value, dict):
                if value.get('type') == 'url':
                    # This is a bookmark
                    item = {
                        'name': value.get('name', ''),
                        'url': clean_url(value.get('url', '')),
                        'folder': folder_path,
                        'date_added': time_epoch_to_datetime(int(value.get('date_added', 0)))
                    }
                    
                    if item['url']:  # Only add if has URL
                        self.data.append(item)
                        
                elif value.get('type') == 'folder':
                    # This is a folder, recurse
                    new_path = f"{folder_path}/{value.get('name', '')}" if folder_path else value.get('name', '')
                    children = value.get('children', [])
                    if isinstance(children, list):
                        for child in children:
                            if isinstance(child, dict):
                                if child.get('type') == 'url':
                                    item = {
                                        'name': child.get('name', ''),
                                        'url': clean_url(child.get('url', '')),
                                        'folder': new_path,
                                        'date_added': time_epoch_to_datetime(int(child.get('date_added', 0)))
                                    }
                                    if item['url']:
                                        self.data.append(item)
                                elif child.get('type') == 'folder':
                                    self._extract_bookmark_folder({'folder': child}, new_path)

class ChromiumLocalStorageExtractor(BaseExtractor):
    """Extract local storage from Chromium-based browsers using manual LevelDB parsing"""
    
    def __init__(self):
        super().__init__(DataType.CHROMIUM_LOCAL_STORAGE)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract local storage data from LevelDB files"""
        self.data = []
        
        if not os.path.isdir(file_path):
            return self.data
        
        leveldb_path = os.path.join(file_path, "leveldb")
        if not os.path.exists(leveldb_path):
            return self.data
        
        # Use manual parsing since LevelDB libraries don't work well on Windows
        self.data = self._parse_leveldb_manual(leveldb_path)
        
        return self.data
    
    def _parse_leveldb_manual(self, leveldb_path: str) -> List[Dict[str, Any]]:
        """Manually parse LevelDB files based on analysis of structure"""
        items = []
        
        try:
            # Get all LevelDB files
            db_files = [f for f in os.listdir(leveldb_path) 
                       if f.endswith('.ldb') or f.endswith('.log')]
            
            for db_file in db_files:
                file_path = os.path.join(leveldb_path, db_file)
                items.extend(self._parse_leveldb_file_structured(file_path))
        
        except Exception as e:
            pass
        
        # Remove duplicates
        unique_items = {}
        for item in items:
            key = f"{item.get('url', '')}|{item.get('key', '')}"
            if key not in unique_items and item.get('url') and item.get('key'):
                unique_items[key] = item
        
        return list(unique_items.values())
    
    def _parse_leveldb_file_structured(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse LevelDB file using discovered structure"""
        items = []
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Look for URL patterns with underscore prefix
            import re
            
            # Find all underscore-prefixed URLs
            url_pattern = rb'_https?://[^\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f]+'
            
            for match in re.finditer(url_pattern, data):
                url_start = match.start()
                url_end = match.end()
                url_bytes = match.group()
                
                try:
                    # Remove the underscore prefix
                    url = url_bytes[1:].decode('utf-8', errors='ignore')
                    
                    # Get data after the URL (next 300 bytes)
                    after_url = data[url_end:url_end + 300]
                    
                    # Parse the structured data after URL
                    items.extend(self._extract_key_value_pairs(url, after_url))
                    
                except Exception:
                    continue
        
        except Exception:
            pass
        
        return items
    
    def _extract_key_value_pairs(self, url: str, data: bytes) -> List[Dict[str, Any]]:
        """Extract key-value pairs from data after URL"""
        items = []
        
        try:
            # Split by null bytes to find potential key-value pairs
            parts = data.split(b'\x00')
            
            i = 0
            while i < len(parts) - 1:
                try:
                    key_bytes = parts[i]
                    value_bytes = parts[i + 1] if i + 1 < len(parts) else b''
                    
                    # Try to decode key
                    key = key_bytes.decode('utf-8', errors='ignore').strip()
                    
                    # Skip if key starts with control byte
                    if key and key[0].isprintable() and len(key) > 1 and len(key) < 200:
                        
                        # Try to find corresponding value
                        value = ""
                        
                        # Look for value in next few parts
                        for j in range(i + 1, min(i + 4, len(parts))):
                            try:
                                candidate_value = parts[j].decode('utf-8', errors='ignore').strip()
                                
                                # If this looks like a meaningful value
                                if (candidate_value and 
                                    len(candidate_value) > 0 and 
                                    len(candidate_value) < 5000 and
                                    not candidate_value.startswith('http')):  # Don't use URLs as values
                                    
                                    value = candidate_value
                                    break
                            except:
                                continue
                        
                        # Only add if we have both key and value
                        if key and value and self._is_valid_storage_pair(key, value):
                            items.append({
                                'url': url,
                                'key': key,
                                'value': value,
                                'is_meta': False
                            })
                            
                            # Skip the value part we just used
                            i += 2
                            continue
                    
                    i += 1
                    
                except Exception:
                    i += 1
                    continue
        
        except Exception:
            pass
        
        return items
    
    def _is_valid_storage_pair(self, key: str, value: str) -> bool:
        """Check if key-value pair looks valid"""
        # Key validation
        if not key or len(key) < 2 or len(key) > 200:
            return False
        
        # Key should not be mostly control characters
        if sum(1 for c in key if ord(c) < 32) > len(key) * 0.3:
            return False
        
        # Value validation  
        if not value or len(value) > 10000:
            return False
        
        # Value should not be mostly control characters
        if sum(1 for c in value if ord(c) < 32) > len(value) * 0.5:
            return False
        
        # Skip obvious junk patterns
        junk_patterns = [
            all(c in '0123456789abcdefABCDEF' for c in key),  # Pure hex
            key.isdigit(),  # Pure numbers
            len(key) == 1,  # Single characters
            key in ['META:', 'VERSION', 'chrome'],  # Meta keys
        ]
        
        if any(junk_patterns):
            return False
        
        return True

class ChromiumSessionStorageExtractor(BaseExtractor):
    """Extract session storage from Chromium-based browsers"""
    
    def __init__(self):
        super().__init__(DataType.CHROMIUM_SESSION_STORAGE)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract session storage data"""
        self.data = []
        
        # Session Storage is typically stored in "Session Storage" directory
        # Similar to Local Storage but for session-scoped data
        try:
            import os
            if os.path.isdir(file_path):
                # Look for session storage files
                storage_files = [f for f in os.listdir(file_path) if f.endswith(('.ldb', '.log', '.db'))]
                
                for storage_file in storage_files[:5]:  # Limit to first 5 files
                    storage_path = os.path.join(file_path, storage_file)
                    try:
                        with open(storage_path, 'rb') as f:
                            data = f.read()
                            # Simple text extraction
                            text_data = data.decode('utf-8', errors='ignore')
                            
                            # Look for session data patterns
                            lines = text_data.split('\x00')
                            for i, line in enumerate(lines):
                                if len(line) > 5 and ('session' in line.lower() or 'storage' in line.lower()):
                                    try:
                                        # Try to extract session data
                                        if i + 1 < len(lines):
                                            key = line.strip()
                                            value = lines[i + 1].strip() if lines[i + 1] else ""
                                            
                                            if key and len(key) < 200:
                                                item = {
                                                    'origin': key,
                                                    'key': key.split('/')[-1] if '/' in key else key,
                                                    'value': value[:500] if value else "",
                                                    'source_file': storage_file,
                                                    'type': 'session'
                                                }
                                                self.data.append(item)
                                    except Exception:
                                        continue
                                        
                    except Exception:
                        continue
                        
        except Exception:
            pass
        
        return self.data

class ChromiumDownloadExtractor(BaseExtractor):
    """Extract downloads from Chromium-based browsers"""
    
    def __init__(self):
        super().__init__(DataType.CHROMIUM_DOWNLOAD)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract downloads from History file (downloads table)"""
        self.data = []
        
        conn = safe_sqlite_connect(file_path)
        if not conn:
            return self.data
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT target_path, tab_url, total_bytes, start_time, end_time, mime_type, state
                FROM downloads
                ORDER BY start_time DESC
                LIMIT 500
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    item = {
                        'target_path': row[0] or "",
                        'url': clean_url(row[1] or ""),
                        'total_bytes': row[2] or 0,
                        'start_time': time_epoch_to_datetime(row[3] or 0),
                        'end_time': time_epoch_to_datetime(row[4] or 0),
                        'mime_type': row[5] or "",
                        'state': row[6] or 0  # 0=in progress, 1=complete, etc.
                    }
                    
                    if item['target_path'] or item['url']:  # Only add if has meaningful data
                        self.data.append(item)
                        
                except Exception:
                    continue
                    
        except sqlite3.Error:
            pass
        finally:
            conn.close()
        
        return self.data
