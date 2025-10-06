#!/bin/bash

# Nerdbuntu Setup Script
# Sets up MarkItDown with Azure AI Factory for intelligent markdown parsing and semantic backlinking

set -e

echo "=== Nerdbuntu Setup Script ==="
echo "This script will install and configure MarkItDown with Azure AI integration"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    echo -e "${YELLOW}Note: This script is optimized for Ubuntu but will attempt to run anyway.${NC}"
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get upgrade -y
elif command -v yum &> /dev/null; then
    sudo yum update -y
else
    echo -e "${YELLOW}Package manager not detected. Skipping system update.${NC}"
fi

echo -e "${GREEN}Step 2: Installing system dependencies...${NC}"
if command -v apt-get &> /dev/null; then
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-tk \
        git \
        curl \
        jq \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        poppler-utils \
        ghostscript
elif command -v yum &> /dev/null; then
    sudo yum install -y \
        python3 \
        python3-pip \
        python3-tkinter \
        git \
        curl \
        jq \
        gcc \
        gcc-c++ \
        make \
        openssl-devel \
        libffi-devel \
        python3-devel \
        poppler-utils \
        ghostscript
else
    echo -e "${RED}Warning: Could not install system dependencies automatically.${NC}"
    echo "Please ensure Python 3, pip, and PDF tools (poppler-utils, ghostscript) are installed."
fi

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${GREEN}Step 3: Setting up Python virtual environment...${NC}"
cd "$SCRIPT_DIR"

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${GREEN}Step 4: Upgrading pip...${NC}"
pip install --upgrade pip

# Install Python packages
echo -e "${GREEN}Step 5: Installing Python packages from requirements.txt...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${YELLOW}Warning: requirements.txt not found. Installing core packages manually...${NC}"
    pip install "markitdown[all]"
    pip install azure-ai-inference azure-identity openai
    pip install python-dotenv sentence-transformers chromadb
    pip install numpy flask pillow beautifulsoup4 requests
fi

echo ""
echo -e "${GREEN}Step 6: Azure Configuration${NC}"

# Check if .env already exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}.env file already exists. Skipping Azure configuration.${NC}"
    echo "To reconfigure, delete .env and run this script again."
else
    echo "Please enter your Azure AI credentials (or press Enter to skip for basic PDF conversion only):"
    echo ""

    # Prompt for Azure endpoint
    read -p "Azure AI Endpoint [press Enter to skip]: " AZURE_ENDPOINT

    if [ -z "$AZURE_ENDPOINT" ]; then
        echo -e "${YELLOW}Skipping Azure configuration. Semantic features will be disabled.${NC}"
        AZURE_ENDPOINT=""
        AZURE_API_KEY=""
        AZURE_DEPLOYMENT_NAME="gpt-4o"
    else
        # Auto-add https:// if missing
        if [[ ! "$AZURE_ENDPOINT" =~ ^https:// ]] && [[ ! "$AZURE_ENDPOINT" =~ ^http:// ]]; then
            echo -e "${YELLOW}Note: Adding https:// prefix to endpoint${NC}"
            AZURE_ENDPOINT="https://${AZURE_ENDPOINT}"
        fi

        # Validate it's now https (not http)
        while [[ ! "$AZURE_ENDPOINT" =~ ^https:// ]]; do
            echo -e "${RED}Error: Endpoint must use https:// (not http://)${NC}"
            read -p "Azure AI Endpoint: " AZURE_ENDPOINT
            # Auto-add https:// if missing
            if [[ ! "$AZURE_ENDPOINT" =~ ^https:// ]] && [[ ! "$AZURE_ENDPOINT" =~ ^http:// ]]; then
                AZURE_ENDPOINT="https://${AZURE_ENDPOINT}"
            fi
        done

        echo -e "${GREEN}Using endpoint: $AZURE_ENDPOINT${NC}"

        # Prompt for Azure API key
        read -sp "Azure API Key: " AZURE_API_KEY
        echo ""

        # Validate API key is not empty
        while [ -z "$AZURE_API_KEY" ]; do
            echo -e "${RED}Error: API Key cannot be empty${NC}"
            read -sp "Azure API Key: " AZURE_API_KEY
            echo ""
        done

        # Prompt for deployment name (optional)
        echo ""
        read -p "Azure Deployment Name [default: gpt-4o]: " AZURE_DEPLOYMENT_NAME
        if [ -z "$AZURE_DEPLOYMENT_NAME" ]; then
            AZURE_DEPLOYMENT_NAME="gpt-4o"
        fi
    fi

    # Create .env file
    echo -e "${GREEN}Step 7: Creating configuration file...${NC}"
    cat > "$SCRIPT_DIR/.env" << EOF
# Azure AI Configuration
AZURE_ENDPOINT=$AZURE_ENDPOINT
AZURE_API_KEY=$AZURE_API_KEY
AZURE_DEPLOYMENT_NAME=$AZURE_DEPLOYMENT_NAME

# Application Settings
INPUT_DIR=data/input
OUTPUT_DIR=data/output
VECTOR_DB_DIR=data/vector_db

# Processing Settings
CHUNK_SIZE=1000
MAX_CONCEPTS=10
EMBEDDING_MODEL=all-MiniLM-L6-v2
EOF
fi

echo -e "${GREEN}Step 8: Creating data directories...${NC}"
mkdir -p "$SCRIPT_DIR/data/input"
mkdir -p "$SCRIPT_DIR/data/output"
mkdir -p "$SCRIPT_DIR/data/vector_db"

# Make scripts executable
chmod +x "$SCRIPT_DIR/launch_gui.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/launch_gui.py" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/app.py" 2>/dev/null || true
chmod +x "$SCRIPT_DIR/examples.py" 2>/dev/null || true

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Project directory: $SCRIPT_DIR"
echo "Virtual environment: $SCRIPT_DIR/venv"
echo ""
if [ -f ".env" ]; then
    echo -e "${YELLOW}Configuration saved to: $SCRIPT_DIR/.env${NC}"
fi
echo ""
echo "To activate the virtual environment, run:"
echo "  ${YELLOW}source $SCRIPT_DIR/venv/bin/activate${NC}"
echo ""
echo "To start the GUI, run:"
echo "  ${YELLOW}./launch_gui.sh${NC}"
echo "  or"
echo "  ${YELLOW}python3 launch_gui.py${NC}"
echo ""
echo "For batch processing, use:"
echo "  ${YELLOW}python3 examples.py batch <input_dir> <output_dir>${NC}"
echo ""
echo "For querying similar content, use:"
echo "  ${YELLOW}python3 examples.py query '<search text>'${NC}"
echo ""
echo -e "${GREEN}Ready to convert PDFs to intelligent markdown! 🚀${NC}"
