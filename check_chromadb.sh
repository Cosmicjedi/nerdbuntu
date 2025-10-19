#!/bin/bash
# ChromaDB Diagnostic Script Launcher
# Ensures correct Python environment is used

set -e

echo "==================================="
echo " ChromaDB Diagnostic Tool"
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
    exit 1
fi

echo "✅ Python: $($PYTHON_CMD --version)"
echo ""

# Run the diagnostic script with arguments
$PYTHON_CMD check_chromadb.py "$@"
