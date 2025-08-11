"""
Browser path configurations for different operating systems
"""
import os
import platform
from pathlib import Path
from typing import List, Dict, Any
from core.types import DataType, DEFAULT_CHROMIUM_TYPES, DEFAULT_FIREFOX_TYPES

def get_home_dir() -> str:
    """Get user home directory"""
    return str(Path.home())

class BrowserPaths:
    """Browser path configurations"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.home_dir = get_home_dir()
        
    def get_chrome_paths(self) -> List[str]:
        """Get Chrome profile paths"""
        paths = []
        
        if self.system == 'windows':
            base_paths = [
                os.path.join(self.home_dir, "AppData", "Local", "Google", "Chrome", "User Data"),
                os.path.join(self.home_dir, "AppData", "Local", "Google", "Chrome Beta", "User Data"),
            ]
        elif self.system == 'darwin':  # macOS
            base_paths = [
                os.path.join(self.home_dir, "Library", "Application Support", "Google", "Chrome"),
            ]
        else:  # Linux
            base_paths = [
                os.path.join(self.home_dir, ".config", "google-chrome"),
                os.path.join(self.home_dir, ".config", "google-chrome-beta"),
            ]
        
        # Find all profiles
        for base_path in base_paths:
            if os.path.exists(base_path):
                # Add Default profile
                default_path = os.path.join(base_path, "Default")
                if os.path.exists(default_path):
                    paths.append(default_path)
                
                # Add numbered profiles (Profile 1, Profile 2, etc.)
                for item in os.listdir(base_path):
                    if item.startswith("Profile ") and os.path.isdir(os.path.join(base_path, item)):
                        paths.append(os.path.join(base_path, item))
                        
        return paths
    
    def get_edge_paths(self) -> List[str]:
        """Get Microsoft Edge profile paths"""
        if self.system == 'windows':
            return [
                os.path.join(self.home_dir, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default"),
            ]
        elif self.system == 'darwin':  # macOS
            return [
                os.path.join(self.home_dir, "Library", "Application Support", "Microsoft Edge", "Default"),
            ]
        else:  # Linux
            return [
                os.path.join(self.home_dir, ".config", "microsoft-edge", "Default"),
            ]
    
    def get_firefox_paths(self) -> List[str]:
        """Get Firefox profile paths"""
        if self.system == 'windows':
            firefox_dir = os.path.join(self.home_dir, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
        elif self.system == 'darwin':  # macOS
            firefox_dir = os.path.join(self.home_dir, "Library", "Application Support", "Firefox", "Profiles")
        else:  # Linux
            firefox_dir = os.path.join(self.home_dir, ".mozilla", "firefox")
        
        paths = []
        if os.path.exists(firefox_dir):
            for item in os.listdir(firefox_dir):
                profile_path = os.path.join(firefox_dir, item)
                if os.path.isdir(profile_path) and ('default' in item.lower() or 'release' in item.lower()):
                    paths.append(profile_path)
        
        return paths
    
    def get_brave_paths(self) -> List[str]:
        """Get Brave browser profile paths"""
        paths = []
        
        if self.system == 'windows':
            base_paths = [
                os.path.join(self.home_dir, "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data"),
                os.path.join(self.home_dir, "AppData", "Local", "BraveSoftware", "Brave-Browser-Beta", "User Data"),
                os.path.join(self.home_dir, "AppData", "Local", "BraveSoftware", "Brave-Browser-Dev", "User Data"),
            ]
        elif self.system == 'darwin':  # macOS
            base_paths = [
                os.path.join(self.home_dir, "Library", "Application Support", "BraveSoftware", "Brave-Browser"),
            ]
        else:  # Linux
            base_paths = [
                os.path.join(self.home_dir, ".config", "BraveSoftware", "Brave-Browser"),
            ]
        
        # Find all profiles
        for base_path in base_paths:
            if os.path.exists(base_path):
                # Add Default profile
                default_path = os.path.join(base_path, "Default")
                if os.path.exists(default_path):
                    paths.append(default_path)
                
                # Add numbered profiles
                for item in os.listdir(base_path):
                    if item.startswith("Profile ") and os.path.isdir(os.path.join(base_path, item)):
                        paths.append(os.path.join(base_path, item))
                        
        return paths
    
    def get_opera_paths(self) -> List[str]:
        """Get Opera browser profile paths"""
        if self.system == 'windows':
            return [
                os.path.join(self.home_dir, "AppData", "Roaming", "Opera Software", "Opera Stable"),
                os.path.join(self.home_dir, "AppData", "Roaming", "Opera Software", "Opera GX Stable"),
            ]
        elif self.system == 'darwin':  # macOS
            return [
                os.path.join(self.home_dir, "Library", "Application Support", "com.operasoftware.Opera"),
            ]
        else:  # Linux
            return [
                os.path.join(self.home_dir, ".config", "opera"),
                os.path.join(self.home_dir, ".config", "opera-beta"),
            ]
    
    def get_vivaldi_paths(self) -> List[str]:
        """Get Vivaldi browser profile paths"""
        if self.system == 'windows':
            return [
                os.path.join(self.home_dir, "AppData", "Local", "Vivaldi", "User Data", "Default"),
            ]
        elif self.system == 'darwin':  # macOS
            return [
                os.path.join(self.home_dir, "Library", "Application Support", "Vivaldi", "Default"),
            ]
        else:  # Linux
            return [
                os.path.join(self.home_dir, ".config", "vivaldi", "Default"),
            ]

# Browser configurations
BROWSER_CONFIGS = {
    'chrome': {
        'name': 'Google Chrome',
        'engine': 'chromium',
        'data_types': DEFAULT_CHROMIUM_TYPES,
        'path_getter': 'get_chrome_paths'
    },
    'edge': {
        'name': 'Microsoft Edge',
        'engine': 'chromium',
        'data_types': DEFAULT_CHROMIUM_TYPES,
        'path_getter': 'get_edge_paths'
    },
    'firefox': {
        'name': 'Mozilla Firefox',
        'engine': 'firefox',
        'data_types': DEFAULT_FIREFOX_TYPES,
        'path_getter': 'get_firefox_paths'
    },
    'brave': {
        'name': 'Brave Browser',
        'engine': 'chromium',
        'data_types': DEFAULT_CHROMIUM_TYPES,
        'path_getter': 'get_brave_paths'
    },
    'opera': {
        'name': 'Opera',
        'engine': 'chromium',
        'data_types': DEFAULT_CHROMIUM_TYPES,
        'path_getter': 'get_opera_paths'
    },
    'vivaldi': {
        'name': 'Vivaldi',
        'engine': 'chromium',
        'data_types': DEFAULT_CHROMIUM_TYPES,
        'path_getter': 'get_vivaldi_paths'
    }
}
