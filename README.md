# HackBrowserData Python

A Python version of the popular [HackBrowserData](https://github.com/moonD4rk/HackBrowserData) tool for extracting browser data (passwords, cookies, history, bookmarks, etc.) from various browsers.

> **🙏 Credits:** This project is a Python port of the excellent [HackBrowserData](https://github.com/moonD4rk/HackBrowserData) originally written in Go by [moonD4rk](https://github.com/moonD4rk). All credit for the original concept and implementation goes to the original author.

## Features

- Extract browser data from Chrome, Firefox, Edge, Brave and more
- Support for passwords, cookies, history, bookmarks, downloads
- Multiple output formats (JSON, CSV)
- Cross-platform support (Windows, macOS, Linux)
- Command-line interface

## Installation

### Method 1: Install from GitHub (Recommended)
```bash
pip install git+https://github.com/ramune0144/HackBrowserDataPython.git
```

### Method 2: Clone and Install
```bash
git clone https://github.com/ramune0144/HackBrowserDataPython.git
cd HackBrowserDataPython
pip install -e .
```

### Method 3: Install Dependencies Manually
```bash
pip install -r requirements.txt
```

## Usage

After installation, you can use the tool in two ways:

### Using the installed command:
```bash
hackbrowserdata --browser chrome --format json --output results
hackbrowserdata --browser all --format csv --output data --zip
```

### Using Python module:
```bash
python -m hackbrowserdata --browser chrome --format json --output results
python -m hackbrowserdata --browser all --format csv --output data --zip
```

## Supported Browsers

- Google Chrome
- Microsoft Edge
- Mozilla Firefox
- Brave Browser
- Opera
- Vivaldi

## Supported Data Types

- Passwords
- Cookies
- History
- Bookmarks
- Downloads
- Local Storage
- Session Storage

## ⚠️ Security Warning

**CRITICAL SECURITY NOTICE:**
- ❌ **NEVER commit extraction results to version control**
- ❌ **NEVER share extraction files** - they contain real passwords and personal data
- 🔒 **DELETE results immediately** after analysis
- ⚡ **Close all browsers** before running
- 🛡️ **Use only on your own devices**
- 📚 **Educational purposes only**

## Disclaimer

This tool is for educational and security research purposes only. Users are responsible for compliance with applicable laws and regulations.

## Credits

This project is inspired by and based on:

- **[HackBrowserData](https://github.com/moonD4rk/HackBrowserData)** - Original Go implementation by [moonD4rk](https://github.com/moonD4rk)
- All algorithms and extraction methods are adapted from the original project
- Special thanks to the original author for the excellent work and open-source contribution

## License

MIT License - see [LICENSE](LICENSE) file for details.
