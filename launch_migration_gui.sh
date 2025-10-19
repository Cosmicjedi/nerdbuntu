#!/bin/bash
# Launch ChromaDB to Qdrant Migration GUI
# Supports two-server migration: Server 1 (ChromaDB) and Server 2 (Qdrant)

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
echo ""

check_package() {
    if $PYTHON_CMD -c "import $1" 2>/dev/null; then
        echo "✅ $1 installed"
        return 0
    else
        echo "⚠️  $1 not installed"
        return 1
    fi
}

CHROMADB_AVAILABLE=0
QDRANT_AVAILABLE=0
SENTRANS_AVAILABLE=0
TKINTER_AVAILABLE=0

# Check ChromaDB (needed on Server 1 for export only)
if check_package "chromadb"; then
    CHROMADB_AVAILABLE=1
else
    echo "   → Only needed on Server 1 (for Export tab)"
fi

# Check Sentence Transformers (needed on Server 1 for export only)
if check_package "sentence_transformers"; then
    SENTRANS_AVAILABLE=1
else
    echo "   → Only needed on Server 1 (for Export tab)"
fi

# Check Qdrant Client (needed on Server 2 for import only)
if check_package "qdrant_client"; then
    QDRANT_AVAILABLE=1
else
    echo "   → Only needed on Server 2 (for Import tab)"
fi

# Check tkinter (needed on both servers for GUI)
if check_package "tkinter"; then
    TKINTER_AVAILABLE=1
else
    echo "   → Required on both servers for GUI"
    echo "   On Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "   On macOS: tkinter should be included with Python"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Two-Server Migration Package Requirements:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "SERVER 1 (ChromaDB - Export):"
echo "  - chromadb            $([ $CHROMADB_AVAILABLE -eq 1 ] && echo '✅' || echo '❌')"
echo "  - sentence-transformers $([ $SENTRANS_AVAILABLE -eq 1 ] && echo '✅' || echo '❌')"
echo "  - tkinter             $([ $TKINTER_AVAILABLE -eq 1 ] && echo '✅' || echo '❌')"
echo ""
echo "SERVER 2 (Qdrant - Import):"
echo "  - qdrant-client       $([ $QDRANT_AVAILABLE -eq 1 ] && echo '✅' || echo '❌')"
echo "  - tkinter             $([ $TKINTER_AVAILABLE -eq 1 ] && echo '✅' || echo '❌')"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Only block if tkinter is missing (required for GUI on both)
if [ $TKINTER_AVAILABLE -eq 0 ]; then
    echo "❌ Critical: tkinter is required for the GUI on both servers"
    echo ""
    echo "Install tkinter:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  Fedora/RHEL:   sudo dnf install python3-tkinter"
    echo "  macOS:         Should be included with Python"
    exit 1
fi

# Determine which server setup we're likely on
if [ $CHROMADB_AVAILABLE -eq 1 ] && [ $QDRANT_AVAILABLE -eq 0 ]; then
    echo "💡 Detected: SERVER 1 setup (ChromaDB available)"
    echo "   → Use the 'Export (Server 1)' tab"
    echo ""
elif [ $QDRANT_AVAILABLE -eq 1 ] && [ $CHROMADB_AVAILABLE -eq 0 ]; then
    echo "💡 Detected: SERVER 2 setup (Qdrant available)"
    echo "   → Use the 'Import (Server 2)' tab"
    echo ""
elif [ $CHROMADB_AVAILABLE -eq 1 ] && [ $QDRANT_AVAILABLE -eq 1 ]; then
    echo "💡 Detected: Single-server setup (both databases available)"
    echo "   → You can use both Export and Import tabs"
    echo ""
else
    echo "⚠️  Warning: Neither ChromaDB nor Qdrant detected"
    echo ""
    echo "To install packages for your server:"
    echo ""
    echo "For SERVER 1 (Export only):"
    if [ -d "venv" ]; then
        echo "  pip install chromadb sentence-transformers"
    else
        echo "  pip3 install chromadb sentence-transformers"
    fi
    echo ""
    echo "For SERVER 2 (Import only):"
    if [ -d "venv" ]; then
        echo "  pip install qdrant-client"
    else
        echo "  pip3 install qdrant-client"
    fi
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Offer to install missing packages if we can detect which server
MISSING_PACKAGES=0

if [ $CHROMADB_AVAILABLE -eq 1 ] || [ $QDRANT_AVAILABLE -eq 1 ]; then
    # We have at least one DB, so we can proceed
    :
else
    # Neither DB available, offer to install
    if [ -d "venv" ] || command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
        echo ""
        read -p "Would you like to install packages for this server? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo "Which server is this?"
            echo "  1) Server 1 (ChromaDB - for Export)"
            echo "  2) Server 2 (Qdrant - for Import)"
            echo "  3) Single server (both)"
            read -p "Enter choice (1-3): " -n 1 -r
            echo ""
            
            if [[ $REPLY == "1" ]]; then
                echo "Installing Server 1 packages..."
                if [ -d "venv" ]; then
                    pip install chromadb sentence-transformers
                elif command -v pip3 &> /dev/null; then
                    pip3 install chromadb sentence-transformers
                else
                    pip install chromadb sentence-transformers
                fi
                echo "✅ Server 1 packages installed"
            elif [[ $REPLY == "2" ]]; then
                echo "Installing Server 2 packages..."
                if [ -d "venv" ]; then
                    pip install qdrant-client
                elif command -v pip3 &> /dev/null; then
                    pip3 install qdrant-client
                else
                    pip install qdrant-client
                fi
                echo "✅ Server 2 packages installed"
            elif [[ $REPLY == "3" ]]; then
                echo "Installing all packages..."
                if [ -d "venv" ]; then
                    pip install chromadb sentence-transformers qdrant-client
                elif command -v pip3 &> /dev/null; then
                    pip3 install chromadb sentence-transformers qdrant-client
                else
                    pip install chromadb sentence-transformers qdrant-client
                fi
                echo "✅ All packages installed"
            fi
        fi
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
