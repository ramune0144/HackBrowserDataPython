"""
Browser implementations
"""
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.browser_data import BrowserData
from core.types import DataType, CHROMIUM_FILES, FIREFOX_FILES
from utils.crypto_utils import get_chromium_master_key
from extractors.chromium_extractors import (
    ChromiumPasswordExtractor, ChromiumCookieExtractor, 
    ChromiumHistoryExtractor, ChromiumBookmarkExtractor,
    ChromiumLocalStorageExtractor, ChromiumSessionStorageExtractor,
    ChromiumDownloadExtractor
)
from extractors.firefox_extractors import (
    FirefoxPasswordExtractor, FirefoxCookieExtractor,
    FirefoxHistoryExtractor, FirefoxBookmarkExtractor, 
    FirefoxDownloadExtractor, FirefoxLocalStorageExtractor,
    FirefoxSessionStorageExtractor
)

class BaseBrowser(ABC):
    """Base browser class"""
    
    def __init__(self, name: str, profile_path: str, data_types: List[DataType]):
        self.name = name
        self.profile_path = profile_path
        self.data_types = data_types
        self.master_key: Optional[bytes] = None
    
    @abstractmethod
    def extract_data(self, full_export: bool = True) -> Optional[BrowserData]:
        """Extract browser data"""
        pass
    
    def is_accessible(self) -> bool:
        """Check if browser profile is accessible"""
        return os.path.isdir(self.profile_path)

class ChromiumBrowser(BaseBrowser):
    """Chromium-based browser implementation"""
    
    def __init__(self, name: str, profile_path: str, data_types: List[DataType]):
        super().__init__(name, profile_path, data_types)
        self.engine = "chromium"
    
    def extract_data(self, full_export: bool = True) -> Optional[BrowserData]:
        """Extract data from Chromium-based browser"""
        if not self.is_accessible():
            return None
        
        browser_data = BrowserData()
        
        # Get master key for password decryption
        self.master_key = self._get_master_key()
        
        # Extract each data type
        for data_type in self.data_types:
            if not full_export and self._is_sensitive_data(data_type):
                continue
                
            try:
                extractor = self._get_extractor(data_type)
                if extractor:
                    file_path = self._get_data_file_path(data_type)
                    if file_path and os.path.exists(file_path):
                        items = extractor.extract(file_path, self.master_key)
                        if items:
                            browser_data.add_data(data_type, items)
            except Exception:
                continue
        
        return browser_data if browser_data.has_data() else None
    
    def _get_master_key(self) -> Optional[bytes]:
        """Get master key for decryption"""
        local_state_path = os.path.join(os.path.dirname(self.profile_path), "Local State")
        if os.path.exists(local_state_path):
            return get_chromium_master_key(local_state_path)
        return None
    
    def _get_data_file_path(self, data_type: DataType) -> Optional[str]:
        """Get file path for data type"""
        filename = CHROMIUM_FILES.get(data_type)
        if filename:
            return os.path.join(self.profile_path, filename)
        return None
    
    def _get_extractor(self, data_type: DataType):
        """Get appropriate extractor for data type"""
        extractors = {
            DataType.CHROMIUM_PASSWORD: ChromiumPasswordExtractor,
            DataType.CHROMIUM_COOKIE: ChromiumCookieExtractor,
            DataType.CHROMIUM_HISTORY: ChromiumHistoryExtractor,
            DataType.CHROMIUM_BOOKMARK: ChromiumBookmarkExtractor,
            DataType.CHROMIUM_LOCAL_STORAGE: ChromiumLocalStorageExtractor,
            DataType.CHROMIUM_SESSION_STORAGE: ChromiumSessionStorageExtractor,
            DataType.CHROMIUM_DOWNLOAD: ChromiumDownloadExtractor,
        }
        
        extractor_class = extractors.get(data_type)
        if extractor_class:
            return extractor_class()
        return None
    
    def _is_sensitive_data(self, data_type: DataType) -> bool:
        """Check if data type is sensitive"""
        sensitive_types = [
            DataType.CHROMIUM_PASSWORD,
            DataType.CHROMIUM_CREDIT_CARD,
        ]
        return data_type in sensitive_types

class FirefoxBrowser(BaseBrowser):
    """Firefox browser implementation"""
    
    def __init__(self, name: str, profile_path: str, data_types: List[DataType]):
        super().__init__(name, profile_path, data_types)
        self.engine = "firefox"
    
    def extract_data(self, full_export: bool = True) -> Optional[BrowserData]:
        """Extract data from Firefox browser"""
        if not self.is_accessible():
            return None
        
        browser_data = BrowserData()
        
        # Extract each data type
        for data_type in self.data_types:
            if not full_export and self._is_sensitive_data(data_type):
                continue
                
            try:
                extractor = self._get_extractor(data_type)
                if extractor:
                    file_path = self._get_data_file_path(data_type)
                    if file_path and os.path.exists(file_path):
                        items = extractor.extract(file_path, None)
                        if items:
                            browser_data.add_data(data_type, items)
            except Exception:
                continue
        
        return browser_data if browser_data.has_data() else None
    
    def _get_data_file_path(self, data_type: DataType) -> Optional[str]:
        """Get file path for data type"""
        filename = FIREFOX_FILES.get(data_type)
        if filename:
            file_path = os.path.join(self.profile_path, filename)
            
            # Handle special cases
            if data_type == DataType.FIREFOX_BOOKMARK:
                # Bookmarks are in places.sqlite
                return os.path.join(self.profile_path, "places.sqlite")
            elif data_type == DataType.FIREFOX_HISTORY:
                return os.path.join(self.profile_path, "places.sqlite")
            elif data_type == DataType.FIREFOX_DOWNLOAD:
                return os.path.join(self.profile_path, "places.sqlite")
            elif data_type == DataType.FIREFOX_LOCAL_STORAGE:
                return os.path.join(self.profile_path, "webappsstore.sqlite")
            elif data_type == DataType.FIREFOX_SESSION_STORAGE:
                return os.path.join(self.profile_path, "sessionstore-backups")
                
            return file_path
        return None
    
    def _get_extractor(self, data_type: DataType):
        """Get appropriate extractor for data type"""
        extractors = {
            DataType.FIREFOX_PASSWORD: FirefoxPasswordExtractor,
            DataType.FIREFOX_COOKIE: FirefoxCookieExtractor,
            DataType.FIREFOX_HISTORY: FirefoxHistoryExtractor,
            DataType.FIREFOX_BOOKMARK: FirefoxBookmarkExtractor,
            DataType.FIREFOX_DOWNLOAD: FirefoxDownloadExtractor,
            DataType.FIREFOX_LOCAL_STORAGE: FirefoxLocalStorageExtractor,
            DataType.FIREFOX_SESSION_STORAGE: FirefoxSessionStorageExtractor,
        }
        
        extractor_class = extractors.get(data_type)
        if extractor_class:
            return extractor_class()
        return None
    
    def _is_sensitive_data(self, data_type: DataType) -> bool:
        """Check if data type is sensitive"""
        sensitive_types = [
            DataType.FIREFOX_PASSWORD,
            DataType.FIREFOX_CREDIT_CARD,
        ]
        return data_type in sensitive_types
