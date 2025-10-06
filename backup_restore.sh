#!/bin/bash

# Nerdbuntu Backup and Restore Script
# Backup: Bundles all processed markdown files and ChromaDB vector database for transport/backup
# Restore: Extracts and restores data from a backup archive

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$HOME/nerdbuntu"
OUTPUT_DIR="$PROJECT_DIR/data/output"
VECTOR_DB_DIR="$PROJECT_DIR/data/vector_db"
EXPORT_DIR="$PROJECT_DIR/exports"

# Function to show usage
show_usage() {
    echo "=== Nerdbuntu Backup and Restore Script ==="
    echo ""
    echo "Usage:"
    echo "  $0 backup              Create a backup of your RAG data"
    echo "  $0 restore <file.zip>  Restore data from a backup archive"
    echo ""
    echo "Examples:"
    echo "  $0 backup"
    echo "  $0 restore ~/nerdbuntu/exports/nerdbuntu_backup_20251006_120000.zip"
    echo ""
}

# Function to create backup
create_backup() {
    echo "=== Nerdbuntu Backup ==="
    echo "Creating backup of your RAG data..."
    echo ""

    # Check if project directory exists
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}Error: Nerdbuntu project directory not found at $PROJECT_DIR${NC}"
        echo "Please run setup.sh first"
        exit 1
    fi

    # Create exports directory if it doesn't exist
    mkdir -p "$EXPORT_DIR"

    # Generate timestamp for unique backup filename
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_NAME="nerdbuntu_backup_${TIMESTAMP}"
    BACKUP_PATH="$EXPORT_DIR/${BACKUP_NAME}.zip"

    echo -e "${GREEN}Step 1: Checking data directories...${NC}"

    # Check if output directory has files
    OUTPUT_FILES=0
    if [ -d "$OUTPUT_DIR" ]; then
        if [ -n "$(ls -A $OUTPUT_DIR 2>/dev/null)" ]; then
            OUTPUT_FILES=$(find "$OUTPUT_DIR" -type f | wc -l)
            echo -e "${BLUE}Found $OUTPUT_FILES file(s) in output directory${NC}"
        else
            echo -e "${YELLOW}Warning: No files found in output directory ($OUTPUT_DIR)${NC}"
            echo "Have you processed any PDFs yet?"
            read -p "Continue anyway? (y/n): " response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                exit 0
            fi
        fi
    else
        echo -e "${YELLOW}Warning: Output directory does not exist${NC}"
        read -p "Continue anyway? (y/n): " response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi

    # Check if vector database exists
    VECTOR_DB_SIZE="0 bytes"
    if [ -d "$VECTOR_DB_DIR" ]; then
        if [ -n "$(ls -A $VECTOR_DB_DIR 2>/dev/null)" ]; then
            VECTOR_DB_SIZE=$(du -sh "$VECTOR_DB_DIR" | cut -f1)
            echo -e "${BLUE}Vector database size: $VECTOR_DB_SIZE${NC}"
        else
            echo -e "${YELLOW}Warning: Vector database directory is empty ($VECTOR_DB_DIR)${NC}"
            read -p "Continue anyway? (y/n): " response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                exit 0
            fi
        fi
    else
        echo -e "${YELLOW}Warning: Vector database directory does not exist${NC}"
        read -p "Continue anyway? (y/n): " response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi

    echo ""
    echo -e "${GREEN}Step 2: Creating temporary backup structure...${NC}"

    # Create temporary directory for organizing backup
    TEMP_DIR=$(mktemp -d)
    TEMP_BACKUP="$TEMP_DIR/$BACKUP_NAME"
    mkdir -p "$TEMP_BACKUP"

    # Copy output files
    echo "Copying markdown files..."
    if [ -d "$OUTPUT_DIR" ] && [ -n "$(ls -A $OUTPUT_DIR 2>/dev/null)" ]; then
        mkdir -p "$TEMP_BACKUP/markdown"
        cp -r "$OUTPUT_DIR"/* "$TEMP_BACKUP/markdown/" 2>/dev/null || true
    fi

    # Copy vector database
    echo "Copying vector database..."
    if [ -d "$VECTOR_DB_DIR" ] && [ -n "$(ls -A $VECTOR_DB_DIR 2>/dev/null)" ]; then
        mkdir -p "$TEMP_BACKUP/vector_db"
        cp -r "$VECTOR_DB_DIR"/* "$TEMP_BACKUP/vector_db/" 2>/dev/null || true
    fi

    # Create metadata file
    echo -e "${GREEN}Step 3: Creating metadata...${NC}"
    cat > "$TEMP_BACKUP/BACKUP_INFO.txt" << EOF
Nerdbuntu RAG Backup
====================

Backup Date: $(date)
Backup Machine: $(hostname)
Backup User: $(whoami)

Contents:
---------
- Markdown Files: $OUTPUT_FILES files
- Vector Database Size: $VECTOR_DB_SIZE
- Backup Name: $BACKUP_NAME

Directory Structure:
--------------------
$BACKUP_NAME/
├── markdown/          # Processed markdown files with semantic metadata
├── vector_db/         # ChromaDB vector database
├── BACKUP_INFO.txt    # This file
└── RESTORE_README.md  # Instructions for restoring

Vector Database Info:
---------------------
- Database Type: ChromaDB
- Collection Name: markdown_chunks
- Embedding Model: all-MiniLM-L6-v2
- Similarity Metric: Cosine

Restore Instructions:
---------------------
1. Run the restore command:
   ./backup_restore.sh restore $BACKUP_NAME.zip

2. Choose restore mode:
   - Merge: Add to existing data (safe)
   - Replace: Clear and restore (destructive)

3. Your data will be restored to:
   - Markdown: ~/nerdbuntu/data/output/
   - Vector DB: ~/nerdbuntu/data/vector_db/

Generated by: Nerdbuntu Backup & Restore Script
Repository: https://github.com/Cosmicjedi/nerdbuntu
EOF

    # Create restore instructions
    cat > "$TEMP_BACKUP/RESTORE_README.md" << 'EOF'
# Restoring Nerdbuntu Backup

This backup contains your processed markdown files and vector database.

## Quick Restore

### Using the Script (Recommended)

```bash
# Navigate to nerdbuntu directory
cd ~/nerdbuntu

# Restore with the script
./backup_restore.sh restore path/to/backup.zip
```

### Restore Options

When restoring, you'll be asked to choose:

1. **Merge Mode** (Recommended)
   - Adds backup data to existing data
   - Safe - won't delete anything
   - Use this if you want to combine multiple backups

2. **Replace Mode** (Careful!)
   - Deletes ALL existing data first
   - Then restores backup data
   - Use this for a clean restore

### Manual Restore

If you prefer to restore manually:

```bash
# Extract the backup
unzip nerdbuntu_backup_*.zip
cd nerdbuntu_backup_*

# Copy markdown files
cp -r markdown/* ~/nerdbuntu/data/output/

# Copy vector database
cp -r vector_db/* ~/nerdbuntu/data/vector_db/
```

## After Restoring

### Verify the Restoration

```bash
# Activate environment
source ~/nerdbuntu/venv/bin/activate
cd ~/nerdbuntu

# Check markdown files
ls -l data/output/

# Test vector database with a query
python examples.py query "test query"

# Or launch GUI
python app.py
```

### Using Your Restored Data

**Query the vector database:**
```bash
python examples.py query "your search text"
```

**Launch GUI application:**
```bash
python app.py
```

**Integrate with your RAG application:**
```python
from app import SemanticLinker

# Initialize with restored database
linker = SemanticLinker(endpoint, api_key)
linker.initialize_vector_db("~/nerdbuntu/data/vector_db")

# Query
results = linker.find_similar_chunks("your query", n_results=5)
```

## Backup Information

- **Backup contains:** All processed markdown files + complete ChromaDB database
- **Embedding model:** all-MiniLM-L6-v2 (must use same model for queries)
- **Collection name:** markdown_chunks
- **Database type:** ChromaDB (persistent client)

## Troubleshooting

### "Collection not found" error
```bash
# Verify database files exist
ls ~/nerdbuntu/data/vector_db/

# If empty, re-run restore
./backup_restore.sh restore backup.zip
```

### "Embedding dimension mismatch" error
- This means you're using a different embedding model
- You must use `all-MiniLM-L6-v2` for queries
- This model produces 384-dimensional embeddings

### Files not showing in GUI
```bash
# Refresh by restarting the app
python app.py
```

### Database seems corrupted
```bash
# Try replace mode (WARNING: deletes current data)
./backup_restore.sh restore backup.zip
# Choose option 2 (Replace)
```

## Multiple Backups

You can restore multiple backups using merge mode:

```bash
# Restore first backup
./backup_restore.sh restore backup1.zip
# Choose: Merge

# Restore second backup (adds to first)
./backup_restore.sh restore backup2.zip
# Choose: Merge

# All data now combined!
```

## Need Help?

- GitHub Issues: https://github.com/Cosmicjedi/nerdbuntu/issues
- Documentation: https://github.com/Cosmicjedi/nerdbuntu

---

**Happy restoring! 🔄**
EOF

    echo -e "${GREEN}Step 4: Creating ZIP archive...${NC}"
    cd "$TEMP_DIR"
    zip -r "$BACKUP_PATH" "$BACKUP_NAME" -q

    # Get final archive size
    ARCHIVE_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)

    # Cleanup temp directory
    rm -rf "$TEMP_DIR"

    echo ""
    echo -e "${GREEN}=== Backup Complete! ===${NC}"
    echo ""
    echo -e "${BLUE}Backup Summary:${NC}"
    echo "  Archive: $BACKUP_PATH"
    echo "  Size: $ARCHIVE_SIZE"
    echo "  Markdown files: $OUTPUT_FILES"
    echo "  Vector DB size: $VECTOR_DB_SIZE"
    echo ""
    echo -e "${YELLOW}To restore this backup:${NC}"
    echo "  ./backup_restore.sh restore $BACKUP_PATH"
    echo ""
    echo -e "${GREEN}Backup saved successfully! 💾${NC}"
}

# Function to restore from backup
restore_backup() {
    local ARCHIVE_PATH="$1"

    echo "=== Nerdbuntu Restore ==="
    echo "Restoring data from backup archive..."
    echo ""

    # Check if archive path was provided
    if [ -z "$ARCHIVE_PATH" ]; then
        echo -e "${RED}Error: No backup archive specified${NC}"
        echo ""
        echo "Usage: $0 restore <path-to-backup.zip>"
        exit 1
    fi

    # Check if archive exists
    if [ ! -f "$ARCHIVE_PATH" ]; then
        echo -e "${RED}Error: Archive not found: $ARCHIVE_PATH${NC}"
        exit 1
    fi

    # Check if it's a zip file
    if [[ ! "$ARCHIVE_PATH" =~ \.zip$ ]]; then
        echo -e "${RED}Error: File must be a .zip archive${NC}"
        exit 1
    fi

    echo -e "${GREEN}Step 1: Checking Nerdbuntu installation...${NC}"

    # Check if Nerdbuntu is installed
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${YELLOW}Nerdbuntu not found at $PROJECT_DIR${NC}"
        echo ""
        read -p "Would you like to create data directories? (y/n): " response
        
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Creating data directories at $PROJECT_DIR${NC}"
            mkdir -p "$OUTPUT_DIR"
            mkdir -p "$VECTOR_DB_DIR"
        else
            echo "Restore cancelled"
            exit 1
        fi
    else
        echo -e "${BLUE}Found Nerdbuntu installation${NC}"
    fi

    # Create directories if they don't exist
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$VECTOR_DB_DIR"

    echo ""
    echo -e "${GREEN}Step 2: Extracting backup archive...${NC}"

    # Create temporary extraction directory
    TEMP_DIR=$(mktemp -d)
    echo "Extracting to temporary directory..."
    unzip -q "$ARCHIVE_PATH" -d "$TEMP_DIR"

    # Find the extracted directory
    EXTRACTED_DIR=$(find "$TEMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)

    if [ -z "$EXTRACTED_DIR" ]; then
        echo -e "${RED}Error: Could not find extracted directory${NC}"
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    echo -e "${BLUE}Archive extracted successfully${NC}"

    echo ""
    echo -e "${GREEN}Step 3: Analyzing backup contents...${NC}"

    # Check what's in the archive
    HAS_MARKDOWN=false
    HAS_VECTOR_DB=false
    MARKDOWN_COUNT=0
    VECTOR_SIZE="0"

    if [ -d "$EXTRACTED_DIR/markdown" ]; then
        MARKDOWN_COUNT=$(find "$EXTRACTED_DIR/markdown" -type f 2>/dev/null | wc -l)
        if [ "$MARKDOWN_COUNT" -gt 0 ]; then
            HAS_MARKDOWN=true
            echo -e "${BLUE}Found $MARKDOWN_COUNT markdown file(s)${NC}"
        fi
    fi

    if [ -d "$EXTRACTED_DIR/vector_db" ] && [ -n "$(ls -A $EXTRACTED_DIR/vector_db 2>/dev/null)" ]; then
        HAS_VECTOR_DB=true
        VECTOR_SIZE=$(du -sh "$EXTRACTED_DIR/vector_db" 2>/dev/null | cut -f1)
        echo -e "${BLUE}Found vector database ($VECTOR_SIZE)${NC}"
    fi

    if [ "$HAS_MARKDOWN" = "false" ] && [ "$HAS_VECTOR_DB" = "false" ]; then
        echo -e "${RED}Error: Backup appears to be empty or invalid${NC}"
        rm -rf "$TEMP_DIR"
        exit 1
    fi

    echo ""
    echo -e "${YELLOW}Restore Options:${NC}"
    echo "  1. Merge with existing data (recommended - safe)"
    echo "  2. Replace existing data (WARNING: deletes current data)"
    echo "  3. Cancel restore"
    echo ""
    read -p "Choose option (1-3): " option

    case $option in
        1)
            MODE="merge"
            echo -e "${GREEN}Will merge with existing data${NC}"
            ;;
        2)
            MODE="replace"
            echo -e "${YELLOW}WARNING: This will DELETE ALL your current data!${NC}"
            read -p "Are you absolutely sure? Type 'DELETE' to confirm: " confirm
            if [ "$confirm" != "DELETE" ]; then
                echo "Restore cancelled"
                rm -rf "$TEMP_DIR"
                exit 0
            fi
            ;;
        3)
            echo "Restore cancelled"
            rm -rf "$TEMP_DIR"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            rm -rf "$TEMP_DIR"
            exit 1
            ;;
    esac

    echo ""
    echo -e "${GREEN}Step 4: Restoring data...${NC}"

    # Replace mode: clear existing data
    if [ "$MODE" = "replace" ]; then
        echo "Clearing existing data..."
        rm -rf "$OUTPUT_DIR"/*
        rm -rf "$VECTOR_DB_DIR"/*
        echo -e "${BLUE}Existing data cleared${NC}"
    fi

    # Restore markdown files
    if [ "$HAS_MARKDOWN" = "true" ]; then
        echo "Restoring markdown files..."
        cp -r "$EXTRACTED_DIR/markdown"/* "$OUTPUT_DIR/" 2>/dev/null || true
        RESTORED_MD=$(find "$OUTPUT_DIR" -type f 2>/dev/null | wc -l)
        echo -e "${GREEN}✓ Restored $RESTORED_MD markdown file(s)${NC}"
    fi

    # Restore vector database
    if [ "$HAS_VECTOR_DB" = "true" ]; then
        echo "Restoring vector database..."
        cp -r "$EXTRACTED_DIR/vector_db"/* "$VECTOR_DB_DIR/" 2>/dev/null || true
        echo -e "${GREEN}✓ Restored vector database${NC}"
    fi

    # Copy backup info
    if [ -f "$EXTRACTED_DIR/BACKUP_INFO.txt" ]; then
        cp "$EXTRACTED_DIR/BACKUP_INFO.txt" "$PROJECT_DIR/LAST_RESTORE_INFO.txt"
    fi

    # Cleanup
    rm -rf "$TEMP_DIR"

    echo ""
    echo -e "${GREEN}=== Restore Complete! ===${NC}"
    echo ""
    echo -e "${BLUE}Restore Summary:${NC}"
    echo "  Restored to: $PROJECT_DIR"
    echo "  Markdown files: $OUTPUT_DIR"
    echo "  Vector database: $VECTOR_DB_DIR"
    echo "  Restore mode: $MODE"
    echo ""

    # Check if Nerdbuntu is fully installed
    if [ -f "$PROJECT_DIR/app.py" ]; then
        echo -e "${YELLOW}Next Steps:${NC}"
        echo "  1. Activate environment:"
        echo "     ${GREEN}source ~/nerdbuntu/venv/bin/activate${NC}"
        echo ""
        echo "  2. Verify restoration:"
        echo "     ${GREEN}cd ~/nerdbuntu${NC}"
        echo "     ${GREEN}python examples.py query 'test query'${NC}"
        echo ""
        echo "  3. Or launch the GUI:"
        echo "     ${GREEN}python app.py${NC}"
    else
        echo -e "${YELLOW}Next Steps:${NC}"
        echo "  Data restored to: $PROJECT_DIR"
        echo "  See LAST_RESTORE_INFO.txt for details"
    fi

    echo ""
    echo -e "${GREEN}Restore successful! 🔄${NC}"
}

# Main script logic
case "$1" in
    backup)
        create_backup
        ;;
    restore)
        restore_backup "$2"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
