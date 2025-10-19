#!/bin/bash
# ChromaDB Diagnostic Script Launcher with Better Environment Detection

set -e

echo "==================================="
echo " ChromaDB Diagnostic Tool"
echo "==================================="
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📂 Working directory: $SCRIPT_DIR"
echo ""

# Function to test if chromadb is available
test_chromadb() {
    $1 -c "import chromadb" 2>/dev/null
    return $?
}

# Try to find a working Python with chromadb
PYTHON_CMD=""

# Option 1: Virtual environment
if [ -d "venv" ]; then
    echo "🔍 Checking virtual environment..."
    source venv/bin/activate
    if test_chromadb "python"; then
        PYTHON_CMD="python"
        echo "✅ Using venv Python with chromadb"
    elif test_chromadb "python3"; then
        PYTHON_CMD="python3"
        echo "✅ Using venv Python3 with chromadb"
    else
        echo "⚠️  Virtual environment found but chromadb not installed in it"
        deactivate 2>/dev/null || true
    fi
fi

# Option 2: System Python3
if [ -z "$PYTHON_CMD" ]; then
    echo "🔍 Checking system Python3..."
    if command -v python3 &> /dev/null; then
        if test_chromadb "python3"; then
            PYTHON_CMD="python3"
            echo "✅ Using system Python3 with chromadb"
        else
            echo "⚠️  Python3 found but chromadb not installed"
        fi
    fi
fi

# Option 3: System Python
if [ -z "$PYTHON_CMD" ]; then
    echo "🔍 Checking system Python..."
    if command -v python &> /dev/null; then
        if test_chromadb "python"; then
            PYTHON_CMD="python"
            echo "✅ Using system Python with chromadb"
        else
            echo "⚠️  Python found but chromadb not installed"
        fi
    fi
fi

# If we still don't have a working Python
if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "❌ Could not find Python with chromadb installed"
    echo ""
    echo "Checking Python installations:"
    echo ""
    
    # Show what we have
    if [ -d "venv" ]; then
        echo "Virtual environment: FOUND"
        source venv/bin/activate
        echo "  Python: $(which python || echo 'not found')"
        echo "  Python3: $(which python3 || echo 'not found')"
        echo "  Version: $(python --version 2>&1 || python3 --version 2>&1 || echo 'unknown')"
        echo "  Installed packages:"
        pip list 2>/dev/null | grep -i chroma || echo "    (no chromadb packages found)"
        deactivate 2>/dev/null || true
    else
        echo "Virtual environment: NOT FOUND"
    fi
    
    echo ""
    if command -v python3 &> /dev/null; then
        echo "System Python3: $(which python3)"
        echo "  Version: $(python3 --version)"
        echo "  Installed packages:"
        python3 -m pip list 2>/dev/null | grep -i chroma || echo "    (no chromadb packages found)"
    else
        echo "System Python3: NOT FOUND"
    fi
    
    echo ""
    echo "To install chromadb:"
    echo ""
    if [ -d "venv" ]; then
        echo "  # Install in virtual environment (recommended)"
        echo "  source venv/bin/activate"
        echo "  pip install chromadb"
    else
        echo "  # Install system-wide"
        echo "  pip3 install chromadb"
        echo ""
        echo "  # Or create virtual environment first"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install chromadb"
    fi
    echo ""
    exit 1
fi

echo "✅ Python: $($PYTHON_CMD --version)"
echo ""

# Run the diagnostic script with arguments
$PYTHON_CMD check_chromadb.py "$@"
