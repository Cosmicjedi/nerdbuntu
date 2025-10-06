#!/bin/bash
# Nerdbuntu GUI Launcher Script
# This script launches the Nerdbuntu GUI application

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Virtual environment not found."
    echo "Please run setup.sh first to create the environment and install dependencies"
    exit 1
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "Warning: .env file not found"
    echo "Azure credentials may not be configured"
    echo "Please copy .env.template to .env and configure your Azure settings"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Launch the GUI
echo "Launching Nerdbuntu GUI..."
python3 "$SCRIPT_DIR/launch_gui.py"

# Deactivate virtual environment on exit
deactivate
