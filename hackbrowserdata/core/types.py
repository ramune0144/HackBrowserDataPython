"""
Data types and constants for browser data extraction
"""
from enum import Enum, auto
import os
from pathlib import Path

class DataType(Enum):
    """Browser data types"""
    # Chromium-based browsers
    CHROMIUM_PASSWORD = auto()
    CHROMIUM_COOKIE = auto()
    CHROMIUM_BOOKMARK = auto()
    CHROMIUM_HISTORY = auto()
    CHROMIUM_DOWNLOAD = auto()
    CHROMIUM_CREDIT_CARD = auto()
    CHROMIUM_LOCAL_STORAGE = auto()
    CHROMIUM_SESSION_STORAGE = auto()
    CHROMIUM_EXTENSION = auto()
    CHROMIUM_KEY = auto()
    
    # Firefox-based browsers
    FIREFOX_PASSWORD = auto()
    FIREFOX_COOKIE = auto()
    FIREFOX_BOOKMARK = auto()
    FIREFOX_HISTORY = auto()
    FIREFOX_DOWNLOAD = auto()
    FIREFOX_CREDIT_CARD = auto()
    FIREFOX_LOCAL_STORAGE = auto()
    FIREFOX_SESSION_STORAGE = auto()
    FIREFOX_EXTENSION = auto()
    FIREFOX_KEY4 = auto()

# Default data types for different browser engines
DEFAULT_CHROMIUM_TYPES = [
    DataType.CHROMIUM_PASSWORD,
    DataType.CHROMIUM_COOKIE,
    DataType.CHROMIUM_BOOKMARK,
    DataType.CHROMIUM_HISTORY,
    DataType.CHROMIUM_DOWNLOAD,
    DataType.CHROMIUM_CREDIT_CARD,
    DataType.CHROMIUM_LOCAL_STORAGE,
    DataType.CHROMIUM_SESSION_STORAGE,
]

DEFAULT_FIREFOX_TYPES = [
    DataType.FIREFOX_PASSWORD,
    DataType.FIREFOX_COOKIE,
    DataType.FIREFOX_BOOKMARK,
    DataType.FIREFOX_HISTORY,
    DataType.FIREFOX_DOWNLOAD,
    DataType.FIREFOX_LOCAL_STORAGE,
    DataType.FIREFOX_SESSION_STORAGE,
]

# File names for different data types
CHROMIUM_FILES = {
    DataType.CHROMIUM_PASSWORD: "Login Data",
    DataType.CHROMIUM_COOKIE: "Cookies",
    DataType.CHROMIUM_BOOKMARK: "Bookmarks",
    DataType.CHROMIUM_HISTORY: "History",
    DataType.CHROMIUM_DOWNLOAD: "History",
    DataType.CHROMIUM_CREDIT_CARD: "Web Data",
    DataType.CHROMIUM_LOCAL_STORAGE: "Local Storage",
    DataType.CHROMIUM_SESSION_STORAGE: "Session Storage",
    DataType.CHROMIUM_EXTENSION: "Preferences",
    DataType.CHROMIUM_KEY: "Local State",
}

FIREFOX_FILES = {
    DataType.FIREFOX_PASSWORD: "logins.json",
    DataType.FIREFOX_COOKIE: "cookies.sqlite",
    DataType.FIREFOX_BOOKMARK: "places.sqlite",
    DataType.FIREFOX_HISTORY: "places.sqlite",
    DataType.FIREFOX_DOWNLOAD: "places.sqlite",
    DataType.FIREFOX_LOCAL_STORAGE: "webappsstore.sqlite",
    DataType.FIREFOX_SESSION_STORAGE: "sessionstore-backups",
    DataType.FIREFOX_EXTENSION: "extensions.json",
    DataType.FIREFOX_KEY4: "key4.db",
}

def get_home_dir() -> str:
    """Get user home directory"""
    return str(Path.home())

def get_temp_filename(data_type: DataType) -> str:
    """Generate temporary filename for data extraction"""
    import tempfile
    import uuid
    
    suffix = data_type.name.lower()
    temp_file = os.path.join(tempfile.gettempdir(), f"hack_browser_{suffix}_{uuid.uuid4().hex[:8]}")
    return temp_file

def filter_sensitive_items(data_types: list) -> list:
    """Filter out sensitive data types for limited export"""
    sensitive_types = [
        DataType.CHROMIUM_PASSWORD,
        DataType.CHROMIUM_CREDIT_CARD,
        DataType.FIREFOX_PASSWORD,
        DataType.FIREFOX_CREDIT_CARD,
    ]
    
    return [dt for dt in data_types if dt not in sensitive_types]
