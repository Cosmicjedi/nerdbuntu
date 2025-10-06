# Quick Start Guide

## Prerequisites

Before you begin, make sure you have:
- Azure AI credentials (API endpoint and key)
- Ubuntu 20.04+ or Debian-based Linux distribution

**Getting Azure Credentials:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure AI Service or OpenAI resource
3. Copy the **Endpoint** (e.g., `https://your-service.openai.azure.com/`)
4. Copy one of the **Keys** from the "Keys and Endpoint" section

## Installation (5 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/Cosmicjedi/nerdbuntu.git
cd nerdbuntu
```

### Step 2: Run Setup
```bash
chmod +x setup.sh
./setup.sh
```

**What happens during setup:**
1. ✅ System packages updated
2. ✅ Python virtual environment created
3. ✅ Python packages installed (MarkItDown, Azure AI, ChromaDB, etc.)
4. ✅ **You'll be prompted for your Azure credentials:**
   - Azure AI Endpoint
   - Azure API Key
   - Deployment Name (default: gpt-4o)
5. ✅ Configuration file (.env) generated
6. ✅ Project files downloaded

**Time:** ~5-10 minutes (depending on internet speed)

**Setup prompts will look like:**
```
Azure AI Endpoint (e.g., https://your-service.openai.azure.com/): 
Azure API Key: ****
Azure Deployment Name [default: gpt-4o]: 
```

### Step 3: Activate Environment
```bash
source ~/nerdbuntu/venv/bin/activate
```

## First Use (2 minutes)

### Launch GUI
```bash
cd ~/nerdbuntu
python app.py
```

### Process Your First PDF

1. Click **"Browse"** next to "PDF File"
2. Select any PDF from your computer
3. (Optional) Change output directory
4. Click **"Process PDF"**
5. Wait for completion
6. Find your enhanced markdown in the output directory!

## What You Get

Your PDF is now a markdown file with:
- ✨ Clean, structured content
- 🔗 Semantic backlinks
- 🎯 Key concepts extracted
- 💾 Vector embeddings stored
- 📊 RAG-ready format

## Example Output

**Input:** `research_paper.pdf`

**Output:** `research_paper.md`
```markdown
---
source: research_paper.pdf
processed: 2025-10-06T14:00:00
key_concepts: neural networks, deep learning, AI
chunks: 25
---

# Research Paper Title

[Your content here, beautifully formatted...]

---

## Semantic Backlinks

This document is semantically linked in the vector database.
- **Key Concepts**: neural networks, deep learning, AI
- **Total Chunks**: 25
```

## Next Steps

### Batch Processing
```bash
# Process multiple PDFs at once
python examples.py batch ./input_folder ./output_folder
```

### Query Similar Content
```bash
# Find related content
python examples.py query "machine learning concepts"
```

### Integrate with Your RAG System
```python
from app import SemanticLinker

# Initialize
linker = SemanticLinker(endpoint, api_key)
linker.initialize_vector_db("./vector_db")

# Query
results = linker.find_similar_chunks("your query", n_results=5)
```

## Troubleshooting

### "Azure credentials not found"
Make sure you entered your credentials correctly during setup. You can manually edit the `.env` file:
```bash
nano ~/nerdbuntu/.env
```

Update these values:
```
AZURE_ENDPOINT=https://your-service.openai.azure.com/
AZURE_API_KEY=your-actual-api-key
AZURE_DEPLOYMENT_NAME=gpt-4o
```

### "Module not found"
```bash
source ~/nerdbuntu/venv/bin/activate
pip install -r requirements.txt
```

### GUI won't start
```bash
sudo apt-get install python3-tk
```

### Re-run Setup
If you need to reconfigure:
```bash
cd nerdbuntu
./setup.sh
```
It will ask for your Azure credentials again.

## Azure Credentials Reminder

Your Azure credentials are stored in `~/nerdbuntu/.env` and are:
- ✅ Kept local to your machine
- ✅ Not committed to git (in .gitignore)
- ✅ Used only for API calls to Azure

To view your current configuration:
```bash
cat ~/nerdbuntu/.env
```

## Cost Information

**Azure AI Services costs depend on your usage:**
- Pay-as-you-go pricing
- Estimated: ~$0.10-$1.00 per document (varies by size and features used)
- Monitor usage in Azure Portal

## Support

- 📖 Full docs: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/Cosmicjedi/nerdbuntu/issues)
- 💬 Questions: [GitHub Discussions](https://github.com/Cosmicjedi/nerdbuntu/discussions)

---

**That's it! You're ready to convert PDFs to intelligent, RAG-ready markdown! 🚀**
