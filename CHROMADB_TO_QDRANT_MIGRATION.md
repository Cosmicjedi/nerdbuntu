# ChromaDB to Qdrant Migration Guide

Complete guide for migrating your Nerdbuntu vector database from ChromaDB to Qdrant.

## 📋 Overview

This guide covers:
- Why migrate to Qdrant
- Backing up your ChromaDB data
- Exporting data in Qdrant-compatible format
- Importing to Qdrant
- Updating your application
- Verification and testing

## 🎯 Why Migrate to Qdrant?

### Qdrant Advantages

**Performance**
- Faster similarity search for large datasets (1M+ vectors)
- Better memory management
- Optimized for production workloads

**Scalability**
- Horizontal scaling support
- Distributed deployment options
- Cloud-native architecture

**Features**
- Built-in filtering and payload indexing
- Snapshot and backup management
- REST API and gRPC support
- Web UI for management

**Production Ready**
- Better monitoring and observability
- Enterprise support available
- Active development and community

### When to Migrate

✅ **Migrate if you:**
- Have large datasets (100K+ vectors)
- Need production-grade performance
- Want cloud deployment options
- Need advanced filtering capabilities
- Require better scaling

⚠️ **Stay with ChromaDB if you:**
- Have small datasets (<10K vectors)
- Running only local experiments
- Don't need production features
- Satisfied with current performance

## 🔧 Prerequisites

### Install Required Tools

```bash
# On your source machine (with ChromaDB)
pip install chromadb sentence-transformers

# On your destination machine (for Qdrant)
pip install qdrant-client sentence-transformers
```

### Set Up Qdrant

Choose one of these options:

#### Option 1: Docker (Recommended for Testing)

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

#### Option 2: Docker Compose (Recommended for Production)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage:z
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped
```

```bash
docker-compose up -d
```

#### Option 3: Qdrant Cloud

Sign up at https://cloud.qdrant.io and create a cluster.

#### Option 4: Manual Installation

```bash
# Download latest release
wget https://github.com/qdrant/qdrant/releases/latest/download/qdrant

# Make executable
chmod +x qdrant

# Run
./qdrant
```

### Verify Qdrant is Running

```bash
curl http://localhost:6333/
# Should return Qdrant version info
```

Or visit http://localhost:6333/dashboard for the web UI.

## 📦 Step 1: Backup Your ChromaDB Data

Before migration, create a backup of your existing ChromaDB:

```bash
cd ~/nerdbuntu

# Backup vector database
./backup_vector_db.sh backup

# This creates a timestamped backup in ~/nerdbuntu/backups/vector_db/
```

**Important**: Keep this backup until you've verified the Qdrant migration!

## 📤 Step 2: Export ChromaDB Data

Run the export script to create Qdrant-compatible files:

```bash
cd ~/nerdbuntu

# Export all collections
python export_to_qdrant.py
```

This creates:
- `exports/qdrant/TIMESTAMP/` directory
- JSON files (human-readable, easier to debug)
- Pickle files (binary, faster for large datasets)
- Import guide and statistics

### Export Output Example

```
📂 Export directory: /home/user/nerdbuntu/exports/qdrant/20231215_143022/

Files created:
├── markdown_chunks_export_20231215_143022.json     # JSON format
├── markdown_chunks_export_20231215_143022.pkl      # Binary format (faster)
├── markdown_chunks_export_20231215_143022_stats.json
└── QDRANT_IMPORT_GUIDE_20231215_143022.md
```

### Understanding Export Files

**JSON Format** (`*.json`)
- Human-readable
- Easier to debug
- Larger file size
- Use for: Small datasets (<10K vectors)

**Pickle Format** (`*.pkl`)
- Binary format
- Much faster to load
- Smaller file size
- Use for: Large datasets (10K+ vectors)

**Stats File** (`*_stats.json`)
- Export metadata
- File sizes
- Vector counts

**Import Guide** (`QDRANT_IMPORT_GUIDE_*.md`)
- Auto-generated instructions
- Specific to your export
- Example code

## 📥 Step 3: Import to Qdrant

### Basic Import

```bash
# Using JSON file (smaller datasets)
python import_to_qdrant.py \
    --json-file exports/qdrant/TIMESTAMP/markdown_chunks_export_TIMESTAMP.json

# Using pickle file (faster for large datasets)
python import_to_qdrant.py \
    --json-file exports/qdrant/TIMESTAMP/markdown_chunks_export_TIMESTAMP.pkl
```

### Advanced Import Options

```bash
# Custom Qdrant URL
python import_to_qdrant.py \
    --json-file export.json \
    --url http://your-qdrant-server:6333

# Qdrant Cloud
python import_to_qdrant.py \
    --json-file export.json \
    --url https://xyz-example.qdrant.io:6333 \
    --api-key your-api-key-here

# Custom collection name
python import_to_qdrant.py \
    --json-file export.json \
    --collection my_custom_name

# Larger batch size (faster for good network)
python import_to_qdrant.py \
    --json-file export.json \
    --batch-size 1000

# Skip verification (faster, but not recommended)
python import_to_qdrant.py \
    --json-file export.json \
    --skip-verify \
    --skip-test
```

### Import Progress

The script shows:
- Connection status
- Export file validation
- Collection creation
- Batch upload progress
- Verification results
- Test search results

## 🔍 Step 4: Verify the Migration

### Automatic Verification

The import script automatically verifies:
- Vector count matches
- Test search works
- Collection is accessible

### Manual Verification

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

# Check collection info
info = client.get_collection("markdown_chunks")
print(f"Vectors: {info.vectors_count}")
print(f"Config: {info.config}")

# Count should match your export
```

### Compare Search Results

Test the same query on both databases:

**ChromaDB:**
```python
import chromadb

client = chromadb.PersistentClient(path="./data/vector_db")
collection = client.get_collection("markdown_chunks")

results = collection.query(
    query_texts=["machine learning"],
    n_results=5
)
print("ChromaDB Results:", results['documents'][0][:100])
```

**Qdrant:**
```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(url="http://localhost:6333")
model = SentenceTransformer('all-MiniLM-L6-v2')

query_vector = model.encode("machine learning").tolist()
results = client.search(
    collection_name="markdown_chunks",
    query_vector=query_vector,
    limit=5
)

for r in results:
    print("Qdrant Result:", r.payload['document'][:100])
```

Results should be similar (order may vary slightly due to different distance calculations).

## 🔄 Step 5: Update Your Application

### Update semantic_linker.py

Replace ChromaDB initialization with Qdrant:

**Before (ChromaDB):**
```python
import chromadb

self.chroma_client = chromadb.PersistentClient(path=db_path)
self.collection = self.chroma_client.get_or_create_collection(
    name="markdown_chunks",
    metadata={"hnsw:space": "cosine"}
)
```

**After (Qdrant):**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

self.qdrant_client = QdrantClient(url="http://localhost:6333")

# Create collection if it doesn't exist
try:
    self.qdrant_client.get_collection("markdown_chunks")
except:
    self.qdrant_client.create_collection(
        collection_name="markdown_chunks",
        vectors_config=VectorParams(
            size=384,  # all-MiniLM-L6-v2 dimension
            distance=Distance.COSINE
        )
    )

self.collection_name = "markdown_chunks"
```

### Update add operations

**Before (ChromaDB):**
```python
self.collection.add(
    ids=ids,
    embeddings=embeddings.tolist(),
    documents=chunks,
    metadatas=[{"source": filename, "chunk_id": i} for i in range(len(chunks))]
)
```

**After (Qdrant):**
```python
from qdrant_client.models import PointStruct

points = []
for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    point = PointStruct(
        id=ids[i],
        vector=embedding.tolist(),
        payload={
            "document": chunk,
            "metadata": {
                "source": filename,
                "chunk_id": i
            }
        }
    )
    points.append(point)

self.qdrant_client.upsert(
    collection_name=self.collection_name,
    points=points
)
```

### Update search operations

**Before (ChromaDB):**
```python
query_embedding = self.embedding_model.encode([query_text])[0]
results = self.collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=n_results
)
```

**After (Qdrant):**
```python
query_embedding = self.embedding_model.encode(query_text).tolist()
results = self.qdrant_client.search(
    collection_name=self.collection_name,
    query_vector=query_embedding,
    limit=n_results
)

# Convert to similar format as ChromaDB
formatted_results = {
    'ids': [[r.id for r in results]],
    'documents': [[r.payload['document'] for r in results]],
    'metadatas': [[r.payload.get('metadata', {}) for r in results]],
    'distances': [[r.score for r in results]]
}
```

### Create a Qdrant-compatible semantic_linker.py

See the updated version in the repository: `core/semantic_linker_qdrant.py`

## 🧪 Step 6: Testing

### Test Basic Operations

```python
from core.semantic_linker_qdrant import SemanticLinkerQdrant

# Initialize
linker = SemanticLinkerQdrant(
    azure_endpoint="your-endpoint",
    azure_api_key="your-key",
    qdrant_url="http://localhost:6333"
)

# Test search
results = linker.find_similar_chunks("machine learning", n_results=5)
print(f"Found {len(results)} results")

# Test adding new documents
test_text = "This is a test document"
linker.add_semantic_links(test_text, "test.md")
```

### Performance Testing

```python
import time
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Test search speed
queries = [
    "machine learning algorithms",
    "data preprocessing techniques",
    "neural network architectures",
    "model evaluation metrics",
    "feature engineering methods"
]

start = time.time()
for query in queries:
    vector = model.encode(query).tolist()
    results = client.search(
        collection_name="markdown_chunks",
        query_vector=vector,
        limit=10
    )
end = time.time()

print(f"Average query time: {(end-start)/len(queries):.3f}s")
```

## 📊 Performance Comparison

### Expected Improvements

| Metric | ChromaDB | Qdrant | Improvement |
|--------|----------|--------|-------------|
| Search Speed (10K vectors) | ~50ms | ~10ms | 5x faster |
| Search Speed (100K vectors) | ~200ms | ~15ms | 13x faster |
| Memory Usage | Higher | Lower | 30-40% less |
| Batch Insert | Slower | Faster | 2-3x faster |
| Concurrent Queries | Limited | Good | Better |

*Note: Actual performance depends on hardware, dataset, and configuration*

## 🔒 Step 7: Backup and Cleanup

### Backup Qdrant

```bash
# Using Qdrant's snapshot feature
curl -X POST 'http://localhost:6333/collections/markdown_chunks/snapshots'

# List snapshots
curl 'http://localhost:6333/collections/markdown_chunks/snapshots'

# Download snapshot
curl 'http://localhost:6333/collections/markdown_chunks/snapshots/{snapshot-name}' \
    --output snapshot.snapshot
```

### Keep ChromaDB Backup

**Do NOT delete ChromaDB immediately!**

Keep it for at least 2-4 weeks until you're confident in the Qdrant migration.

### Archive Export Files

```bash
# Move export to long-term storage
mv ~/nerdbuntu/exports/qdrant ~/backups/chromadb_to_qdrant_migration_$(date +%Y%m%d)

# Or upload to cloud storage
# aws s3 cp ~/nerdbuntu/exports/qdrant s3://your-bucket/migrations/ --recursive
```

## 🚨 Troubleshooting

### Common Issues

#### Issue: "Collection already exists"

```python
# Delete and recreate
client.delete_collection("markdown_chunks")
# Then re-run import script
```

#### Issue: "Vector dimension mismatch"

**Cause**: Using different embedding model

**Solution**: Ensure you use `all-MiniLM-L6-v2` (384 dimensions)

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print(f"Dimension: {model.get_sentence_embedding_dimension()}")  # Should be 384
```

#### Issue: "Out of memory during import"

**Solutions:**
1. Reduce batch size: `--batch-size 100`
2. Increase Qdrant memory limits in docker-compose
3. Import in multiple sessions

#### Issue: "Connection refused"

**Check:**
```bash
# Is Qdrant running?
docker ps | grep qdrant

# Can you reach it?
curl http://localhost:6333/

# Check logs
docker logs qdrant
```

#### Issue: "Search results different from ChromaDB"

**Normal!** Slight differences expected due to:
- Different distance calculation implementations
- Different index structures
- Floating point precision

**Verify:**
- Top results should be similar
- Scores should be in same range
- No completely wrong results

## 📚 Additional Resources

### Qdrant Documentation
- Official Docs: https://qdrant.tech/documentation/
- API Reference: https://qdrant.tech/documentation/api-reference/
- Examples: https://github.com/qdrant/qdrant-client

### Tutorials
- [Getting Started with Qdrant](https://qdrant.tech/documentation/quick-start/)
- [Collections and Indexing](https://qdrant.tech/documentation/concepts/collections/)
- [Search and Filtering](https://qdrant.tech/documentation/concepts/search/)

### Community
- Discord: https://discord.gg/qdrant
- GitHub: https://github.com/qdrant/qdrant
- Forum: https://github.com/qdrant/qdrant/discussions

## ✅ Migration Checklist

Use this checklist to track your migration:

- [ ] Backed up ChromaDB data
- [ ] Installed Qdrant
- [ ] Verified Qdrant is running
- [ ] Ran export script successfully
- [ ] Reviewed export files
- [ ] Ran import script successfully
- [ ] Verified vector counts match
- [ ] Tested search functionality
- [ ] Updated application code
- [ ] Tested application with Qdrant
- [ ] Performance tested
- [ ] Created Qdrant backups
- [ ] Documented changes
- [ ] Monitored for 1-2 weeks
- [ ] Archived ChromaDB backup

## 🎉 Success!

You've successfully migrated from ChromaDB to Qdrant!

### Next Steps

1. **Monitor Performance**: Track search times and accuracy
2. **Optimize**: Tune Qdrant configuration for your workload
3. **Scale**: Consider distributed setup for very large datasets
4. **Backup**: Set up regular Qdrant snapshot schedules

### Questions or Issues?

- GitHub Issues: https://github.com/Cosmicjedi/nerdbuntu/issues
- Include: Error messages, logs, system info
- Mark with `qdrant-migration` label

---

**Last Updated**: October 2025
**Script Version**: 1.0
**Qdrant Version**: 1.6.x+
