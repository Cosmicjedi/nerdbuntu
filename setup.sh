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
    git \
    curl \
    jq \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

# Install Azure CLI
echo -e "${GREEN}Step 3: Installing Azure CLI...${NC}"
if ! command -v az &> /dev/null; then
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
else
    echo "Azure CLI already installed"
fi

# Create project directory
echo -e "${GREEN}Step 4: Creating project directory...${NC}"
PROJECT_DIR="$HOME/nerdbuntu"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create Python virtual environment
echo -e "${GREEN}Step 5: Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo -e "${GREEN}Step 6: Installing Python packages...${NC}"
pip install --upgrade pip
pip install markitdown
pip install azure-ai-inference
pip install azure-identity
pip install openai
pip install python-dotenv
pip install tkinter
pip install sentence-transformers
pip install chromadb
pip install numpy
pip install flask

# Azure Login
echo -e "${GREEN}Step 7: Azure Authentication...${NC}"
echo "Please sign in to Azure..."
az login

# Get Azure subscription
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "Using subscription: $SUBSCRIPTION_ID"

# Set resource group name
RESOURCE_GROUP="nerdbuntu-rg"
LOCATION="eastus"

echo -e "${GREEN}Step 8: Creating Azure resources...${NC}"
echo "Creating resource group: $RESOURCE_GROUP in $LOCATION"

# Create resource group if it doesn't exist
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
else
    echo "Resource group already exists"
fi

# Create Azure AI Services account
AI_SERVICE_NAME="nerdbuntu-ai-$(date +%s)"
echo "Creating Azure AI Services: $AI_SERVICE_NAME"

if ! az cognitiveservices account show --name "$AI_SERVICE_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    az cognitiveservices account create \
        --name "$AI_SERVICE_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --kind "AIServices" \
        --sku "S0" \
        --location "$LOCATION" \
        --yes
fi

# Get the endpoint and key
AZURE_ENDPOINT=$(az cognitiveservices account show \
    --name "$AI_SERVICE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.endpoint" -o tsv)

AZURE_API_KEY=$(az cognitiveservices account keys list \
    --name "$AI_SERVICE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "key1" -o tsv)

# Create .env file
echo -e "${GREEN}Step 9: Creating configuration file...${NC}"
cat > "$PROJECT_DIR/.env" << EOF
AZURE_ENDPOINT=$AZURE_ENDPOINT
AZURE_API_KEY=$AZURE_API_KEY
AZURE_DEPLOYMENT_NAME=gpt-4
RESOURCE_GROUP=$RESOURCE_GROUP
AI_SERVICE_NAME=$AI_SERVICE_NAME
EOF

echo -e "${GREEN}Step 10: Creating data directories...${NC}"
mkdir -p "$PROJECT_DIR/data/input"
mkdir -p "$PROJECT_DIR/data/output"
mkdir -p "$PROJECT_DIR/data/vector_db"

# Download project files from GitHub
echo -e "${GREEN}Step 11: Downloading project files...${NC}"
if [ ! -f "$PROJECT_DIR/app.py" ]; then
    echo "app.py will be created by the repository"
fi

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Virtual environment: $PROJECT_DIR/venv"
echo ""
echo "To activate the virtual environment, run:"
echo "  source $PROJECT_DIR/venv/bin/activate"
echo ""
echo "To start the application, run:"
echo "  cd $PROJECT_DIR && python app.py"
echo ""
echo "Azure Resources Created:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  AI Service: $AI_SERVICE_NAME"
echo "  Endpoint: $AZURE_ENDPOINT"
echo ""
echo -e "${YELLOW}Configuration saved to: $PROJECT_DIR/.env${NC}"
