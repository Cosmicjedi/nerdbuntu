# Nerdbuntu 🚀

**Intelligent PDF to Markdown Converter with Azure AI Integration**

Nerdbuntu is an Ubuntu-based solution that uses MarkItDown with Azure AI to intelligently parse PDFs into markdown files with semantic backlinking for Retrieval Augmented Generation (RAG) systems.

## Features ✨

- 🎯 **Intelligent PDF Parsing**: Converts PDFs to clean, structured markdown
- 🧠 **Azure AI Integration**: Uses Azure AI Services for semantic analysis
- 🔗 **Semantic Backlinking**: Automatically creates semantic links between content
- 💾 **Vector Database**: ChromaDB integration with Qdrant migration support
- 🎨 **User-Friendly GUI**: Simple Tkinter interface with single file and bulk processing modes
- 📦 **Bulk Directory Processing**: Process entire directories of PDFs at once (NEW!)
- 🔄 **Qdrant Migration**: Export ChromaDB data to Qdrant for better performance (NEW!)
- 📦 **Automated Setup**: One-script installation with your Azure credentials
- 🔍 **Key Concept Extraction**: AI-powered concept identification
- 📊 **RAG-Ready Output**: Optimized for retrieval augmented generation
- 💾 **Backup & Restore**: Complete data backup and restoration system

## What's New 🎉

### Version 2.0 Features

**Bulk Processing Mode**
- Process entire directories of PDFs
- File pattern matching (e.g., `*.pdf`, `report_*.pdf`)
- Smart skip logic (skip already processed files)
- Detailed progress tracking and statistics
- See [BULK_PROCESSING_GUIDE.md](BULK_PROCESSING_GUIDE.md) for details

**Qdrant Migration**
- Export ChromaDB to Qdrant-compatible format
- Import data into Qdrant with verification
- 5-13x faster search performance
- Production-ready vector database
- See [CHROMADB_TO_QDRANT_MIGRATION.md](CHROMADB_TO_QDRANT_MIGRATION.md) for details

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
./launch_gui.sh
```

## Usage 📖

### Single File Processing

1. **Launch the GUI**
2. Select "Single File - Process one PDF file" mode
3. Click "Browse File" and select your PDF
4. Configure options (semantic processing, concept extraction)
5. Click "Process PDF File"

### Bulk Directory Processing (NEW!)

1. **Launch the GUI**
2. Select "Bulk Directory - Process all PDFs in a directory" mode  
3. Click "Browse Directory" and select folder with PDFs
4. (Optional) Set file pattern (default: `*.pdf`)
5. Enable "Skip files that already have output" to resume jobs
6. Click "Process All PDFs in Directory"
7. Confirm number of files and wait for completion

**See detailed guide:** [BULK_PROCESSING_GUIDE.md](BULK_PROCESSING_GUIDE.md)

### What Happens During Processing

1. **PDF Conversion**: MarkItDown converts PDF to structured markdown
2. **Semantic Chunking**: Text is split into semantic chunks (~1000 chars)
3. **Embedding Generation**: Each chunk gets a vector embedding
4. **Concept Extraction**: Azure AI extracts key concepts and topics
5. **Vector Storage**: Chunks stored in ChromaDB for similarity search
6. **Metadata Addition**: Document enriched with semantic metadata
7. **Backlink Generation**: Related content automatically linked

## Migrating to Qdrant 🔄

For better performance and scalability, migrate from ChromaDB to Qdrant:

### Quick Migration

```bash
# 1. Export ChromaDB data
python export_to_qdrant.py

# 2. Setup Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# 3. Import to Qdrant
python import_to_qdrant.py --json-file exports/qdrant/TIMESTAMP/export.json
```

**Performance Improvements:**
- 5x faster search for 10K vectors
- 13x faster search for 100K vectors
- 30-40% less memory usage
- Production-ready features

**See full guide:** [CHROMADB_TO_QDRANT_MIGRATION.md](CHROMADB_TO_QDRANT_MIGRATION.md)

**Quick reference:** [QDRANT_QUICK_REFERENCE.md](QDRANT_QUICK_REFERENCE.md)

## Backup and Restore 💾

### Creating a Backup

```bash
cd ~/nerdbuntu
./backup_restore.sh backup
```

**What gets backed up:**
- ✅ All processed markdown files
- ✅ Complete ChromaDB vector database
- ✅ Backup metadata and restore instructions

### Restoring from Backup

```bash
./backup_restore.sh restore ~/nerdbuntu/exports/nerdbuntu_backup_*.zip
```

## Documentation 📚

### User Guides
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[BULK_PROCESSING_GUIDE.md](BULK_PROCESSING_GUIDE.md)** - Bulk directory processing
- **[BACKUP_GUIDE.md](BACKUP_GUIDE.md)** - Backup and restore operations
- **[MULTI_DOCUMENT_GUIDE.md](MULTI_DOCUMENT_GUIDE.md)** - Working with multiple documents

### Migration & Advanced Features
- **[CHROMADB_TO_QDRANT_MIGRATION.md](CHROMADB_TO_QDRANT_MIGRATION.md)** - Complete Qdrant migration guide
- **[QDRANT_QUICK_REFERENCE.md](QDRANT_QUICK_REFERENCE.md)** - Quick commands and snippets
- **[QDRANT_MIGRATION_SUMMARY.md](QDRANT_MIGRATION_SUMMARY.md)** - Migration overview

### Technical Documentation
- **[PROCESSING_PIPELINE.md](PROCESSING_PIPELINE.md)** - How processing works
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project organization
- **[TOPIC_SPLITTING_GUIDE.md](TOPIC_SPLITTING_GUIDE.md)** - Advanced chunking

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

### Directory Structure

```
~/nerdbuntu/
├── gui/
│   └── app.py                # GUI application (v2.0 with bulk processing)
├── core/
│   ├── semantic_linker.py    # ChromaDB semantic linker
│   └── semantic_linker_qdrant.py  # Qdrant semantic linker (NEW!)
├── export_to_qdrant.py       # Qdrant export script (NEW!)
├── import_to_qdrant.py       # Qdrant import script (NEW!)
├── setup.sh                  # Setup script
├── backup_restore.sh         # Backup and restore
├── launch_gui.sh             # GUI launcher
├── requirements.txt          # Python dependencies
├── .env                      # Configuration
├── venv/                     # Python virtual environment
├── exports/                  # Backup and export archives
│   └── qdrant/              # Qdrant exports (NEW!)
└── data/
    ├── input/               # Place PDFs here
    ├── output/              # Processed markdown files
    └── vector_db/           # ChromaDB storage
```

## Performance Comparison 📊

### ChromaDB vs Qdrant

| Metric | ChromaDB | Qdrant | Improvement |
|--------|----------|--------|-------------|
| Search (10K vectors) | ~50ms | ~10ms | **5x faster** |
| Search (100K vectors) | ~200ms | ~15ms | **13x faster** |
| Memory Usage | Higher | Lower | **30-40% less** |
| Batch Insert | Slower | Faster | **2-3x faster** |

### Processing Speed (Bulk Mode)

| Mode | Files | Time | Per File |
|------|-------|------|----------|
| Basic (no AI) | 100 | ~30 min | 10-30 sec |
| Semantic (with AI) | 100 | ~3 hours | 1-3 min |
| Basic (no AI) | 500 | ~2.5 hours | 10-30 sec |

## Troubleshooting 🔧

### Common Issues

**Issue**: "No files found" in bulk mode
```bash
# Check pattern syntax
Pattern: *.pdf        # All PDFs
Pattern: report_*.pdf # Files starting with "report_"
```

**Issue**: "All files skipped" in bulk mode
```bash
# Disable "Skip existing files" or delete outputs
rm ~/nerdbuntu/data/output/*.md
```

**Issue**: Bulk processing very slow
```bash
# Disable semantic processing for speed
# Process smaller batches
# Run overnight for large sets
```

**Issue**: Qdrant migration errors
```bash
# Ensure Qdrant is running
docker ps | grep qdrant

# Check Qdrant is accessible
curl http://localhost:6333/
```

See documentation for more troubleshooting tips.

## RAG Integration 🤖

Output markdown files are optimized for RAG systems:

1. **Semantic Chunks**: Pre-chunked for efficient retrieval
2. **Vector Embeddings**: Already computed and stored
3. **Metadata**: Rich context for filtering
4. **Backlinks**: Discover related content
5. **Key Concepts**: Quick topic identification

### Example RAG Pipeline

```python
from core.semantic_linker import SemanticLinker

# Initialize
linker = SemanticLinker(azure_endpoint, azure_api_key)
linker.initialize_vector_db("./data/vector_db")

# Query the vector database
results = linker.find_similar_chunks("How do neural networks work?", n_results=3)

# Use chunks as context for LLM
context = "\n\n".join(results['documents'][0])

# Generate answer with Azure AI
# ... (see full example in documentation)
```

## Contributing 🤝

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License 📄

MIT License - see [LICENSE](LICENSE) file for details

## Support 💬

- **Issues**: [GitHub Issues](https://github.com/Cosmicjedi/nerdbuntu/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Cosmicjedi/nerdbuntu/discussions)
- **Documentation**: See docs listed above

## Acknowledgments 🙏

- [MarkItDown](https://github.com/microsoft/markitdown) by Microsoft
- [Azure AI Services](https://azure.microsoft.com/en-us/products/ai-services)
- [ChromaDB](https://www.trychroma.com/)
- [Qdrant](https://qdrant.tech/)
- [Sentence Transformers](https://www.sbert.net/)

## Roadmap 🗺️

- [x] Export/Import functionality
- [x] Backup and restore system
- [x] Bulk processing UI ✅ **NEW!**
- [x] Qdrant migration support ✅ **NEW!**
- [ ] Web interface (Flask/FastAPI)
- [ ] Additional file formats (DOCX, PPTX)
- [ ] Custom embedding models
- [ ] Advanced RAG features
- [ ] Docker container
- [ ] Cloud deployment guide

---

**Made with ❤️ for the RAG community**
