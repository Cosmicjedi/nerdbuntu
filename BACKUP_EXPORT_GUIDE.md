# Backup and Export Guide

## 📦 Two Separate Backup Scripts

Now there are TWO scripts for different purposes:

### 1. `backup_vector_db.sh` - For RAG/LLM Use
Backs up ONLY the vector database (ChromaDB).

**Use this when:**
- You want to move data to your LLM environment
- You need the semantic search capability
- You're building a RAG system

### 2. `backup_markdown.sh` - For Human-Readable Archives  
Backs up ONLY the markdown files.

**Use this when:**
- You want to archive the converted documents
- You need human-readable files
- You're moving to a note-taking app
- You want to back up your documentation

## 🚀 Quick Start

### Vector Database Export (for LLM)

```bash
# Make executable
chmod +x backup_vector_db.sh

# Export for LLM environment
./backup_vector_db.sh export

# This creates:
# - vector_db_export_TIMESTAMP.tar.gz (the database)
# - vector_db_export_TIMESTAMP_README.txt (instructions)
```

### Markdown Files Export (for archiving)

```bash
# Make executable  
chmod +x backup_markdown.sh

# Export markdown files
./backup_markdown.sh export

# This creates:
# - markdown_export_TIMESTAMP.tar.gz (all .md files)
```

## 📋 Vector Database Script

**backup_vector_db.sh** - For moving vector data to LLM environments

### Commands

```bash
# Create backup
./backup_vector_db.sh backup

# Export for LLM (creates README)
./backup_vector_db.sh export [filename]

# List available backups
./backup_vector_db.sh list

# Restore from backup
./backup_vector_db.sh restore <backup_file>
```

### Example: Moving to LLM Environment

```bash
# 1. Export the vector database
./backup_vector_db.sh export my_rag_data.tar.gz

# 2. Transfer files to LLM server
scp my_rag_data.tar.gz user@llm-server:/path/

# 3. On LLM server, extract
tar -xzf my_rag_data.tar.gz

# 4. Use in your RAG system
python3 << EOF
import chromadb
client = chromadb.PersistentClient(path="./vector_db")
collection = client.get_collection("markdown_chunks")

# Query your data
results = collection.query(
    query_texts=["your search query"],
    n_results=5
)
EOF
```

## 📄 Markdown Files Script

**backup_markdown.sh** - For archiving converted documents

### Commands

```bash
# Create backup
./backup_markdown.sh backup

# Export markdown files
./backup_markdown.sh export [filename]
```

### Example: Archiving Documents

```bash
# Export all markdown files
./backup_markdown.sh export my_documents.tar.gz

# Extract later
tar -xzf my_documents.tar.gz

# You now have an output/ folder with all .md files
```

## 🎯 Why Split Them?

### Vector Database (ChromaDB)
- **What**: Binary database files with embeddings
- **Size**: Larger (includes all vector data)
- **Use**: RAG systems, semantic search, LLM applications
- **Speed**: Fast to query, requires ChromaDB
- **Format**: Binary (not human-readable)

### Markdown Files
- **What**: Text files with converted PDF content
- **Size**: Smaller (just text)
- **Use**: Reading, archiving, documentation, note-taking
- **Speed**: Instant to read, no special software
- **Format**: Plain text (human-readable)

## 📊 Typical Workflow

### For RAG/LLM Development:

```bash
# 1. Process PDFs with semantic features
python3 multi_document_demo.py process *.pdf

# 2. Export ONLY the vector database
./backup_vector_db.sh export

# 3. Move to LLM environment
# (You don't need the markdown files!)
```

### For Documentation Archive:

```bash
# 1. Process PDFs (basic or semantic mode)
python3 multi_document_demo.py process *.pdf

# 2. Export ONLY the markdown files
./backup_markdown.sh export

# 3. Store or share the readable docs
# (You don't need the vector database!)
```

### For Complete Backup (both):

```bash
# 1. Backup vector database
./backup_vector_db.sh backup

# 2. Backup markdown files
./backup_markdown.sh backup

# Both stored separately in:
# ~/nerdbuntu/backups/vector_db/
# ~/nerdbuntu/backups/markdown/
```

## 🔄 Restore Examples

### Restore Vector Database

```bash
# List available backups
./backup_vector_db.sh list

# Restore a specific backup
./backup_vector_db.sh restore ~/nerdbuntu/backups/vector_db/vector_db_backup_20250106_143022.tar.gz
```

### Use in Different Locations

```bash
# Custom vector database location
VECTOR_DB_DIR=/custom/path/vector_db ./backup_vector_db.sh export

# Custom markdown location
MARKDOWN_DIR=/custom/path/output ./backup_markdown.sh export
```

## 📦 What Gets Created

### Vector Database Export:
```
vector_db_export_20250106_143022.tar.gz    ← The database
vector_db_export_20250106_143022_README.txt ← Instructions
```

### Markdown Export:
```
markdown_export_20250106_143022.tar.gz  ← The markdown files
```

## 💡 Best Practices

### For LLM/RAG Systems:
1. ✅ Export vector database only
2. ✅ Keep it updated as you add documents
3. ✅ No need for markdown files in production
4. ✅ Smaller transfer size

### For Documentation:
1. ✅ Export markdown files only
2. ✅ Human-readable format
3. ✅ Easy to search and read
4. ✅ Import into any note-taking app

### For Complete Backup:
1. ✅ Backup both separately
2. ✅ Vector DB for restoring search capability
3. ✅ Markdown for human access to content
4. ✅ Store in different locations for redundancy

## 🎯 Summary

| Need | Script | Export | Size | Format |
|------|--------|--------|------|--------|
| RAG/LLM | backup_vector_db.sh | Vector DB | Larger | Binary |
| Reading | backup_markdown.sh | Markdown | Smaller | Text |
| Both | Both scripts | Both | Largest | Mixed |

**Choose the right tool for your needs!** 🎉
