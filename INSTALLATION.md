# Installation & Troubleshooting Guide

## Quick Install

### Method 1: Using setup.sh (Recommended)
```bash
# Clone the repository
git clone https://github.com/Cosmicjedi/nerdbuntu.git
cd nerdbuntu

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Method 2: Manual Installation
```bash
# Clone the repository
git clone https://github.com/Cosmicjedi/nerdbuntu.git
cd nerdbuntu

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Azure (optional, for semantic features)
cp .env.template .env
# Edit .env with your credentials
```

## Important: PDF Conversion Dependencies

MarkItDown requires **all** its optional dependencies for PDF conversion. Make sure you install with:

```bash
pip install markitdown[all]
```

Or use our updated `requirements.txt` which includes `markitdown[all]`.

### System Dependencies

For Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils ghostscript
```

For RedHat/CentOS:
```bash
sudo yum install poppler-utils ghostscript
```

For macOS:
```bash
brew install poppler ghostscript
```

## Common Issues

### Issue 1: "MissingDependencyException with missing pdfconverter"

**Solution:**
```bash
# Activate your virtual environment first
source venv/bin/activate

# Reinstall markitdown with all dependencies
pip install --upgrade "markitdown[all]"
```

### Issue 2: "No module named dotenv"

**Solution:**
```bash
pip install python-dotenv
```

### Issue 3: "Azure credentials not found"

**Solution:**
This is only needed for semantic features (AI-powered backlinking). Basic PDF to Markdown conversion works without Azure!

To enable semantic features:
1. Copy `.env.template` to `.env`
2. Add your Azure OpenAI credentials
3. Restart the application

### Issue 4: GUI won't launch

**Solution:**
```bash
# Make sure tkinter is installed
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo yum install python3-tkinter  # RedHat/CentOS

# Verify virtual environment is activated
source venv/bin/activate

# Launch GUI
python3 launch_gui.py
```

### Issue 5: "Command not found: ./launch_gui.sh"

**Solution:**
```bash
# Make the script executable
chmod +x launch_gui.sh

# Then run it
./launch_gui.sh
```

## Reinstalling Dependencies

If you're having persistent issues, try a clean reinstall:

```bash
# Deactivate virtual environment if active
deactivate

# Remove old virtual environment
rm -rf venv

# Recreate and install
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Verifying Installation

Test if MarkItDown is properly installed:

```bash
source venv/bin/activate
python3 -c "from markitdown import MarkItDown; print('MarkItDown installed successfully!')"
```

Test PDF conversion:

```bash
python3 -c "from markitdown import MarkItDown; md = MarkItDown(); print('PDF converter available!')"
```

## Running Without Azure

The application works in two modes:

1. **Basic Mode** (No Azure needed):
   - PDF to Markdown conversion ✓
   - File conversion ✓
   
2. **Semantic Mode** (Requires Azure):
   - All basic features ✓
   - AI-powered key concept extraction ✓
   - Semantic backlinking ✓
   - Vector database storage ✓

You can use basic mode without any Azure credentials!

## Getting Help

If you're still having issues:

1. Check you're in the virtual environment: `which python` should show `venv/bin/python`
2. Check Python version: `python3 --version` (should be 3.8+)
3. Check installed packages: `pip list | grep markitdown`
4. Look at error messages carefully - they usually point to the missing dependency

## System Requirements

- Python 3.8 or higher
- 2GB RAM minimum (4GB recommended for semantic features)
- Internet connection (for Azure features)
- Ubuntu 20.04+ / macOS 10.14+ / Windows 10+ with WSL
