#!/bin/bash
# Azure OpenAI Auto-Configuration Wrapper Script

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Azure OpenAI Auto-Configuration${NC}"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${YELLOW}Azure CLI is not installed.${NC}"
    echo ""
    echo "Please install Azure CLI first:"
    echo ""
    echo "  Ubuntu/Debian:"
    echo "    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    echo ""
    echo "  macOS:"
    echo "    brew install azure-cli"
    echo ""
    echo "  Windows (PowerShell):"
    echo "    Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\\AzureCLI.msi"
    echo "    Start-Process msiexec.exe -ArgumentList '/I AzureCLI.msi /quiet'"
    echo ""
    echo "Or visit: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Run the Python configuration script
python3 "$SCRIPT_DIR/configure_azure.py"
