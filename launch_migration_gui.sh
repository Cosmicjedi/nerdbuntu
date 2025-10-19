#!/bin/bash
# Launch ChromaDB to Qdrant Migration GUI

set -e

echo "==================================="
echo " ChromaDB to Qdrant Migration GUI"
echo "==================================="
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    echo "Activating virtual environment..."
    source venv/bin/activate
    PYTHON_CMD="python"
else
    echo "⚠️  No virtual environment found"
    echo "Using system Python..."
    PYTHON_CMD="python3"
fi

# Check if Python is available
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python is required but not found"
    echo "Please install Python 3 and try again"
    exit 1
fi

echo "✅ Python found: $($PYTHON_CMD --version)"

# Check for required packages
echo ""
echo "Checking dependencies..."

check_package() {
    if $PYTHON_CMD -c "import $1" 2>/dev/null; then
        echo "✅ $1 installed"
        return 0
    else
        echo "❌ $1 not installed"
        return 1
    fi
}

MISSING_PACKAGES=0

# Core packages
check_package "chromadb" || MISSING_PACKAGES=1
check_package "sentence_transformers" || MISSING_PACKAGES=1
check_package "qdrant_client" || MISSING_PACKAGES=1
check_package "tkinter" || {
    echo "⚠️  tkinter not available (may need system package)"
    echo "   On Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "   On macOS: tkinter should be included with Python"
    MISSING_PACKAGES=1
}

if [ $MISSING_PACKAGES -eq 1 ]; then
    echo ""
    echo "⚠️  Some packages are missing"
    
    # Only offer to install if we have a venv or pip
    if [ -d "venv" ] || command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
        echo ""
        read -p "Would you like to install missing packages now? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Installing packages..."
            
            # Use the appropriate pip command
            if [ -d "venv" ]; then
                pip install chromadb sentence-transformers qdrant-client
            elif command -v pip3 &> /dev/null; then
                pip3 install chromadb sentence-transformers qdrant-client
            else
                pip install chromadb sentence-transformers qdrant-client
            fi
            
            echo "✅ Packages installed"
        else
            echo ""
            echo "To install packages manually, run:"
            if [ -d "venv" ]; then
                echo "  source venv/bin/activate"
                echo "  pip install chromadb sentence-transformers qdrant-client"
            else
                echo "  pip3 install chromadb sentence-transformers qdrant-client"
            fi
            exit 1
        fi
    else
        echo ""
        echo "Please install missing packages manually:"
        echo "  pip3 install chromadb sentence-transformers qdrant-client"
        echo ""
        echo "Or run the setup script first:"
        echo "  ./setup.sh"
        exit 1
    fi
fi

echo ""
echo "🚀 Launching Migration GUI..."
echo ""

# Launch the GUI
$PYTHON_CMD launch_migration_gui.py

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ GUI closed successfully"
else
    echo ""
    echo "❌ GUI encountered an error"
    exit 1
fi
