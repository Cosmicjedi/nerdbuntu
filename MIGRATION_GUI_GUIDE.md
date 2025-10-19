# ChromaDB to Qdrant Migration GUI

A user-friendly graphical interface for migrating your vector database from ChromaDB to Qdrant.

## Overview

The Migration GUI provides a complete workflow for:
1. **Backing up** (exporting) your ChromaDB data
2. **Restoring** (importing) data to Qdrant
3. **Verifying** the migration was successful
4. **Testing** the new Qdrant database

## Features

### 🎯 Main Features

- **Tab-based Interface**: Organized workflow with separate tabs for each step
- **Real-time Logging**: See exactly what's happening during export/import
- **Progress Tracking**: Visual progress indicators for long-running operations
- **Configuration Management**: Save your settings for future use
- **Connection Testing**: Verify Qdrant is reachable before importing
- **Verification**: Automatic verification that all vectors were migrated
- **Test Search**: Run test queries to ensure everything works
- **History Tracking**: View past migration operations

### 📊 Export (Backup) Features

- Export to JSON format (human-readable)
- Export to Pickle format (faster, more compact)
- Choose which collections to export
- Automatic statistics generation
- Export multiple collections at once

### 📥 Import (Restore) Features

- Import from JSON or Pickle files
- Configurable batch sizes for optimal performance
- Custom collection naming
- Automatic collection creation
- Vector count verification
- Test search functionality
- Support for Qdrant Cloud and local instances

## Quick Start

### Prerequisites

```bash
# Install required packages
pip install chromadb sentence-transformers qdrant-client

# On Ubuntu/Debian, you may also need:
sudo apt-get install python3-tk
```

### Launch the GUI

**Option 1: Using the shell script (recommended)**
```bash
cd ~/nerdbuntu
chmod +x launch_migration_gui.sh
./launch_migration_gui.sh
```

**Option 2: Using Python directly**
```bash
cd ~/nerdbuntu
python3 launch_migration_gui.py
```

**Option 3: From the GUI directory**
```bash
cd ~/nerdbuntu/gui
python3 migration_gui.py
```

## User Guide

### Step 1: Set Up Qdrant

Before migrating, you need a running Qdrant instance.

#### Option A: Docker (Recommended for Testing)

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

#### Option B: Qdrant Cloud

1. Sign up at https://cloud.qdrant.io
2. Create a cluster
3. Copy your cluster URL and API key

### Step 2: Export from ChromaDB

1. **Open the Migration GUI**
   ```bash
   ./launch_migration_gui.sh
   ```

2. **Go to the "1. Backup from ChromaDB" tab**

3. **Configure paths**:
   - **ChromaDB Path**: Location of your ChromaDB database
     - Default: `~/nerdbuntu/data/vector_db`
   - **Export Directory**: Where to save exported files
     - Default: `~/nerdbuntu/exports/qdrant`

4. **Select export formats**:
   - ✅ **JSON**: Human-readable, easier to debug (recommended for small datasets)
   - ✅ **Pickle**: Binary format, faster and more compact (recommended for large datasets)

5. **Click "🚀 Start Export"**

6. **Monitor the log** to see:
   - Collections being processed
   - Number of vectors exported
   - File sizes
   - Completion status

7. **Export files** will be saved to:
   ```
   ~/nerdbuntu/exports/qdrant/YYYYMMDD_HHMMSS/
   ├── collection_name_export_TIMESTAMP.json
   ├── collection_name_export_TIMESTAMP.pkl
   └── collection_name_export_TIMESTAMP_stats.json
   ```

### Step 3: Import to Qdrant

1. **Go to the "2. Restore to Qdrant" tab**

2. **Select export file**:
   - Click "Browse" to select your exported `.json` or `.pkl` file
   - Tip: `.pkl` files are faster to load

3. **Configure Qdrant connection**:
   - **Qdrant URL**: 
     - Local: `http://localhost:6333`
     - Cloud: Your cluster URL (e.g., `https://xyz-example.qdrant.io:6333`)
   - **API Key**: (Optional) For Qdrant Cloud only

4. **Test connection**:
   - Click "Test Connection" to verify Qdrant is accessible
   - You'll see existing collections (if any)

5. **Configure import options**:
   - **Collection Name**: Leave empty to use original name, or provide custom name
   - **Batch Size**: Number of vectors to upload at once (default: 500)
     - Smaller (100-200): Safer, slower
     - Larger (1000-2000): Faster, requires more memory
   - **Verify import**: ✅ Recommended - checks vector counts match
   - **Run test search**: ✅ Recommended - ensures search works

6. **Click "🚀 Start Import"**

7. **Monitor the log** to see:
   - Connection status
   - Collection creation
   - Upload progress
   - Verification results
   - Test search results

### Step 4: Verify Success

The GUI automatically verifies the import, but you can also manually check:

1. **Check the log** in the Import tab:
   - Look for: `✅ Verification successful! Counts match.`
   - Look for: `✅ Search successful! Found X results`

2. **Use Qdrant's web UI** (if running locally):
   - Open: http://localhost:6333/dashboard
   - Browse your collections
   - View vector counts
   - Run test searches

3. **Use the Configuration tab**:
   - View system information
   - Check installed packages
   - See current settings

4. **Check the History tab**:
   - View past export/import operations
   - See timestamps and details

## Configuration Tab

The Configuration tab shows:

- **System Information**:
  - Python version
  - Installed packages (ChromaDB, Qdrant, etc.)
  - Current configuration paths

- **Default Paths**:
  - Settings are saved automatically to `~/.nerdbuntu_migration_config.json`

## History Tab

The History tab shows:

- Recent export operations
- Recent import operations
- Timestamps and status
- Details about each operation

## Troubleshooting

### GUI won't start

**Problem**: `ModuleNotFoundError: No module named 'tkinter'`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
# tkinter should be included with Python
# If not, reinstall Python from python.org

# Windows
# tkinter should be included
# If not, reinstall Python with "tcl/tk" option
```

### Export fails

**Problem**: `ChromaDB not found at: /path/to/vector_db`

**Solution**:
- Make sure you've processed some documents first
- Check the ChromaDB path is correct
- Browse to the correct location using the GUI

**Problem**: `No collections found to export`

**Solution**:
- Your ChromaDB is empty
- Process some documents first using the main Nerdbuntu application

### Import fails

**Problem**: `Failed to connect to Qdrant`

**Solution**:
- Make sure Qdrant is running: `docker ps | grep qdrant`
- Check the URL is correct (default: `http://localhost:6333`)
- For Qdrant Cloud, verify API key and URL

**Problem**: `Collection already exists`

**Solution**:
- Delete the existing collection in Qdrant, or
- Use a different collection name in the GUI

**Problem**: `Vector dimension mismatch`

**Solution**:
- Ensure you're using the same embedding model (`all-MiniLM-L6-v2`)
- The export includes model information - don't mix different models

**Problem**: `Out of memory during import`

**Solution**:
- Reduce batch size (try 100-200)
- Close other applications
- For very large datasets, import in multiple sessions

### Verification warnings

**Problem**: `⚠️ Warning: Count mismatch!`

**Solution**:
- Check the import log for errors
- Some vectors may have been skipped (e.g., if they had no embeddings)
- The difference is usually small - check if it's acceptable
- If major mismatch, re-run the import

## Advanced Usage

### Custom Export Directory Structure

You can organize exports by date or project:

```bash
~/nerdbuntu/exports/qdrant/
├── 2024-01-15_project_a/
│   └── markdown_chunks_export_*.json
├── 2024-01-20_project_b/
│   └── markdown_chunks_export_*.json
└── 2024-01-25_full_backup/
    └── markdown_chunks_export_*.json
```

### Batch Processing Multiple Exports

For very large datasets, you can:

1. Export collections one at a time
2. Import them separately
3. Use different batch sizes for different collections

### Using with Qdrant Cloud

1. Create a cluster at https://cloud.qdrant.io
2. Copy your cluster URL: `https://xyz-example.qdrant.io:6333`
3. Copy your API key from the dashboard
4. In the GUI:
   - Set **Qdrant URL** to your cluster URL
   - Set **API Key** to your key
   - Test connection before importing

### Automation

While the GUI is for interactive use, you can still use the CLI tools for automation:

**Export**:
```bash
python3 export_to_qdrant.py
```

**Import**:
```bash
python3 import_to_qdrant.py --json-file exports/qdrant/latest/export.json
```

## Best Practices

### Before Migration

1. ✅ **Backup your ChromaDB** data directory
2. ✅ **Test Qdrant** is running and accessible
3. ✅ **Have enough disk space** (exports can be large)
4. ✅ **Note your embedding model** (should be `all-MiniLM-L6-v2`)

### During Export

1. ✅ **Export to both JSON and Pickle** (JSON for debugging, Pickle for speed)
2. ✅ **Keep the export log** for troubleshooting
3. ✅ **Verify file sizes** are reasonable (check stats file)
4. ✅ **Don't delete ChromaDB** until migration is verified

### During Import

1. ✅ **Start with a test collection** before full migration
2. ✅ **Monitor memory usage** during import
3. ✅ **Adjust batch size** if needed
4. ✅ **Enable verification** to catch issues early

### After Migration

1. ✅ **Run test queries** to verify results
2. ✅ **Compare performance** with ChromaDB
3. ✅ **Keep ChromaDB backup** for 2-4 weeks
4. ✅ **Update your application** to use Qdrant
5. ✅ **Set up Qdrant backups** (snapshots)

## Performance Tips

### For Large Datasets (100K+ vectors)

- Use **Pickle** format for exports (3-5x faster than JSON)
- Increase **batch size** to 1000-2000 for imports
- Run Qdrant with adequate memory (8GB+ recommended)
- Consider using **async client** for very large imports (requires code changes)

### For Slow Networks

- Reduce **batch size** to 200-300
- Use local Qdrant instead of cloud (for testing)
- Upload in multiple sessions if needed

### For Limited Memory

- Reduce **batch size** to 100-200
- Close other applications
- Process collections one at a time
- Consider upgrading system memory

## Files and Locations

### Configuration File
```
~/.nerdbuntu_migration_config.json
```
Contains saved settings (paths, URLs, etc.)

### Export Files
```
~/nerdbuntu/exports/qdrant/YYYYMMDD_HHMMSS/
```
Contains exported data in JSON and/or Pickle format

### Logs
The GUI doesn't save logs to files, but you can:
- Copy from the log window
- Screenshot for records
- Use the CLI tools which log to files

## FAQ

**Q: Can I migrate back from Qdrant to ChromaDB?**

A: The export creates a Qdrant-specific format. To migrate back, you'd need to:
1. Export from Qdrant using its tools
2. Convert the format
3. Import to ChromaDB
Better to keep your ChromaDB backup!

**Q: How long does migration take?**

A: Depends on dataset size:
- 1K vectors: ~30 seconds
- 10K vectors: ~2-5 minutes
- 100K vectors: ~15-30 minutes
- 1M vectors: ~2-4 hours

**Q: Can I cancel a migration in progress?**

A: Yes! Close the GUI window. Partial data may be in Qdrant - you can delete the collection and start over.

**Q: Do I need to export and import on the same machine?**

A: No! You can:
1. Export on Machine A
2. Copy export files to Machine B
3. Import on Machine B with Qdrant running there

**Q: Can I import the same export multiple times?**

A: Yes, but you'll need to delete the existing collection first, or use a different collection name.

**Q: What happens if import fails midway?**

A: Partial data will be in Qdrant. Options:
1. Delete the collection and retry
2. Resume (if you track which batches completed)
3. Check logs to see what went wrong

## Support

### Getting Help

- **GitHub Issues**: https://github.com/Cosmicjedi/nerdbuntu/issues
- **Documentation**: See CHROMADB_TO_QDRANT_MIGRATION.md
- **Qdrant Docs**: https://qdrant.tech/documentation/

### Reporting Bugs

When reporting issues, include:

1. **GUI version**: Check the Configuration tab
2. **Error message**: Copy from the log window
3. **Steps to reproduce**: What you clicked/entered
4. **System info**: From the Configuration tab
5. **Dataset size**: Number of vectors
6. **Screenshots**: If helpful

### Feature Requests

We welcome suggestions! Please open a GitHub issue with:
- **Use case**: What you're trying to do
- **Current limitation**: What's not working
- **Proposed solution**: Your idea

## License

This migration GUI is part of the Nerdbuntu project and uses the same license.

## Acknowledgments

- **ChromaDB**: For the excellent vector database
- **Qdrant**: For the powerful production-ready alternative
- **Contributors**: Everyone who helped test and improve the migration process

---

**Version**: 1.0  
**Last Updated**: October 2024  
**Compatibility**: ChromaDB 0.4+, Qdrant 1.6+
