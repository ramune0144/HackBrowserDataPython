"""
Logger configuration for HackBrowserData Python
"""
import logging
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for Windows support
colorama.init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE
    }
    
    def format(self, record):
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, '')
        if level_color:
            record.levelname = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        
        return super().format(record)

def setup_logger(verbose: bool = False) -> logging.Logger:
    """Setup and configure logger"""
    
    # Create logger
    logger = logging.getLogger('hack_browser_data')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Create formatter
    formatter = ColoredFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger
