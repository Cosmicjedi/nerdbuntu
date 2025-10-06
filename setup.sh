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
if ! grep -q "Ubuntu" /etc/os-release; then
    echo -e "${RED}Warning: This script is designed for Ubuntu. Continue anyway? (y/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo -e "${GREEN}Step 2: Installing system dependencies...${NC}"
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
    python3-dev

# Create project directory
echo -e "${GREEN}Step 3: Creating project directory...${NC}"
PROJECT_DIR="$HOME/nerdbuntu"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create Python virtual environment
echo -e "${GREEN}Step 4: Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo -e "${GREEN}Step 5: Installing Python packages...${NC}"
pip install --upgrade pip
pip install markitdown
pip install azure-ai-inference
pip install azure-identity
pip install openai
pip install python-dotenv
pip install sentence-transformers
pip install chromadb
pip install numpy
pip install flask
pip install pillow
pip install beautifulsoup4
pip install requests

echo ""
echo -e "${GREEN}Step 6: Azure Configuration${NC}"
echo "Please enter your Azure AI credentials:"
echo ""

# Prompt for Azure endpoint
read -p "Azure AI Endpoint (e.g., https://your-service.openai.azure.com/): " AZURE_ENDPOINT

# Validate endpoint format
while [[ ! "$AZURE_ENDPOINT" =~ ^https:// ]]; do
    echo -e "${RED}Error: Endpoint must start with https://${NC}"
    read -p "Azure AI Endpoint: " AZURE_ENDPOINT
done

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

# Create .env file
echo -e "${GREEN}Step 7: Creating configuration file...${NC}"
cat > "$PROJECT_DIR/.env" << EOF
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

echo -e "${GREEN}Step 8: Creating data directories...${NC}"
mkdir -p "$PROJECT_DIR/data/input"
mkdir -p "$PROJECT_DIR/data/output"
mkdir -p "$PROJECT_DIR/data/vector_db"

echo -e "${GREEN}Step 9: Downloading project files from GitHub...${NC}"
# Download app.py if it doesn't exist
if [ ! -f "$PROJECT_DIR/app.py" ]; then
    echo "Downloading app.py..."
    curl -sSL https://raw.githubusercontent.com/Cosmicjedi/nerdbuntu/main/app.py -o "$PROJECT_DIR/app.py"
fi

# Download examples.py if it doesn't exist
if [ ! -f "$PROJECT_DIR/examples.py" ]; then
    echo "Downloading examples.py..."
    curl -sSL https://raw.githubusercontent.com/Cosmicjedi/nerdbuntu/main/examples.py -o "$PROJECT_DIR/examples.py"
fi

# Download backup_restore.sh if it doesn't exist
if [ ! -f "$PROJECT_DIR/backup_restore.sh" ]; then
    echo "Downloading backup_restore.sh..."
    curl -sSL https://raw.githubusercontent.com/Cosmicjedi/nerdbuntu/main/backup_restore.sh -o "$PROJECT_DIR/backup_restore.sh"
    chmod +x "$PROJECT_DIR/backup_restore.sh"
fi

# Make scripts executable
chmod +x "$PROJECT_DIR/app.py" 2>/dev/null || true
chmod +x "$PROJECT_DIR/examples.py" 2>/dev/null || true

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Virtual environment: $PROJECT_DIR/venv"
echo ""
echo -e "${YELLOW}Configuration saved to: $PROJECT_DIR/.env${NC}"
echo ""
echo "To activate the virtual environment, run:"
echo "  ${YELLOW}source $PROJECT_DIR/venv/bin/activate${NC}"
echo ""
echo "To start the application, run:"
echo "  ${YELLOW}cd $PROJECT_DIR && python app.py${NC}"
echo ""
echo "For batch processing, use:"
echo "  ${YELLOW}python examples.py batch <input_dir> <output_dir>${NC}"
echo ""
echo "For querying similar content, use:"
echo "  ${YELLOW}python examples.py query '<search text>'${NC}"
echo ""
echo "To backup your data, use:"
echo "  ${YELLOW}./backup_restore.sh backup${NC}"
echo ""
echo -e "${GREEN}Ready to convert PDFs to intelligent markdown! 🚀${NC}"
