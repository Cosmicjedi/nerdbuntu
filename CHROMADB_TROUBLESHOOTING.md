# ChromaDB Troubleshooting Guide

## Problem: Migration GUI Can't Find Data

If the migration GUI isn't finding any data in ChromaDB, use this guide to diagnose the issue.

## Step 1: Run the Diagnostic Script

```bash
# Auto-detect ChromaDB location
python3 check_chromadb.py

# Or specify the path manually
python3 check_chromadb.py /path/to/vector_db
```

### What the Script Checks

1. ✅ ChromaDB library is installed
2. 📂 ChromaDB directory exists
3. 🔗 Can connect to ChromaDB
4. 📊 Lists all collections
5. 📈 Shows item counts
6. 📝 Displays sample data

## Step 2: Interpret Results

### Case 1: "NO COLLECTIONS FOUND"

**Problem**: ChromaDB is empty - no data has been added yet.

**Solutions**:

```bash
# Option A: Process documents via GUI
./launch_gui.sh

# Option B: Batch process documents
python3 examples.py batch data/input data/output

# Option C: Process a single file
python3 examples.py process /path/to/document.pdf
```

### Case 2: "Collections exist but contain no data"

**Problem**: Collections were created but no vectors were added.

**This can happen if**:
- Documents failed to process
- Embeddings weren't generated
- Azure AI errors occurred

**Solution**: Re-process your documents with verbose logging.

### Case 3: "Path does not exist"

**Problem**: Wrong ChromaDB path.

**Common locations**:
- `~/nerdbuntu/data/vector_db` (default)
- `./data/vector_db` (relative to repo)
- Check your `.env` file for `VECTOR_DB_DIR`

**Solution**: Find the correct path:

```bash
# Check .env file
cat ~/.env | grep VECTOR_DB_DIR

# Or search for ChromaDB files
find ~ -name "chroma.sqlite3" -type f 2>/dev/null
```

### Case 4: Multiple ChromaDB Locations

**Problem**: You have ChromaDB data in multiple places.

**Solution**: Determine which one to use:

```bash
# Check all possible locations
python3 check_chromadb.py ~/nerdbuntu/data/vector_db
python3 check_chromadb.py ./data/vector_db
python3 check_chromadb.py /var/lib/chromadb
```

## Step 3: Verify Data Before Migration

Once you've found your ChromaDB with data:

```bash
# Run diagnostic to confirm
python3 check_chromadb.py

# Expected output:
# ✅ Connected to ChromaDB successfully
# 📊 Found X collection(s)
# 📈 Total items: XXX
# ✅ ChromaDB contains data and is ready for migration!
```

## Step 4: Update Migration GUI Path

If your ChromaDB is in a non-standard location:

### Option A: Update via GUI
1. Run `./launch_migration_gui.sh`
2. Go to "Export (Server 1)" tab
3. Click "Browse" next to "ChromaDB Path"
4. Select your ChromaDB directory

### Option B: Update config file
```bash
# Edit the config
nano ~/.nerdbuntu_migration_config.json

# Update this line:
"chromadb_path": "/your/actual/path/to/vector_db"
```

## Common ChromaDB Locations by Setup

### Default nerdbuntu setup:
```
~/nerdbuntu/data/vector_db/
```

### If running from repo directory:
```
./data/vector_db/
```

### Docker installations:
```
/var/lib/chromadb/
/opt/chromadb/data/
```

### Custom installations:
Check your `.env` file or environment variables.

## Manually Connecting to ChromaDB (Python)

If you want to check ChromaDB manually:

```python
import chromadb

# Connect to your ChromaDB
client = chromadb.PersistentClient(path="/path/to/vector_db")

# List collections
collections = client.list_collections()
print(f"Collections: {[c.name for c in collections]}")

# Check a collection
if collections:
    col = client.get_collection(collections[0].name)
    print(f"Items in {collections[0].name}: {col.count()}")
    
    # Get sample
    sample = col.get(limit=1, include=['documents', 'metadatas'])
    print(f"Sample: {sample}")
```

## Still Having Issues?

### Check ChromaDB Files

ChromaDB stores data in SQLite files:

```bash
# Look for ChromaDB files
ls -lah ~/nerdbuntu/data/vector_db/

# Should see files like:
# chroma.sqlite3
# *.parquet files (in subdirectories)
```

If these files don't exist, ChromaDB is truly empty.

### Check Processing Logs

Review logs from when you processed documents:

```bash
# If using the GUI, check for errors in terminal output
# If using batch processing:
python3 examples.py batch data/input data/output --verbose
```

### Verify ChromaDB Version

```bash
pip show chromadb

# Check if it's compatible
# Recommended: chromadb >= 0.4.0
```

## Quick Diagnostic Command Summary

```bash
# 1. Check ChromaDB exists and has data
python3 check_chromadb.py

# 2. If empty, process some documents
python3 examples.py batch data/input data/output

# 3. Verify data was added
python3 check_chromadb.py

# 4. Run migration
./launch_migration_gui.sh
```

## Emergency: Finding All ChromaDB Databases

```bash
# Search entire home directory for ChromaDB files
find ~ -name "chroma.sqlite3" -type f 2>/dev/null

# Search system-wide (may require sudo)
sudo find / -name "chroma.sqlite3" -type f 2>/dev/null
```

Each `chroma.sqlite3` file indicates a ChromaDB instance. Use the diagnostic script to check each one.
