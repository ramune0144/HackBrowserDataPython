#!/usr/bin/env python3
"""
HackBrowserData Python Version
A command-line tool for extracting browser data from various browsers.
"""

import click
import os
import sys
from typing import List, Optional
from pathlib import Path

# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.browser_manager import BrowserManager
from core.logger import setup_logger
from utils.file_utils import compress_directory

__version__ = "1.0.0"

@click.command()
@click.option(
    '--browser', '-b',
    default='all',
    help='Browser to extract data from (all, chrome, firefox, edge, brave, opera, vivaldi)'
)
@click.option(
    '--format', '-f',
    default='json',
    type=click.Choice(['json', 'csv']),
    help='Output format (json or csv)'
)
@click.option(
    '--output', '-o',
    default='results',
    help='Output directory for extracted data'
)
@click.option(
    '--profile-path', '-p',
    help='Custom browser profile path'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose logging'
)
@click.option(
    '--compress', '--zip',
    is_flag=True,
    help='Compress results to ZIP file'
)
@click.option(
    '--full-export',
    is_flag=True,
    default=True,
    help='Export all available data types'
)
@click.version_option(version=__version__)
def main(
    browser: str,
    format: str,
    output: str,
    profile_path: Optional[str],
    verbose: bool,
    compress: bool,
    full_export: bool
):
    """
    HackBrowserData Python - Extract browser data from various browsers
    
    Examples:
        python hack_browser_data.py --browser chrome --format json
        python hack_browser_data.py --browser all --output results --zip
    """
    
    # Setup logging
    logger = setup_logger(verbose)
    
    logger.info(f"HackBrowserData Python v{__version__}")
    logger.info(f"Target browser: {browser}")
    logger.info(f"Output format: {format}")
    logger.info(f"Output directory: {output}")
    
    try:
        # Initialize browser manager
        browser_manager = BrowserManager(logger)
        
        # Get available browsers
        browsers = browser_manager.pick_browsers(browser, profile_path)
        
        if not browsers:
            logger.error("No browsers found or accessible")
            sys.exit(1)
        
        logger.info(f"Found {len(browsers)} browser(s) to process")
        
        # Create output directory
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process each browser
        for browser_instance in browsers:
            logger.info(f"Processing {browser_instance.name}...")
            
            try:
                # Extract browser data
                browser_data = browser_instance.extract_data(full_export)
                
                if browser_data:
                    # Output data
                    browser_data.save_to_file(
                        output_dir=str(output_path),
                        browser_name=browser_instance.name,
                        output_format=format
                    )
                    logger.info(f"Successfully extracted data from {browser_instance.name}")
                else:
                    logger.warning(f"No data extracted from {browser_instance.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {browser_instance.name}: {str(e)}")
                continue
        
        # Compress results if requested
        if compress:
            logger.info("Compressing results...")
            try:
                compress_directory(str(output_path))
                logger.info("Results compressed successfully")
            except Exception as e:
                logger.error(f"Compression failed: {str(e)}")
        
        logger.info("Extraction completed!")
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
