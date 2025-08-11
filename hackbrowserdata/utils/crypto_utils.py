"""
Cryptography utilities for browser data decryption
"""
import os
import base64
import json
from typing import Optional, Union
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import sqlite3
import tempfile

# Windows-specific imports
try:
    import win32crypt
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False

def decrypt_chromium_password(encrypted_password: bytes, master_key: bytes = None) -> str:
    """Decrypt Chromium-based browser password"""
    try:
        if not encrypted_password:
            return ""
        
        # Windows DPAPI decryption (old format)
        if HAS_WIN32 and encrypted_password.startswith(b'\x01\x00\x00\x00'):
            try:
                decrypted = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
                return decrypted.decode('utf-8', errors='ignore')
            except Exception:
                pass
        
        # AES decryption with master key (new format v10/v11)
        if master_key and (encrypted_password.startswith(b'v10') or encrypted_password.startswith(b'v11')):
            try:
                # Extract IV (12 bytes) and encrypted data
                iv = encrypted_password[3:15]
                encrypted_data = encrypted_password[15:-16]  # Remove tag (last 16 bytes)
                tag = encrypted_password[-16:]  # Authentication tag
                
                # Create AES cipher
                cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
                
                # Decrypt with authentication
                decrypted = cipher.decrypt_and_verify(encrypted_data, tag)
                return decrypted.decode('utf-8', errors='ignore')
            except Exception as e:
                # Try without authentication if that fails
                try:
                    iv = encrypted_password[3:15]
                    encrypted_data = encrypted_password[15:]
                    cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
                    decrypted = cipher.decrypt(encrypted_data[:-16])
                    return decrypted.decode('utf-8', errors='ignore')
                except Exception:
                    pass
        
        # Try DPAPI fallback even without the header
        if HAS_WIN32:
            try:
                decrypted = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
                return decrypted.decode('utf-8', errors='ignore')
            except Exception:
                pass
    
    except Exception:
        pass
    
    return ""

def get_chromium_master_key(local_state_path: str) -> Optional[bytes]:
    """Get master key from Chromium Local State file"""
    try:
        if not os.path.exists(local_state_path):
            return None
            
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.load(f)
        
        # Check if os_crypt exists
        if 'os_crypt' not in local_state:
            return None
            
        if 'encrypted_key' not in local_state['os_crypt']:
            return None
            
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        
        # Remove 'DPAPI' prefix (5 bytes)
        if encrypted_key.startswith(b'DPAPI'):
            encrypted_key = encrypted_key[5:]
        
        if HAS_WIN32:
            try:
                master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                return master_key
            except Exception as e:
                # Try different approach
                try:
                    # Sometimes the key doesn't need DPAPI decryption
                    if len(encrypted_key) == 32:  # AES-256 key length
                        return encrypted_key
                except Exception:
                    pass
    
    except Exception:
        pass
    
    return None

def decrypt_firefox_password(encrypted_data: str, master_password: str = "") -> str:
    """Decrypt Firefox password (simplified implementation)"""
    try:
        # Firefox uses NSS library for encryption
        # This is a simplified implementation
        # In practice, you'd need to use NSS library or similar
        return ""
    except Exception:
        return ""

def create_temp_db_copy(db_path: str) -> Optional[str]:
    """Create temporary copy of SQLite database for safe reading"""
    try:
        if not os.path.exists(db_path):
            return None
            
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
        os.close(temp_fd)
        
        # Copy database
        import shutil
        shutil.copy2(db_path, temp_path)
        
        return temp_path
    
    except Exception:
        return None

def safe_sqlite_connect(db_path: str) -> Optional[sqlite3.Connection]:
    """Safely connect to SQLite database"""
    try:
        # Create temporary copy
        temp_path = create_temp_db_copy(db_path)
        if not temp_path:
            return None
            
        # Connect to copy
        conn = sqlite3.connect(temp_path)
        conn.row_factory = sqlite3.Row
        
        return conn
    
    except Exception:
        return None

def time_epoch_to_datetime(epoch_time: int) -> str:
    """Convert epoch time to readable datetime string"""
    try:
        from datetime import datetime
        
        # Chrome uses microseconds since 1601-01-01
        if epoch_time > 10000000000000:  # Likely Chrome time
            # Convert Chrome time to Unix timestamp
            unix_timestamp = (epoch_time / 1000000) - 11644473600
            dt = datetime.fromtimestamp(unix_timestamp)
        else:
            # Regular Unix timestamp
            dt = datetime.fromtimestamp(epoch_time)
            
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    except Exception:
        return str(epoch_time)

def clean_url(url: str) -> str:
    """Clean and validate URL"""
    if not url:
        return ""
    
    # Remove null bytes and clean
    url = url.replace('\x00', '').strip()
    
    # Add protocol if missing
    if url and not url.startswith(('http://', 'https://', 'ftp://', 'file://')):
        url = 'http://' + url
    
    return url
