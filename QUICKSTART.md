# Quick Start Guide

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
2. ✅ Azure CLI installed
3. ✅ Python virtual environment created
4. ✅ Python packages installed (MarkItDown, Azure AI, ChromaDB, etc.)
5. ✅ Azure authentication (browser opens)
6. ✅ Azure AI Services created automatically
7. ✅ Configuration file (.env) generated

**Time:** ~5-10 minutes (depending on internet speed)

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
```bash
az login
./setup.sh
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

## Cost Information

**Azure AI Services:**
- Free tier: 20 transactions/minute
- S0 tier: Pay-as-you-go (~$0.10-$1.00 per document)
- You can delete resources anytime:
  ```bash
  az group delete --name nerdbuntu-rg
  ```

## Support

- 📖 Full docs: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/Cosmicjedi/nerdbuntu/issues)
- 💬 Questions: [GitHub Discussions](https://github.com/Cosmicjedi/nerdbuntu/discussions)

---

**That's it! You're ready to convert PDFs to intelligent, RAG-ready markdown! 🚀**
