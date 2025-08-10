# Contributing to HackBrowserData Python

Thank you for your interest in contributing to HackBrowserData Python! This document provides guidelines for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Windows 10/11 (for full testing)
- Understanding of browser data structures

### Development Setup
```bash
git clone https://github.com/ramune0144/HackBrowserDataPython.git
cd HackBrowserDataPython
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

## 📋 How to Contribute

### 1. Issues
- **Bug Reports**: Include OS, Python version, browser versions
- **Feature Requests**: Describe the use case and expected behavior
- **Security Issues**: Email directly, don't create public issues

### 2. Pull Requests
- Fork the repository
- Create feature branch from `main`
- Write clear commit messages
- Include tests for new features
- Update documentation
- Ensure all tests pass

### 3. Code Standards
- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to all functions/classes
- Include error handling
- Test on multiple browsers

## 🛡️ Security Guidelines

### Critical Rules
- **NEVER** commit real extraction results
- **NEVER** include actual passwords/cookies in code
- **ALWAYS** use synthetic test data
- **ALWAYS** add security warnings to new features

### Testing Security
```bash
# Before committing, always check:
git status
git diff --cached
# Ensure no sensitive files are staged
```

## 🧪 Testing

### Running Tests
```bash
python -m pytest tests/
```

### Manual Testing
- Test with different browsers
- Test with different OS versions
- Verify security warnings work
- Test error handling

## 📝 Documentation

### Required Documentation
- Update README.md for new features
- Add docstrings to all functions
- Update CHANGELOG.md
- Include usage examples

## 🚨 What NOT to Contribute

- Real browser data or credentials
- Code that bypasses security measures
- Features for malicious purposes
- Anything that violates terms of service

## 📞 Getting Help

- Create an issue for questions
- Join discussions in existing issues
- Read the code - it's well documented!

## 🎯 Priority Areas

### High Priority
- Cross-platform support (macOS, Linux)
- Additional browser support
- Performance improvements
- Security enhancements

### Medium Priority  
- GUI interface
- Better error messages
- More output formats
- Documentation improvements

## ✅ Review Process

1. **Automated Checks**: Code style, tests, security scans
2. **Manual Review**: Code quality, security, functionality
3. **Testing**: Multiple browsers and OS versions
4. **Documentation**: Clear and complete

## 📜 Legal

By contributing, you agree that:
- Your contributions are original work
- You grant us license to use your contributions
- You follow all applicable laws
- You understand this is for educational/research purposes

## 🙏 Recognition

All contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

Thank you for helping make HackBrowserData Python better! 🎉
