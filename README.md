# Nerdbuntu 🚀

**Intelligent PDF to Markdown Converter with Azure AI Integration**

Nerdbuntu is an Ubuntu-based solution that uses MarkItDown with Azure AI Factory to intelligently parse PDFs into markdown files with semantic backlinking for Retrieval Augmented Generation (RAG) systems.

## Features ✨

- 🎯 **Intelligent PDF Parsing**: Converts PDFs to clean, structured markdown
- 🧠 **Azure AI Integration**: Uses Azure AI Services for semantic analysis
- 🔗 **Semantic Backlinking**: Automatically creates semantic links between content
- 💾 **Vector Database**: ChromaDB integration for efficient similarity search
- 🎨 **User-Friendly GUI**: Simple Tkinter interface for file selection
- 📦 **Automated Setup**: One-script installation and Azure configuration
- 🔍 **Key Concept Extraction**: AI-powered concept identification
- 📊 **RAG-Ready Output**: Optimized for retrieval augmented generation

## Prerequisites 📋

- Ubuntu 20.04+ (or Debian-based Linux distribution)
- Internet connection
- Azure account (free tier works)
- Python 3.8+

## Quick Start 🚀

### 1. Clone the Repository

```bash
git clone https://github.com/Cosmicjedi/nerdbuntu.git
cd nerdbuntu
```

### 2. Run Setup Script

The setup script will:
- Install all system dependencies
- Install Azure CLI
- Create Python virtual environment
- Install all Python packages
- Authenticate with Azure
- Create Azure AI Services resources
- Configure environment variables

```bash
chmod +x setup.sh
./setup.sh
```

During setup, you'll be prompted to:
1. Sign in to Azure (browser will open)
2. Confirm Azure subscription

### 3. Launch the Application

```bash
source ~/nerdbuntu/venv/bin/activate
cd ~/nerdbuntu
python app.py
```

## Usage 📖

### GUI Application

1. **Launch the app**: Run `python app.py`
2. **Select PDF**: Click "Browse" to choose your PDF file
3. **Choose Output Directory**: Select where to save the markdown file
4. **Configure Options**:
   - ✅ Enable Semantic Backlinking (recommended)
   - ✅ Extract Key Concepts (recommended)
5. **Process**: Click "Process PDF"
6. **View Results**: Check the log for progress and find your markdown in the output directory

### What Happens During Processing

1. **PDF Conversion**: MarkItDown converts PDF to structured markdown
2. **Semantic Chunking**: Text is split into semantic chunks (~1000 chars)
3. **Embedding Generation**: Each chunk gets a vector embedding
4. **Concept Extraction**: Azure AI extracts key concepts and topics
5. **Vector Storage**: Chunks stored in ChromaDB for similarity search
6. **Metadata Addition**: Document enriched with semantic metadata
7. **Backlink Generation**: Related content automatically linked

### Output Format

Your markdown file will include:

```markdown
---
source: example.pdf
processed: 2025-10-06T12:00:00
key_concepts: machine learning, neural networks, AI
chunks: 15
---

[Your original content here...]

---

## Semantic Backlinks

This document is semantically linked in the vector database.
- **Key Concepts**: machine learning, neural networks, AI
- **Total Chunks**: 15
```

## Architecture 🏗️

### Components

```
┌─────────────────────────────────────────┐
│           Nerdbuntu Application          │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌────────────────┐  │
│  │   Tkinter   │───▶│  MarkItDown    │  │
│  │     GUI     │    │   Converter    │  │
│  └─────────────┘    └────────────────┘  │
│         │                    │           │
│         ▼                    ▼           │
│  ┌──────────────────────────────────┐   │
│  │    Semantic Linker Engine        │   │
│  ├──────────────────────────────────┤   │
│  │  • Chunking                      │   │
│  │  • Embedding (SentenceTransform) │   │
│  │  • Azure AI Analysis             │   │
│  │  • Concept Extraction            │   │
│  └──────────────────────────────────┘   │
│         │                    │           │
│         ▼                    ▼           │
│  ┌─────────────┐    ┌────────────────┐  │
│  │  ChromaDB   │    │   Azure AI     │  │
│  │   Vector    │    │   Services     │  │
│  │     DB      │    │                │  │
│  └─────────────┘    └────────────────┘  │
└─────────────────────────────────────────┘
```

### Data Flow

1. **Input**: PDF file selected via GUI
2. **Conversion**: MarkItDown → Markdown text
3. **Chunking**: Text → Semantic chunks
4. **Embedding**: Chunks → Vector embeddings
5. **AI Analysis**: Azure AI → Key concepts
6. **Storage**: Vectors → ChromaDB
7. **Enrichment**: Markdown + Metadata + Backlinks
8. **Output**: Enhanced markdown file

## Configuration ⚙️

### Environment Variables

Located in `~/nerdbuntu/.env`:

```bash
AZURE_ENDPOINT=https://your-service.cognitiveservices.azure.com/
AZURE_API_KEY=your-api-key
AZURE_DEPLOYMENT_NAME=gpt-4
RESOURCE_GROUP=nerdbuntu-rg
AI_SERVICE_NAME=nerdbuntu-ai-xxxxx
```

### Directory Structure

```
~/nerdbuntu/
├── app.py                    # Main application
├── setup.sh                  # Setup script
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (created by setup)
├── venv/                     # Python virtual environment
└── data/
    ├── input/               # Place PDFs here (optional)
    ├── output/              # Processed markdown files
    └── vector_db/           # ChromaDB storage
```

## Azure Resources 🌐

The setup script creates:

- **Resource Group**: `nerdbuntu-rg`
- **Azure AI Services**: Multi-service account (S0 tier)
  - Includes: GPT models, embeddings, text analytics
  - Location: East US (configurable)

### Cost Considerations

- Azure AI Services (S0 tier): Pay-as-you-go
- Estimated cost: $0.10-$1.00 per document (depending on size)
- Free tier available for testing

## Advanced Usage 🎓

### Batch Processing

```python
from app import SemanticLinker, MarkItDown
import os

# Initialize
md = MarkItDown()
linker = SemanticLinker(endpoint, api_key)
linker.initialize_vector_db("./vector_db")

# Process multiple files
for pdf_file in Path("./input").glob("*.pdf"):
    result = md.convert(str(pdf_file))
    enhanced = linker.add_semantic_links(result.text_content, pdf_file.name)
    
    output_file = f"./output/{pdf_file.stem}.md"
    with open(output_file, 'w') as f:
        f.write(enhanced)
```

### Querying Semantic Links

```python
# Find related content
results = linker.find_similar_chunks("machine learning concepts", n_results=5)

for doc, distance in zip(results['documents'][0], results['distances'][0]):
    print(f"Similarity: {1-distance:.3f}")
    print(doc)
    print("---")
```

## Troubleshooting 🔧

### Common Issues

**Issue**: Azure authentication fails
```bash
# Solution: Re-authenticate
az logout
az login
```

**Issue**: ChromaDB errors
```bash
# Solution: Clear and reinitialize
rm -rf ~/nerdbuntu/data/vector_db/*
python app.py  # Will reinitialize
```

**Issue**: Import errors
```bash
# Solution: Reinstall dependencies
source ~/nerdbuntu/venv/bin/activate
pip install -r requirements.txt
```

**Issue**: Tkinter not found
```bash
# Solution: Install Python Tkinter
sudo apt-get install python3-tk
```

## RAG Integration 🤖

The output markdown files are optimized for RAG systems:

1. **Semantic Chunks**: Pre-chunked for efficient retrieval
2. **Vector Embeddings**: Already computed and stored
3. **Metadata**: Rich context for filtering
4. **Backlinks**: Discover related content
5. **Key Concepts**: Quick topic identification

### Example RAG Pipeline

```python
# 1. Query the vector database
query = "How do neural networks work?"
results = linker.find_similar_chunks(query, n_results=3)

# 2. Use chunks as context for LLM
context = "\n\n".join(results['documents'][0])

# 3. Generate answer with Azure AI
response = client.complete(
    messages=[
        {"role": "system", "content": "Answer based on the context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]
)
```

## Contributing 🤝

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License 📄

MIT License - see LICENSE file for details

## Support 💬

- **Issues**: [GitHub Issues](https://github.com/Cosmicjedi/nerdbuntu/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Cosmicjedi/nerdbuntu/discussions)

## Acknowledgments 🙏

- [MarkItDown](https://github.com/microsoft/markitdown) by Microsoft
- [Azure AI Services](https://azure.microsoft.com/en-us/products/ai-services)
- [ChromaDB](https://www.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

## Roadmap 🗺️

- [ ] Batch processing UI
- [ ] Web interface (Flask/FastAPI)
- [ ] Additional file formats (DOCX, PPTX)
- [ ] Custom embedding models
- [ ] Advanced RAG features
- [ ] Docker container
- [ ] Cloud deployment guide

---

**Made with ❤️ for the RAG community**
