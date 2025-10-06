# Azure Auto-Configuration Script

## 🎯 Purpose

This script automatically connects to your Azure account and discovers the correct configuration for Nerdbuntu's AI features, eliminating manual configuration errors.

## 🚀 Quick Start

```bash
# Make executable
chmod +x configure_azure.sh

# Run it
./configure_azure.sh
```

## ✨ What It Does

The script will automatically:

1. **Check Prerequisites**
   - Verify Azure CLI is installed
   - Check if you're logged into Azure

2. **Connect to Azure**
   - Log you in if needed (opens browser)
   - Show your subscription details

3. **Find Resources**
   - Search for all Azure OpenAI resources in your subscription
   - Display location and resource group for each

4. **Discover Deployments**
   - List all model deployments for your selected resource
   - Show model names and versions

5. **Generate Configuration**
   - Build the correct endpoint URL
   - Retrieve API keys securely
   - Create a properly formatted .env file

## 📋 Prerequisites

### 1. Azure CLI

**Ubuntu/Debian:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**macOS:**
```bash
brew install azure-cli
```

**Windows (PowerShell as Admin):**
```powershell
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -ArgumentList '/I AzureCLI.msi /quiet'
```

Or visit: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

### 2. Azure OpenAI Access

You need:
- An Azure subscription
- Azure OpenAI service enabled (may require approval)
- At least one Azure OpenAI resource created
- At least one model deployment (e.g., GPT-4, GPT-3.5-Turbo)

## 🎬 Usage Example

```bash
$ ./configure_azure.sh

======================================================================
  Azure OpenAI Auto-Configuration for Nerdbuntu
======================================================================

This script will:
  1. Connect to your Azure account
  2. Find your Azure OpenAI resources
  3. Discover your model deployments
  4. Generate the correct .env configuration

======================================================================
  Step 1: Checking Azure CLI
======================================================================

✓ Azure CLI is installed

======================================================================
  Step 2: Checking Azure Login
======================================================================

✓ Logged in as: user@company.com
ℹ Subscription: My Azure Subscription

======================================================================
  Step 3: Finding Azure OpenAI Resources
======================================================================

ℹ Searching for Azure OpenAI resources...
✓ Found 2 Azure OpenAI resource(s)

======================================================================
  Step 4: Selecting Resource
======================================================================

Available Azure OpenAI Resources:

1. my-openai-east
   Location: eastus
   Resource Group: my-rg-east

2. my-openai-west
   Location: westus
   Resource Group: my-rg-west

Select resource (1-2): 1
ℹ Using resource: my-openai-east
✓ Endpoint: https://my-openai-east.openai.azure.com/

======================================================================
  Step 5: Retrieving API Key
======================================================================

✓ API key retrieved successfully
ℹ Key: 12345678...abcd

======================================================================
  Step 6: Finding Model Deployments
======================================================================

Available Model Deployments:

1. gpt4-deployment
   Model: gpt-4
   Version: 0613

2. gpt35-deployment
   Model: gpt-35-turbo
   Version: 0613

Select deployment (1-2): 1
✓ Selected deployment: gpt4-deployment

======================================================================
  Step 8: Saving Configuration
======================================================================

Configuration Summary:
  Endpoint:    https://my-openai-east.openai.azure.com/
  API Key:     12345678...abcd
  Deployment:  gpt4-deployment

✓ Configuration saved to: /home/user/nerdbuntu/.env

======================================================================
  ✓ Configuration Complete!
======================================================================

Your Azure OpenAI is now configured for Nerdbuntu!

Next steps:
  1. Launch the GUI: ./launch_gui.sh
  2. Enable semantic features in the GUI options
  3. Start converting PDFs with AI-powered analysis!
```

## 🔧 Troubleshooting

### "Azure CLI is not installed"

Install Azure CLI first:
- Ubuntu/Debian: `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash`
- macOS: `brew install azure-cli`
- Windows: Download from https://aka.ms/installazurecliwindows

### "Not logged into Azure CLI"

The script will automatically prompt you to log in. A browser window will open for authentication.

### "No Azure OpenAI resources found"

You need to create an Azure OpenAI resource first:
1. Go to https://portal.azure.com
2. Click "Create a resource"
3. Search for "Azure OpenAI"
4. Follow the creation wizard
5. Run this script again

### "No model deployments found"

You need to create a deployment:
1. Go to https://portal.azure.com
2. Navigate to your Azure OpenAI resource
3. Click "Model deployments"
4. Click "Create new deployment"
5. Choose a model (gpt-4, gpt-35-turbo, etc.)
6. Give it a name
7. Run this script again

### ".env file already exists"

The script will ask if you want to overwrite it. If you choose 'n', your existing configuration is preserved.

## 🔐 Security Notes

- API keys are never displayed in full (only first/last characters shown)
- The .env file contains sensitive credentials
- Never commit .env to version control (it's in .gitignore)
- Keep your API keys secure

## 📝 Manual Configuration

If you prefer manual configuration or the script doesn't work, see:
- `AZURE_SETUP.md` - Complete manual configuration guide
- `.env.template` - Template file to copy and edit

## 🎯 What Gets Configured

The script creates a `.env` file with:

```bash
# Azure AI Configuration
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_API_KEY=your-actual-api-key
AZURE_DEPLOYMENT_NAME=your-deployment-name

# Application Settings
INPUT_DIR=data/input
OUTPUT_DIR=data/output
VECTOR_DB_DIR=data/vector_db

# Processing Settings
CHUNK_SIZE=1000
MAX_CONCEPTS=10
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## ✅ Verifying Configuration

After running the script, test your configuration:

```bash
# Activate virtual environment
source venv/bin/activate

# Launch the GUI
./launch_gui.sh
```

In the GUI, you should see:
- "Azure AI: ✓ Configured" at the top
- Azure options enabled (not grayed out)

Try processing a PDF with semantic features enabled!

## 🆘 Getting Help

If you're still having issues:
1. Check the detailed error messages from the script
2. See `AZURE_SETUP.md` for manual configuration steps
3. See `INSTALLATION.md` for general troubleshooting
4. Verify your Azure Portal shows the resource and deployment

## 💡 Pro Tips

- Use GPT-3.5-Turbo for cost-effective processing
- Use GPT-4 for higher quality concept extraction
- Create separate deployments for development and production
- Monitor your Azure costs in the Azure Portal
