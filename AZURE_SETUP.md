# Azure OpenAI Configuration Guide

## Understanding the 404 Error

If you see `Error extracting concepts: (404) resource not found`, it means the Azure OpenAI service cannot find your deployment. This is **not a critical error** - the PDF conversion still works, but AI-powered features are disabled.

## Do You Need Azure?

**NO!** Azure is only needed for advanced semantic features:

### Works WITHOUT Azure:
- ✅ PDF to Markdown conversion
- ✅ File conversion
- ✅ Basic processing

### Requires Azure:
- 🤖 AI-powered key concept extraction
- 🤖 Semantic analysis
- 🤖 Advanced backlinking

**Most users can skip Azure configuration and use basic mode!**

## Setting Up Azure OpenAI (Optional)

### Step 1: Get Azure OpenAI Access

1. Go to [Azure Portal](https://portal.azure.com)
2. Create an Azure OpenAI resource
3. Request access if you don't have it yet (may take a few days)

### Step 2: Create a Deployment

1. In Azure Portal, go to your Azure OpenAI resource
2. Click "Model deployments" → "Create new deployment"
3. Choose a model (e.g., `gpt-4`, `gpt-4o`, `gpt-35-turbo`)
4. Give it a deployment name (e.g., `my-gpt4-deployment`)
5. Note down the deployment name - you'll need it!

### Step 3: Get Your Credentials

You need **three** pieces of information:

1. **Endpoint**: 
   - Format: `https://YOUR-RESOURCE-NAME.openai.azure.com/`
   - Find it in Azure Portal → Your Resource → "Keys and Endpoint"

2. **API Key**:
   - Find it in Azure Portal → Your Resource → "Keys and Endpoint"
   - Use either KEY 1 or KEY 2

3. **Deployment Name**:
   - The name you gave when creating the deployment
   - Find it in Azure Portal → Your Resource → "Model deployments"

### Step 4: Configure .env File

Edit your `.env` file in the project root:

```bash
# Example configuration
AZURE_ENDPOINT=https://my-company-openai.openai.azure.com/
AZURE_API_KEY=abc123def456ghi789jkl012mno345pqr678
AZURE_DEPLOYMENT_NAME=my-gpt4-deployment
```

**Important Notes:**
- The endpoint MUST start with `https://`
- The endpoint MUST end with `/`
- The deployment name must EXACTLY match what's in Azure Portal
- Don't include spaces or quotes around values

## Common Configuration Mistakes

### Mistake 1: Wrong Endpoint Format
❌ **Wrong**: `my-company-openai.openai.azure.com`  
✅ **Correct**: `https://my-company-openai.openai.azure.com/`

### Mistake 2: Wrong Deployment Name
The deployment name in `.env` must EXACTLY match the deployment name in Azure Portal.

❌ **Wrong**: `AZURE_DEPLOYMENT_NAME=gpt-4` (this is the model name)  
✅ **Correct**: `AZURE_DEPLOYMENT_NAME=my-gpt4-deployment` (this is YOUR deployment name)

### Mistake 3: Using the Wrong Endpoint
Make sure you're using the Azure OpenAI endpoint, not the regular OpenAI endpoint.

❌ **Wrong**: `https://api.openai.com/`  
✅ **Correct**: `https://YOUR-RESOURCE.openai.azure.com/`

### Mistake 4: Wrong Region
Your endpoint must be in the same region where you created your Azure OpenAI resource.

## Testing Your Configuration

Run this to test your Azure setup:

```bash
# Activate virtual environment
source venv/bin/activate

# Test Azure connection
python3 << EOF
import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("AZURE_API_KEY")

print(f"Testing endpoint: {endpoint}")

try:
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key)
    )
    print("✓ Client created successfully")
    print("✓ Azure OpenAI is configured correctly!")
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nPlease check your .env configuration.")
EOF
```

## Disabling Azure Features

If you don't want to use Azure features, you have two options:

### Option 1: Leave .env Empty
Just create an empty `.env` file or leave the Azure fields blank:

```bash
AZURE_ENDPOINT=
AZURE_API_KEY=
AZURE_DEPLOYMENT_NAME=
```

### Option 2: Uncheck Azure Options in GUI
When using the GUI, simply uncheck:
- ☐ Enable Semantic Backlinking
- ☐ Extract Key Concepts

The application will work perfectly fine without these features!

## Still Having Issues?

### Check Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Click "Model deployments"
4. Verify your deployment exists and is "Succeeded"

### Check the Error Message
The application now provides detailed error messages that tell you:
- What the problem is (404, 401, etc.)
- Possible causes
- How to fix it

### Use Basic Mode
Remember: **You don't need Azure to use this application!** Basic PDF conversion works great without any Azure configuration.

## Cost Information

Azure OpenAI is a **paid service**. Each API call costs money based on:
- The model you use (GPT-4 is more expensive than GPT-3.5)
- The number of tokens processed
- Your Azure pricing tier

For cost-effective use:
- Use GPT-3.5-Turbo instead of GPT-4
- Process fewer documents with semantic features
- Use basic mode for simple conversions

Check [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/) for current rates.

## Summary

- 🟢 **Basic mode** (no Azure): Free, works great for PDF conversion
- 🟡 **Semantic mode** (with Azure): Paid, adds AI-powered analysis

Choose what works best for your needs!
