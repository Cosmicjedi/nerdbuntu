# Qdrant Migration Quick Reference

Quick commands and code snippets for migrating from ChromaDB to Qdrant.

## 🚀 Quick Start

### 1. Export ChromaDB Data (Source Machine)

```bash
cd ~/nerdbuntu
python export_to_qdrant.py
```

Output location: `~/nerdbuntu/exports/qdrant/TIMESTAMP/`

### 2. Setup Qdrant (Destination Machine)

```bash
# Using Docker (easiest)
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant

# Verify it's running
curl http://localhost:6333/
```

### 3. Import to Qdrant

```bash
cd ~/nerdbuntu

# Import JSON export
python import_to_qdrant.py \
    --json-file exports/qdrant/TIMESTAMP/markdown_chunks_export_TIMESTAMP.json

# Or import pickle (faster for large datasets)
python import_to_qdrant.py \
    --json-file exports/qdrant/TIMESTAMP/markdown_chunks_export_TIMESTAMP.pkl
```

## 📋 Command Reference

### Export Commands

```bash
# Basic export (exports all collections)
python export_to_qdrant.py

# The script automatically:
# - Connects to ChromaDB at ~/nerdbuntu/data/vector_db
# - Exports all collections
# - Creates JSON and pickle files
# - Generates import guide
# - Shows statistics
```

### Import Commands

```bash
# Basic import to local Qdrant
python import_to_qdrant.py --json-file <file.json>

# Import to remote Qdrant
python import_to_qdrant.py \
    --json-file <file.json> \
    --url http://your-server:6333

# Import to Qdrant Cloud
python import_to_qdrant.py \
    --json-file <file.json> \
    --url https://xyz.qdrant.io:6333 \
    --api-key your-api-key

# Custom collection name
python import_to_qdrant.py \
    --json-file <file.json> \
    --collection my_collection

# Faster import with larger batches
python import_to_qdrant.py \
    --json-file <file.json> \
    --batch-size 1000

# Skip verification (not recommended)
python import_to_qdrant.py \
    --json-file <file.json> \
    --skip-verify --skip-test
```

## 🐍 Code Snippets

### Initialize Qdrant Client

```python
from qdrant_client import QdrantClient

# Local Qdrant
client = QdrantClient(url="http://localhost:6333")

# Remote Qdrant
client = QdrantClient(url="http://your-server:6333")

# Qdrant Cloud
client = QdrantClient(
    url="https://xyz.qdrant.io:6333",
    api_key="your-api-key"
)
```

### Create Collection

```python
from qdrant_client.models import Distance, VectorParams

client.create_collection(
    collection_name="markdown_chunks",
    vectors_config=VectorParams(
        size=384,  # for all-MiniLM-L6-v2
        distance=Distance.COSINE
    )
)
```

### Add Vectors

```python
from qdrant_client.models import PointStruct

points = []
for i, (text, vector) in enumerate(zip(texts, vectors)):
    point = PointStruct(
        id=f"doc_{i}",
        vector=vector.tolist(),
        payload={"text": text, "metadata": {...}}
    )
    points.append(point)

client.upsert(
    collection_name="markdown_chunks",
    points=points
)
```

### Search

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query_vector = model.encode("your query").tolist()

results = client.search(
    collection_name="markdown_chunks",
    query_vector=query_vector,
    limit=5
)

for result in results:
    print(f"Score: {result.score}")
    print(f"Text: {result.payload['text']}")
```

### Get Collection Info

```python
info = client.get_collection("markdown_chunks")
print(f"Vectors: {info.vectors_count}")
print(f"Points: {info.points_count}")
print(f"Status: {info.status}")
```

### Delete Points

```python
# Delete by ID
client.delete(
    collection_name="markdown_chunks",
    points_selector=["doc_1", "doc_2"]
)

# Delete by filter
from qdrant_client.models import Filter, FieldCondition, MatchValue

client.delete(
    collection_name="markdown_chunks",
    points_selector=Filter(
        must=[
            FieldCondition(
                key="metadata.source",
                match=MatchValue(value="document.pdf")
            )
        ]
    )
)
```

## 🔍 Verification Snippets

### Compare Vector Counts

```python
# ChromaDB
import chromadb
chroma_client = chromadb.PersistentClient(path="./data/vector_db")
chroma_collection = chroma_client.get_collection("markdown_chunks")
chroma_count = chroma_collection.count()
print(f"ChromaDB: {chroma_count}")

# Qdrant
from qdrant_client import QdrantClient
qdrant_client = QdrantClient(url="http://localhost:6333")
qdrant_info = qdrant_client.get_collection("markdown_chunks")
qdrant_count = qdrant_info.vectors_count
print(f"Qdrant: {qdrant_count}")

# Should match
assert chroma_count == qdrant_count, "Count mismatch!"
```

### Test Search Results

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query = "machine learning"

# ChromaDB search
chroma_results = chroma_collection.query(
    query_texts=[query],
    n_results=5
)

# Qdrant search
query_vector = model.encode(query).tolist()
qdrant_results = qdrant_client.search(
    collection_name="markdown_chunks",
    query_vector=query_vector,
    limit=5
)

# Compare top results
print("ChromaDB Top Result:", chroma_results['documents'][0][0][:100])
print("Qdrant Top Result:", qdrant_results[0].payload['document'][:100])
```

## 🐳 Docker Commands

### Start Qdrant

```bash
# Simple start
docker run -d -p 6333:6333 qdrant/qdrant

# With persistent storage
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant

# With custom config
docker run -d -p 6333:6333 \
    -v $(pwd)/qdrant_config.yaml:/qdrant/config/production.yaml \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

### Docker Compose

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
    restart: unless-stopped
```

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f qdrant
```

### Docker Management

```bash
# Check if running
docker ps | grep qdrant

# View logs
docker logs qdrant

# Restart
docker restart qdrant

# Stop
docker stop qdrant

# Remove
docker rm qdrant
```

## 📊 Monitoring

### Check Qdrant Status

```bash
# Health check
curl http://localhost:6333/

# Metrics
curl http://localhost:6333/metrics

# Collections list
curl http://localhost:6333/collections
```

### Get Collection Stats

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
info = client.get_collection("markdown_chunks")

print(f"Vectors: {info.vectors_count}")
print(f"Indexed: {info.indexed_vectors_count}")
print(f"Points: {info.points_count}")
print(f"Segments: {info.segments_count}")
print(f"Status: {info.status}")
```

### Performance Testing

```python
import time
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
model = SentenceTransformer('all-MiniLM-L6-v2')

queries = ["test query 1", "test query 2", "test query 3"]
times = []

for query in queries:
    vector = model.encode(query).tolist()
    start = time.time()
    results = client.search(
        collection_name="markdown_chunks",
        query_vector=vector,
        limit=10
    )
    elapsed = time.time() - start
    times.append(elapsed)

avg_time = sum(times) / len(times)
print(f"Average query time: {avg_time*1000:.2f}ms")
```

## 💾 Backup Commands

### Create Snapshot

```bash
# Create snapshot via API
curl -X POST 'http://localhost:6333/collections/markdown_chunks/snapshots'

# List snapshots
curl 'http://localhost:6333/collections/markdown_chunks/snapshots'

# Download snapshot
curl 'http://localhost:6333/collections/markdown_chunks/snapshots/snapshot-name' \
    --output backup.snapshot
```

### Restore Snapshot

```bash
# Upload and restore
curl -X PUT 'http://localhost:6333/collections/markdown_chunks/snapshots/upload' \
    -H 'Content-Type: multipart/form-data' \
    -F 'snapshot=@backup.snapshot'
```

## 🔧 Troubleshooting Commands

### Reset Collection

```python
# Delete and recreate
client.delete_collection("markdown_chunks")
client.create_collection(
    collection_name="markdown_chunks",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
```

### Check Qdrant Logs

```bash
# Docker logs
docker logs qdrant

# Follow logs
docker logs -f qdrant

# Last 100 lines
docker logs --tail 100 qdrant
```

### Test Connection

```python
from qdrant_client import QdrantClient

try:
    client = QdrantClient(url="http://localhost:6333")
    collections = client.get_collections()
    print(f"✅ Connected! Found {len(collections.collections)} collections")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## 📚 Common Issues & Solutions

### Issue: Port already in use

```bash
# Find process using port 6333
lsof -i :6333
# or
netstat -tulpn | grep 6333

# Kill the process
kill -9 <PID>
```

### Issue: Permission denied (volumes)

```bash
# Fix permissions
chmod 777 qdrant_storage/

# Or use SELinux context (if applicable)
chcon -Rt svirt_sandbox_file_t qdrant_storage/
```

### Issue: Out of memory

```yaml
# In docker-compose.yml, add memory limits
services:
  qdrant:
    image: qdrant/qdrant:latest
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

## 📖 Further Reading

- Full Migration Guide: `CHROMADB_TO_QDRANT_MIGRATION.md`
- Qdrant Docs: https://qdrant.tech/documentation/
- Export Script: `export_to_qdrant.py`
- Import Script: `import_to_qdrant.py`
- Qdrant Semantic Linker: `core/semantic_linker_qdrant.py`

---

**Version**: 1.0  
**Last Updated**: October 2025
