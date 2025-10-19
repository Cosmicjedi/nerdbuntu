# Migration GUI Screenshots

Visual guide to the ChromaDB to Qdrant Migration GUI interface.

## Launch Screen

When you launch the Migration GUI using `./launch_migration_gui.sh`, you'll see the main window with four tabs.

## Tab 1: Backup from ChromaDB

### Export Configuration
```
┌─────────────────────────────────────────────────────────────┐
│ ChromaDB to Qdrant Migration Tool                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Export ChromaDB to Qdrant Format                          │
│                                                              │
│  ┌─ ChromaDB Location ────────────────────────────────┐    │
│  │ ChromaDB Path:                                     │    │
│  │ [/home/user/nerdbuntu/data/vector_db] [Browse]     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Export Destination ──────────────────────────────┐    │
│  │ Export Directory:                                  │    │
│  │ [/home/user/nerdbuntu/exports/qdrant]  [Browse]    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Export Options ──────────────────────────────────┐    │
│  │ ☑ Export as JSON (human-readable)                 │    │
│  │ ☑ Export as Pickle (faster, compact)              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│                    [🚀 Start Export]                         │
│                                                              │
│  [████████████████████████      ]  Progress             │
│                                                              │
│  ┌─ Export Log ──────────────────────────────────────┐    │
│  │ [12:34:56] 📂 Connecting to ChromaDB...           │    │
│  │ [12:34:57] ✅ Connected!                           │    │
│  │ [12:34:57] 📋 Found 1 collection(s)                │    │
│  │ [12:34:57]   - markdown_chunks                     │    │
│  │ [12:34:58] 🔄 Exporting collection: markdown_chunks│    │
│  │ [12:34:58]   Found 5000 items                      │    │
│  │ [12:35:02] ✅ Export complete!                     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Key Elements
- **Path Selection**: Browse buttons to select directories
- **Format Options**: Choose JSON, Pickle, or both
- **Progress Bar**: Shows activity during export
- **Log Window**: Real-time status messages with timestamps

## Tab 2: Restore to Qdrant

### Import Configuration
```
┌─────────────────────────────────────────────────────────────┐
│ Import to Qdrant Database                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ Export File ─────────────────────────────────────┐    │
│  │ Select Export File:                                │    │
│  │ [.../markdown_chunks_export_20241019.pkl] [Browse] │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Qdrant Connection ───────────────────────────────┐    │
│  │ Qdrant URL:                                        │    │
│  │ [http://localhost:6333]                            │    │
│  │                                                     │    │
│  │ API Key (optional, for Qdrant Cloud):             │    │
│  │ [••••••••••••••]                                   │    │
│  │                                                     │    │
│  │              [Test Connection]                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ Import Options ──────────────────────────────────┐    │
│  │ Collection Name (leave empty to use default):     │    │
│  │ []                                                 │    │
│  │                                                     │    │
│  │ Batch Size: [500]                                  │    │
│  │                                                     │    │
│  │ ☑ Verify import after completion                  │    │
│  │ ☑ Run test search                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│                    [🚀 Start Import]                         │
│                                                              │
│  [████████████████████████████████]  Progress            │
│                                                              │
│  ┌─ Import Log ──────────────────────────────────────┐    │
│  │ [12:40:15] 🔗 Connecting to Qdrant...             │    │
│  │ [12:40:16] ✅ Connected! Found 0 collection(s)     │    │
│  │ [12:40:16] 📂 Loading: markdown_chunks_export.pkl  │    │
│  │ [12:40:17] ✅ Loaded pickle file                   │    │
│  │ [12:40:17] 🔧 Creating collection: markdown_chunks │    │
│  │ [12:40:18] ✅ Collection created                   │    │
│  │ [12:40:18] 📤 Importing 5000 vectors (batch: 500)  │    │
│  │ [12:40:22]   Progress: 5000/5000 (100.0%)          │    │
│  │ [12:40:22] ✅ Import complete! Imported 5000       │    │
│  │ [12:40:22] 🔍 Verifying import...                  │    │
│  │ [12:40:23] ✅ Verification successful!             │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Key Elements
- **File Selection**: Browse for JSON or Pickle export files
- **Connection Settings**: Qdrant URL and optional API key
- **Test Connection**: Verify Qdrant is accessible
- **Import Options**: Batch size, verification, testing
- **Progress Tracking**: Shows percentage completed

## Tab 3: Configuration

### System Information
```
┌─────────────────────────────────────────────────────────────┐
│ Migration Settings                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ Default Paths ───────────────────────────────────┐    │
│  │                                                     │    │
│  │  These settings are saved automatically            │    │
│  │                                                     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─ System Information ──────────────────────────────┐    │
│  │ === ChromaDB to Qdrant Migration Tool ===         │    │
│  │ Python Version: 3.10.12                           │    │
│  │ Platform: linux                                    │    │
│  │                                                     │    │
│  │ === Installed Packages ===                         │    │
│  │ ✅ ChromaDB: 0.4.24                                │    │
│  │ ✅ Qdrant Client: Installed                        │    │
│  │ ✅ Sentence Transformers: Installed                │    │
│  │                                                     │    │
│  │ === Configuration ===                              │    │
│  │ ChromaDB Path: /home/user/nerdbuntu/data/vector_db│    │
│  │ Export Directory: /home/user/nerdbuntu/exports/... │    │
│  │ Qdrant URL: http://localhost:6333                 │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Key Elements
- **System Info**: Python version, platform
- **Package Status**: Shows installed dependencies
- **Current Config**: Display saved settings

## Tab 4: History

### Operation History
```
┌─────────────────────────────────────────────────────────────┐
│ Migration History                                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Timestamp          │ Operation │ Status  │ Details  │    │
│  ├────────────────────┼───────────┼─────────┼──────────┤    │
│  │ 2024-10-19 12:40   │ Import    │ Success │ 5000...  │    │
│  │ 2024-10-19 12:35   │ Export    │ Success │ 1 col... │    │
│  │ 2024-10-18 16:22   │ Export    │ Success │ 1 col... │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│                   [Refresh History]                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Elements
- **Operation Log**: Past exports and imports
- **Timestamps**: When operations occurred
- **Status**: Success/failure indicators
- **Details**: Brief operation summary

## Status Bar

At the bottom of every tab:
```
└─────────────────────────────────────────────────────────────┘
  Status: Ready                                               
```

Shows current operation status:
- "Ready" - Waiting for user action
- "Exporting..." - Export in progress
- "Importing..." - Import in progress
- "Done" - Operation complete

## Color Coding in Logs

The GUI uses color-coded symbols:
- ✅ **Green Check**: Success messages
- ❌ **Red X**: Error messages
- ⚠️ **Yellow Warning**: Warning messages
- 📂 **Blue Icon**: Information messages
- 🔄 **Spinner**: Process messages
- 🚀 **Rocket**: Launch/start messages

## Typical Workflow Visualization

```
┌─────────────┐
│  1. Export  │  Tab 1: Configure and export ChromaDB
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 2. Qdrant   │  Terminal: Start Qdrant Docker container
│   Setup     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 3. Test     │  Tab 2: Click "Test Connection"
│  Connect    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  4. Import  │  Tab 2: Start import with verification
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  5. Verify  │  Check logs for success messages
└─────────────┘
```

## Screenshot Checklist

To take your own screenshots for documentation:

### Export Tab
- [ ] Empty state (before export)
- [ ] During export (with progress bar)
- [ ] After successful export (with completion message)
- [ ] Error state (wrong path)

### Import Tab
- [ ] Connection test success
- [ ] Connection test failure
- [ ] During import (with progress)
- [ ] After successful import
- [ ] Verification messages

### Configuration Tab
- [ ] System information display
- [ ] All packages installed
- [ ] Missing packages warning

### History Tab
- [ ] Empty history
- [ ] Multiple operations listed
- [ ] Detailed view of one operation

## Notes for Screenshot Contributors

If you're contributing screenshots to this documentation:

1. **Window Size**: Resize to 900x700 for consistency
2. **Font Size**: Use default system font
3. **Sample Data**: Use ~1000-5000 vectors for screenshots
4. **Privacy**: Blur any API keys or personal paths
5. **Format**: PNG format, reasonable compression
6. **Naming**: Use descriptive names (e.g., `export-success.png`)
7. **Location**: Place in `docs/images/migration-gui/`

## Creating Animated GIFs

For tutorial GIFs showing the workflow:

1. Use screen recording software (e.g., `peek`, `byzanz`)
2. Keep recordings short (10-30 seconds)
3. Focus on specific actions
4. Show cursor movements clearly
5. Save as optimized GIF

Suggested GIF topics:
- Complete export process
- Testing Qdrant connection
- Complete import process
- Handling an error

---

**Note**: This document provides ASCII representations of the GUI. For actual screenshots, run the application and capture images of the interface.

**To contribute screenshots**: Please see CONTRIBUTING.md for guidelines on adding images to the documentation.
