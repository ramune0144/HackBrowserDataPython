"""
Browser manager for discovering and managing browser instances
"""
import os
import logging
from typing import List, Optional
from browsers.browser_paths import BrowserPaths, BROWSER_CONFIGS
from browsers.browser_impl import ChromiumBrowser, FirefoxBrowser, BaseBrowser

class BrowserManager:
    """Manages browser discovery and instantiation"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.browser_paths = BrowserPaths()
    
    def pick_browsers(self, browser_name: str, profile_path: Optional[str] = None) -> List[BaseBrowser]:
        """Pick browsers based on name and optional custom profile path"""
        browsers = []
        
        if browser_name.lower() == 'all':
            # Get all available browsers
            for browser_key in BROWSER_CONFIGS.keys():
                browsers.extend(self._get_browsers_for_type(browser_key, profile_path))
        else:
            # Get specific browser
            browser_key = browser_name.lower()
            if browser_key in BROWSER_CONFIGS:
                browsers.extend(self._get_browsers_for_type(browser_key, profile_path))
            else:
                self.logger.warning(f"Unknown browser: {browser_name}")
        
        # Filter accessible browsers
        accessible_browsers = []
        for browser in browsers:
            if browser.is_accessible():
                accessible_browsers.append(browser)
                self.logger.info(f"✓ Found accessible browser: {browser.name} at {browser.profile_path}")
            else:
                self.logger.debug(f"✗ Browser not accessible: {browser.name} at {browser.profile_path}")
        
        return accessible_browsers
    
    def _get_browsers_for_type(self, browser_key: str, custom_profile_path: Optional[str] = None) -> List[BaseBrowser]:
        """Get browser instances for a specific browser type"""
        browsers = []
        
        if browser_key not in BROWSER_CONFIGS:
            return browsers
        
        config = BROWSER_CONFIGS[browser_key]
        
        # Get profile paths
        if custom_profile_path:
            # Use custom profile path
            profile_paths = [custom_profile_path] if os.path.exists(custom_profile_path) else []
        else:
            # Get default paths
            path_getter_name = config['path_getter']
            path_getter = getattr(self.browser_paths, path_getter_name)
            profile_paths = path_getter()
        
        # Create browser instances
        for profile_path in profile_paths:
            if os.path.exists(profile_path):
                try:
                    if config['engine'] == 'chromium':
                        browser = ChromiumBrowser(
                            name=config['name'],
                            profile_path=profile_path,
                            data_types=config['data_types']
                        )
                    elif config['engine'] == 'firefox':
                        browser = FirefoxBrowser(
                            name=config['name'],
                            profile_path=profile_path,
                            data_types=config['data_types']
                        )
                    else:
                        continue
                    
                    browsers.append(browser)
                    
                except Exception as e:
                    self.logger.error(f"Error creating browser instance for {config['name']}: {e}")
        
        return browsers
    
    def get_available_browser_names(self) -> List[str]:
        """Get list of available browser names"""
        return list(BROWSER_CONFIGS.keys())
    
    def get_browser_info(self, browser_key: str) -> dict:
        """Get information about a specific browser"""
        return BROWSER_CONFIGS.get(browser_key, {})
