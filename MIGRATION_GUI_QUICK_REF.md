# Migration GUI Quick Reference

Quick reference card for the ChromaDB to Qdrant Migration GUI.

## Launch

```bash
cd ~/nerdbuntu
chmod +x launch_migration_gui.sh
./launch_migration_gui.sh
```

Or:
```bash
python3 launch_migration_gui.py
```

## Tab Overview

| Tab | Purpose | Key Actions |
|-----|---------|-------------|
| **1. Backup from ChromaDB** | Export your ChromaDB data | Configure paths, select formats, start export |
| **2. Restore to Qdrant** | Import data into Qdrant | Select file, configure Qdrant, test connection, start import |
| **⚙️ Configuration** | View system info and settings | Check installed packages, review paths |
| **📜 History** | View past operations | Review export/import history, timestamps |

## Common Workflows

### First Time Migration

1. **Tab 1: Backup**
   - Set ChromaDB path (default: `~/nerdbuntu/data/vector_db`)
   - Set export directory (default: `~/nerdbuntu/exports/qdrant`)
   - ✅ Check both JSON and Pickle
   - Click "🚀 Start Export"
   - Wait for completion

2. **Setup Qdrant** (in terminal)
   ```bash
   docker run -d -p 6333:6333 qdrant/qdrant
   ```

3. **Tab 2: Restore**
   - Browse and select your `.pkl` or `.json` file
   - Qdrant URL: `http://localhost:6333`
   - Click "Test Connection"
   - ✅ Verify import
   - ✅ Run test search
   - Click "🚀 Start Import"
   - Wait for completion

### Export Only (Backup)

1. **Tab 1: Backup**
   - Configure paths
   - Click "🚀 Start Export"
   - Files saved to: `~/nerdbuntu/exports/qdrant/TIMESTAMP/`

### Import from Existing Export

1. **Tab 2: Restore**
   - Click "Browse" → Select export file
   - Configure Qdrant connection
   - Click "Test Connection"
   - Click "🚀 Start Import"

## Key Settings

### Export Options

| Option | Description | When to Use |
|--------|-------------|-------------|
| **Export as JSON** | Human-readable format | Small datasets (<10K), debugging |
| **Export as Pickle** | Binary format, faster | Large datasets (10K+), production |

### Import Options

| Option | Description | Recommended |
|--------|-------------|-------------|
| **Collection Name** | Override default name | When avoiding conflicts |
| **Batch Size** | Vectors per upload | 500 (default), 100-200 for slow networks |
| **Verify import** | Check vector counts | ✅ Always enabled |
| **Run test search** | Test functionality | ✅ Always enabled |

## Connection Settings

### Local Qdrant (Docker)
```
URL: http://localhost:6333
API Key: (leave empty)
```

### Qdrant Cloud
```
URL: https://your-cluster.qdrant.io:6333
API Key: (your API key)
```

## Typical Export Sizes

| Vectors | JSON Size | Pickle Size | Export Time |
|---------|-----------|-------------|-------------|
| 1K | ~5 MB | ~2 MB | 10-20 sec |
| 10K | ~50 MB | ~20 MB | 1-2 min |
| 100K | ~500 MB | ~200 MB | 10-15 min |
| 1M | ~5 GB | ~2 GB | 1-2 hours |

## Typical Import Times

| Vectors | Batch 500 | Batch 1000 | Notes |
|---------|-----------|------------|-------|
| 1K | 30 sec | 20 sec | Network matters little |
| 10K | 3 min | 2 min | Network starts to matter |
| 100K | 25 min | 15 min | Good network helps |
| 1M | 3-4 hours | 2-3 hours | Local Qdrant recommended |

## Status Messages

### Success Messages ✅
- `✅ Connected successfully! Found X collection(s)` - Qdrant connection OK
- `✅ Loaded JSON/pickle file` - Export file loaded
- `✅ Collection created` - New collection ready
- `✅ Import complete!` - All vectors imported
- `✅ Verification successful! Counts match.` - Import verified
- `✅ Search successful!` - Test search works

### Warning Messages ⚠️
- `⚠️ Collection 'X' already exists` - Need to delete or rename
- `⚠️ Warning: Count mismatch!` - Some vectors may be missing
- `⚠️ Skipping item X: no vector` - Some items had no embeddings

### Error Messages ❌
- `❌ ChromaDB not found at: X` - Wrong path or no data
- `❌ Failed to connect to Qdrant: X` - Qdrant not running or wrong URL
- `❌ File not found: X` - Export file path incorrect
- `❌ Error during import: X` - Check logs for details

## Troubleshooting Quick Fixes

### GUI Won't Start
```bash
# Install tkinter
sudo apt-get install python3-tk

# Or use CLI tools
python export_to_qdrant.py
python import_to_qdrant.py --help
```

### Export Shows "No Collections"
```bash
# Check ChromaDB has data
ls ~/nerdbuntu/data/vector_db/

# Process some PDFs first
./launch_gui.sh
```

### Can't Connect to Qdrant
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Start Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# Test manually
curl http://localhost:6333/
```

### Import Fails: "Collection Exists"
```bash
# Option 1: Use different name in GUI
# Option 2: Delete in Qdrant
curl -X DELETE http://localhost:6333/collections/markdown_chunks
```

### Out of Memory During Import
```bash
# In GUI: Reduce batch size to 100-200
# Or: Close other applications
# Or: Process in multiple sessions
```

## Best Practices Checklist

### Before Migration
- [ ] Backup ChromaDB data directory
- [ ] Start Qdrant and verify it's running
- [ ] Have enough disk space (2-3x export size)
- [ ] Close unnecessary applications

### During Export
- [ ] Export to both JSON and Pickle
- [ ] Check export log for errors
- [ ] Verify file sizes are reasonable
- [ ] Don't delete ChromaDB yet

### During Import
- [ ] Test connection first
- [ ] Start with smaller batch size
- [ ] Monitor memory usage
- [ ] Keep export files until verified

### After Migration
- [ ] Verify vector counts match
- [ ] Run test searches
- [ ] Keep ChromaDB backup for 2-4 weeks
- [ ] Update application to use Qdrant

## Configuration File Location

The GUI saves settings to:
```
~/.nerdbuntu_migration_config.json
```

Contains:
- Last used paths
- Qdrant URL and API key
- Batch size preferences
- History information

## Export File Structure

```
~/nerdbuntu/exports/qdrant/YYYYMMDD_HHMMSS/
├── collection_export_TIMESTAMP.json      # Human-readable
├── collection_export_TIMESTAMP.pkl       # Binary (faster)
├── collection_export_TIMESTAMP_stats.json # Metadata
└── QDRANT_IMPORT_GUIDE_TIMESTAMP.md     # Import instructions
```

## Log Window Tips

- **Scroll**: Mouse wheel or scrollbar
- **Copy**: Select text, Ctrl+C
- **Search**: Ctrl+F (in most text editors after copying)
- **Save**: Copy to text file for records

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Tab` | Next tab |
| `Ctrl+Shift+Tab` | Previous tab |
| `Esc` | Cancel file browser |
| `Enter` | Confirm dialogs |

## Command Line Equivalents

If GUI isn't working, use these CLI commands:

### Export
```bash
python export_to_qdrant.py
```

### Import
```bash
python import_to_qdrant.py \
  --json-file exports/qdrant/TIMESTAMP/export.pkl \
  --url http://localhost:6333 \
  --batch-size 500
```

### Import to Cloud
```bash
python import_to_qdrant.py \
  --json-file export.pkl \
  --url https://xyz.qdrant.io:6333 \
  --api-key YOUR_KEY
```

## Getting Help

### Documentation
- Full GUI Guide: [MIGRATION_GUI_GUIDE.md](MIGRATION_GUI_GUIDE.md)
- CLI Migration: [CHROMADB_TO_QDRANT_MIGRATION.md](CHROMADB_TO_QDRANT_MIGRATION.md)
- Qdrant Quick Ref: [QDRANT_QUICK_REFERENCE.md](QDRANT_QUICK_REFERENCE.md)

### Support
- GitHub Issues: https://github.com/Cosmicjedi/nerdbuntu/issues
- Include: Screenshots, log output, system info from Configuration tab

## Performance Tips

### For Speed
- ✅ Use Pickle format (3-5x faster than JSON)
- ✅ Increase batch size to 1000-2000
- ✅ Run Qdrant locally (not cloud) during import
- ✅ Close other applications

### For Reliability  
- ✅ Use smaller batch sizes (100-200)
- ✅ Enable verification
- ✅ Keep export files until verified
- ✅ Test search after import

### For Large Datasets (100K+ vectors)
- ✅ Export overnight
- ✅ Use Pickle format only
- ✅ Increase Qdrant memory limits
- ✅ Consider cloud Qdrant for permanent hosting

---

**Quick Start**: Launch GUI → Export → Setup Qdrant → Test Connection → Import → Verify ✅

**Version**: 1.0  
**Last Updated**: October 2024
