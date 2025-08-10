"""
File utility functions
"""
import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional

def file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return os.path.isfile(filepath)

def dir_exists(dirpath: str) -> bool:
    """Check if directory exists"""
    return os.path.isdir(dirpath)

def copy_file(src: str, dst: str) -> bool:
    """Copy file from source to destination"""
    try:
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False

def read_file(filepath: str) -> Optional[str]:
    """Read file content as string"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return None

def read_file_bytes(filepath: str) -> Optional[bytes]:
    """Read file content as bytes"""
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except Exception:
        return None

def create_directory(dirpath: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(dirpath, exist_ok=True)
        return True
    except Exception:
        return False

def compress_directory(directory: str) -> str:
    """Compress directory to ZIP file"""
    zip_path = f"{directory}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, directory)
                zipf.write(file_path, arc_path)
    
    return zip_path

def get_file_size(filepath: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except Exception:
        return 0

def remove_file(filepath: str) -> bool:
    """Remove file if exists"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        return True
    except Exception:
        return False

def get_files_in_directory(directory: str, pattern: str = "*") -> list:
    """Get all files in directory matching pattern"""
    try:
        path = Path(directory)
        return [str(f) for f in path.glob(pattern) if f.is_file()]
    except Exception:
        return []
