# Nerdbuntu 🚀

**Intelligent PDF to Markdown Converter with Azure AI Integration**

Nerdbuntu is an Ubuntu-based solution that uses MarkItDown with Azure AI to intelligently parse PDFs into markdown files with semantic backlinking for Retrieval Augmented Generation (RAG) systems.

## Features ✨

- 🎯 **Intelligent PDF Parsing**: Converts PDFs to clean, structured markdown
- 🧠 **Azure AI Integration**: Uses Azure AI Services for semantic analysis
- 🔗 **Semantic Backlinking**: Automatically creates semantic links between content
- 💾 **Vector Database**: ChromaDB integration for efficient similarity search
- 🎨 **User-Friendly GUI**: Simple Tkinter interface for file selection
- 📦 **Automated Setup**: One-script installation with your Azure credentials
- 🔍 **Key Concept Extraction**: AI-powered concept identification
- 📊 **RAG-Ready Output**: Optimized for retrieval augmented generation
- 🚀 **Export/Import**: Bundle and transport RAG data between machines

## Prerequisites 📋

- Ubuntu 20.04+ (or Debian-based Linux distribution)
- Internet connection
- **Azure AI credentials** (API endpoint and key)
- Python 3.8+

### Getting Azure Credentials

Before running the setup, you'll need your Azure AI credentials:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI or AI Services resource
3. Go to "Keys and Endpoint" section
4. Copy the **Endpoint** (e.g., `https://your-service.openai.azure.com/`)
5. Copy one of the **Keys**
6. Note your **Deployment Name** (e.g., `gpt-4o`, `gpt-4`)

## Quick Start 🚀

### 1. Clone the Repository

```bash
git clone https://github.com/Cosmicjedi/nerdbuntu.git
cd nerdbuntu
```

### 2. Run Setup Script

The setup script will:
- Install all system dependencies
- Create Python virtual environment
- Install all Python packages (MarkItDown, Azure AI, ChromaDB, etc.)
- **Prompt you for your Azure credentials**
- Configure environment variables

```bash
chmod +x setup.sh
./setup.sh
```

During setup, you'll be prompted to enter:
- **Azure AI Endpoint**: `https://your-service.openai.azure.com/`
- **Azure API Key**: Your API key (hidden when typing)
- **Deployment Name**: Your model deployment name (default: `gpt-4o`)

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

## Exporting and Importing RAG Data 📦

### Exporting Your Data

If you're processing PDFs on one machine but will use the RAG data on another machine, use the export script:

```bash
cd ~/nerdbuntu
chmod +x export.sh
./export.sh
```

This creates a ZIP archive containing:
- ✅ All processed markdown files
- ✅ Complete ChromaDB vector database
- ✅ Metadata and import instructions
- ✅ Integration examples

The export is saved to `~/nerdbuntu/exports/nerdbuntu_rag_export_TIMESTAMP.zip`

### Importing on Destination Machine

On your destination machine (where you'll use the RAG data):

```bash
# Option 1: If you have Nerdbuntu installed
chmod +x import.sh
./import.sh ~/path/to/nerdbuntu_rag_export_*.zip

# Option 2: Manual extraction
unzip nerdbuntu_rag_export_*.zip
cd nerdbuntu_rag_export_*
# Follow instructions in IMPORT_README.md
```

The import script offers two modes:
- **Merge**: Add to existing data (recommended)
- **Replace**: Clear existing data and import fresh

### Transport Methods

```bash
# Via SCP
scp ~/nerdbuntu/exports/nerdbuntu_rag_export_*.zip user@destination:/path/

# Via cloud storage
aws s3 cp ~/nerdbuntu/exports/nerdbuntu_rag_export_*.zip s3://bucket/

# Via USB/external drive
cp ~/nerdbuntu/exports/nerdbuntu_rag_export_*.zip /media/usb/
```

## Advanced Usage 🎓

### Batch Processing

Use the included examples script:

```bash
# Process multiple PDFs at once
python examples.py batch ./input_folder ./output_folder
```

Or use it programmatically:

```python
from app import SemanticLinker
from markitdown import MarkItDown
from pathlib import Path

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

```bash
# Find related content
python examples.py query "machine learning concepts"
```

Or programmatically:

```python
# Find related content
results = linker.find_similar_chunks("machine learning concepts", n_results=5)

for doc, distance in zip(results['documents'][0], results['distances'][0]):
    print(f"Similarity: {1-distance:.3f}")
    print(doc)
    print("---")
```

## Configuration ⚙️

### Environment Variables

Located in `~/nerdbuntu/.env`:

```bash
# Azure AI Configuration
AZURE_ENDPOINT=https://your-service.openai.azure.com/
AZURE_API_KEY=your-api-key
AZURE_DEPLOYMENT_NAME=gpt-4o

# Application Settings
INPUT_DIR=data/input
OUTPUT_DIR=data/output
VECTOR_DB_DIR=data/vector_db

# Processing Settings
CHUNK_SIZE=1000
MAX_CONCEPTS=10
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

You can manually edit this file if you need to change your Azure credentials:
```bash
nano ~/nerdbuntu/.env
```

### Directory Structure

```
~/nerdbuntu/
├── app.py                    # Main application
├── setup.sh                  # Setup script
├── export.sh                 # Export RAG data
├── import.sh                 # Import RAG data
├── examples.py               # Advanced usage examples
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (created by setup)
├── venv/                     # Python virtual environment
├── exports/                  # Export archives
└── data/
    ├── input/               # Place PDFs here (optional)
    ├── output/              # Processed markdown files
    └── vector_db/           # ChromaDB storage
```

## Troubleshooting 🔧

### Common Issues

**Issue**: "Azure credentials not found"
```bash
# Solution: Check your .env file
cat ~/nerdbuntu/.env

# Or re-run setup to enter credentials again
./setup.sh
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

**Issue**: Azure API errors
- Verify your endpoint URL is correct (must start with `https://`)
- Check your API key is valid
- Ensure your deployment name matches your Azure resource
- Verify you have quota/credits available in Azure

## RAG Integration 🤖

The output markdown files are optimized for RAG systems:

1. **Semantic Chunks**: Pre-chunked for efficient retrieval
2. **Vector Embeddings**: Already computed and stored
3. **Metadata**: Rich context for filtering
4. **Backlinks**: Discover related content
5. **Key Concepts**: Quick topic identification

### Example RAG Pipeline

```python
from app import SemanticLinker

# Initialize
linker = SemanticLinker(azure_endpoint, azure_api_key)
linker.initialize_vector_db("./vector_db")

# 1. Query the vector database
query = "How do neural networks work?"
results = linker.find_similar_chunks(query, n_results=3)

# 2. Use chunks as context for LLM
context = "\n\n".join(results['documents'][0])

# 3. Generate answer with Azure AI
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint=azure_endpoint,
    credential=AzureKeyCredential(azure_api_key)
)

response = client.complete(
    messages=[
        {"role": "system", "content": "Answer based on the context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ],
    model="gpt-4o"
)

print(response.choices[0].message.content)
```

## Cost Considerations 💰

Azure AI Services costs depend on your usage:
- Pay-as-you-go pricing
- Estimated: ~$0.10-$1.00 per document (varies by size and features used)
- Monitor usage in [Azure Portal](https://portal.azure.com)
- Set up budget alerts to avoid unexpected charges

## Contributing 🤝

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License 📄

MIT License - see [LICENSE](LICENSE) file for details

## Support 💬

- **Issues**: [GitHub Issues](https://github.com/Cosmicjedi/nerdbuntu/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Cosmicjedi/nerdbuntu/discussions)
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)

## Acknowledgments 🙏

- [MarkItDown](https://github.com/microsoft/markitdown) by Microsoft
- [Azure AI Services](https://azure.microsoft.com/en-us/products/ai-services)
- [ChromaDB](https://www.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

## Roadmap 🗺️

- [x] Export/Import functionality
- [ ] Batch processing UI
- [ ] Web interface (Flask/FastAPI)
- [ ] Additional file formats (DOCX, PPTX)
- [ ] Custom embedding models
- [ ] Advanced RAG features
- [ ] Docker container
- [ ] Cloud deployment guide

---

**Made with ❤️ for the RAG community**