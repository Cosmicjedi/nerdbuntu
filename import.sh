#!/bin/bash

# Nerdbuntu Import Script
# Imports RAG data bundle on the destination machine

set -e

echo "=== Nerdbuntu Import Script ==="
echo "This script imports exported RAG data into your Nerdbuntu installation"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if an archive path was provided
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage: $0 <path-to-export-archive.zip>${NC}"
    echo ""
    echo "Example:"
    echo "  $0 ~/Downloads/nerdbuntu_rag_export_20251006_120000.zip"
    echo ""
    exit 1
fi

ARCHIVE_PATH="$1"

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

# Project directory
PROJECT_DIR="$HOME/nerdbuntu"

echo -e "${GREEN}Step 1: Checking Nerdbuntu installation...${NC}"

# Check if Nerdbuntu is installed
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Nerdbuntu not found at $PROJECT_DIR${NC}"
    echo ""
    read -p "Would you like to install Nerdbuntu now? (y/n): " response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Please run these commands first:"
        echo ""
        echo "  git clone https://github.com/Cosmicjedi/nerdbuntu.git"
        echo "  cd nerdbuntu"
        echo "  ./setup.sh"
        echo ""
        echo "Then run this import script again."
        exit 1
    else
        echo -e "${BLUE}Creating standalone import at $PROJECT_DIR${NC}"
        mkdir -p "$PROJECT_DIR/data/output"
        mkdir -p "$PROJECT_DIR/data/vector_db"
    fi
else
    echo -e "${BLUE}Found Nerdbuntu installation${NC}"
fi

OUTPUT_DIR="$PROJECT_DIR/data/output"
VECTOR_DB_DIR="$PROJECT_DIR/data/vector_db"

# Create directories if they don't exist
mkdir -p "$OUTPUT_DIR"
mkdir -p "$VECTOR_DB_DIR"

echo ""
echo -e "${GREEN}Step 2: Extracting archive...${NC}"

# Create temporary extraction directory
TEMP_DIR=$(mktemp -d)
echo "Extracting to temporary directory..."
unzip -q "$ARCHIVE_PATH" -d "$TEMP_DIR"

# Find the extracted directory (should be only one)
EXTRACTED_DIR=$(find "$TEMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)

if [ -z "$EXTRACTED_DIR" ]; then
    echo -e "${RED}Error: Could not find extracted directory${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo -e "${BLUE}Archive extracted successfully${NC}"

echo ""
echo -e "${GREEN}Step 3: Checking import options...${NC}"

# Check what's in the archive
HAS_MARKDOWN=false
HAS_VECTOR_DB=false

if [ -d "$EXTRACTED_DIR/markdown" ]; then
    MARKDOWN_COUNT=$(find "$EXTRACTED_DIR/markdown" -type f | wc -l)
    if [ $MARKDOWN_COUNT -gt 0 ]; then
        HAS_MARKDOWN=true
        echo -e "${BLUE}Found $MARKDOWN_COUNT markdown file(s)${NC}"
    fi
fi

if [ -d "$EXTRACTED_DIR/vector_db" ] && [ "$(ls -A $EXTRACTED_DIR/vector_db)" ]; then
    HAS_VECTOR_DB=true
    VECTOR_SIZE=$(du -sh "$EXTRACTED_DIR/vector_db" | cut -f1)
    echo -e "${BLUE}Found vector database ($VECTOR_SIZE)${NC}"
fi

if [ "$HAS_MARKDOWN" = false ] && [ "$HAS_VECTOR_DB" = false ]; then
    echo -e "${RED}Error: Archive appears to be empty or invalid${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo ""
echo -e "${YELLOW}Import Options:${NC}"
echo "  1. Merge with existing data (recommended)"
echo "  2. Replace existing data (WARNING: deletes current data)"
echo "  3. Cancel import"
echo ""
read -p "Choose option (1-3): " option

case $option in
    1)
        MODE="merge"
        echo -e "${GREEN}Will merge with existing data${NC}"
        ;;
    2)
        MODE="replace"
        echo -e "${YELLOW}WARNING: This will delete your current data${NC}"
        read -p "Are you sure? Type 'yes' to confirm: " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Import cancelled"
            rm -rf "$TEMP_DIR"
            exit 0
        fi
        ;;
    3)
        echo "Import cancelled"
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
echo -e "${GREEN}Step 4: Importing data...${NC}"

# Replace mode: clear existing data
if [ "$MODE" = "replace" ]; then
    echo "Clearing existing data..."
    rm -rf "$OUTPUT_DIR"/*
    rm -rf "$VECTOR_DB_DIR"/*
fi

# Import markdown files
if [ "$HAS_MARKDOWN" = true ]; then
    echo "Importing markdown files..."
    cp -r "$EXTRACTED_DIR/markdown"/* "$OUTPUT_DIR/" 2>/dev/null || true
    IMPORTED_MD=$(find "$OUTPUT_DIR" -type f | wc -l)
    echo -e "${GREEN}✓ Imported $IMPORTED_MD markdown file(s)${NC}"
fi

# Import vector database
if [ "$HAS_VECTOR_DB" = true ]; then
    echo "Importing vector database..."
    cp -r "$EXTRACTED_DIR/vector_db"/* "$VECTOR_DB_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✓ Imported vector database${NC}"
fi

# Copy documentation files
if [ -f "$EXTRACTED_DIR/EXPORT_INFO.txt" ]; then
    cp "$EXTRACTED_DIR/EXPORT_INFO.txt" "$PROJECT_DIR/LAST_IMPORT_INFO.txt"
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}=== Import Complete! ===${NC}"
echo ""
echo -e "${BLUE}Import Summary:${NC}"
echo "  Destination: $PROJECT_DIR"
echo "  Markdown files: $OUTPUT_DIR"
echo "  Vector database: $VECTOR_DB_DIR"
echo "  Import mode: $MODE"
echo ""

# Check if Nerdbuntu is fully installed
if [ -f "$PROJECT_DIR/app.py" ]; then
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Activate Nerdbuntu environment:"
    echo "     ${GREEN}source ~/nerdbuntu/venv/bin/activate${NC}"
    echo ""
    echo "  2. Query your imported data:"
    echo "     ${GREEN}cd ~/nerdbuntu${NC}"
    echo "     ${GREEN}python examples.py query 'your search query'${NC}"
    echo ""
    echo "  3. Or launch the GUI:"
    echo "     ${GREEN}python app.py${NC}"
else
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  Data imported to: $PROJECT_DIR"
    echo ""
    echo "  To use this data:"
    echo "  1. Install dependencies:"
    echo "     ${GREEN}pip install chromadb sentence-transformers${NC}"
    echo ""
    echo "  2. See LAST_IMPORT_INFO.txt for integration examples"
fi

echo ""
echo -e "${GREEN}Import successful! 🚀${NC}"
