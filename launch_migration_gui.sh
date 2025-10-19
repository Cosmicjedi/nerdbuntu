#!/bin/bash
# Launch ChromaDB to Qdrant Migration GUI

set -e

echo "==================================="
echo " ChromaDB to Qdrant Migration GUI"
echo "==================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "Please install Python 3 and try again"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for required packages
echo ""
echo "Checking dependencies..."

check_package() {
    if python3 -c "import $1" 2>/dev/null; then
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
    echo ""
    read -p "Would you like to install missing packages now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing packages..."
        pip install chromadb sentence-transformers qdrant-client
        echo "✅ Packages installed"
    else
        echo "Please install missing packages manually:"
        echo "  pip install chromadb sentence-transformers qdrant-client"
        exit 1
    fi
fi

echo ""
echo "🚀 Launching Migration GUI..."
echo ""

# Launch the GUI
python3 launch_migration_gui.py

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ GUI closed successfully"
else
    echo ""
    echo "❌ GUI encountered an error"
    exit 1
fi
