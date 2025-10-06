#!/bin/bash

# Vector Database Backup and Restore Script
# For moving vector data to LLM environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default paths
VECTOR_DB_DIR="${VECTOR_DB_DIR:-$HOME/nerdbuntu/data/vector_db}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/nerdbuntu/backups/vector_db}"

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

backup_vector_db() {
    print_header "Vector Database Backup"
    
    if [ ! -d "$VECTOR_DB_DIR" ]; then
        print_error "Vector database directory not found: $VECTOR_DB_DIR"
        exit 1
    fi
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Generate timestamp
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/vector_db_backup_$TIMESTAMP.tar.gz"
    
    print_info "Backing up vector database..."
    print_info "Source: $VECTOR_DB_DIR"
    print_info "Destination: $BACKUP_FILE"
    
    # Create tarball
    tar -czf "$BACKUP_FILE" -C "$(dirname "$VECTOR_DB_DIR")" "$(basename "$VECTOR_DB_DIR")"
    
    # Get file size
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    
    print_success "Vector database backed up successfully!"
    print_info "Backup file: $BACKUP_FILE"
    print_info "Size: $FILE_SIZE"
    
    echo ""
    print_success "Ready to transfer to LLM environment!"
}

restore_vector_db() {
    BACKUP_FILE="$1"
    
    print_header "Vector Database Restore"
    
    if [ -z "$BACKUP_FILE" ]; then
        print_error "Please specify a backup file"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_info "Backup file: $BACKUP_FILE"
    print_info "Destination: $VECTOR_DB_DIR"
    
    # Confirm if destination exists
    if [ -d "$VECTOR_DB_DIR" ]; then
        print_info "Existing vector database found."
        read -p "Proceed with restore? This will replace existing data (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Restore cancelled"
            exit 0
        fi
        
        # Remove existing database
        rm -rf "$VECTOR_DB_DIR"
        print_info "Removed existing database"
    fi
    
    # Create parent directory
    mkdir -p "$(dirname "$VECTOR_DB_DIR")"
    
    # Extract backup
    print_info "Restoring vector database..."
    tar -xzf "$BACKUP_FILE" -C "$(dirname "$VECTOR_DB_DIR")"
    
    print_success "Vector database restored successfully!"
    print_info "Location: $VECTOR_DB_DIR"
}

list_backups() {
    print_header "Available Vector Database Backups"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_info "No backups found. Backup directory does not exist."
        exit 0
    fi
    
    BACKUPS=$(find "$BACKUP_DIR" -name "vector_db_backup_*.tar.gz" -type f 2>/dev/null | sort -r)
    
    if [ -z "$BACKUPS" ]; then
        print_info "No backups found in: $BACKUP_DIR"
        exit 0
    fi
    
    echo "Backups found in: $BACKUP_DIR"
    echo ""
    
    COUNT=1
    while IFS= read -r backup; do
        FILENAME=$(basename "$backup")
        SIZE=$(du -h "$backup" | cut -f1)
        
        echo "${COUNT}. $FILENAME"
        echo "   Size: $SIZE"
        echo ""
        
        COUNT=$((COUNT + 1))
    done <<< "$BACKUPS"
}

export_for_llm() {
    EXPORT_FILE="$1"
    
    print_header "Export Vector Database for LLM Environment"
    
    if [ -z "$EXPORT_FILE" ]; then
        EXPORT_FILE="vector_db_export_$(date +%Y%m%d_%H%M%S).tar.gz"
    fi
    
    if [ ! -d "$VECTOR_DB_DIR" ]; then
        print_error "Vector database directory not found: $VECTOR_DB_DIR"
        exit 1
    fi
    
    print_info "Exporting vector database for LLM environment..."
    print_info "Source: $VECTOR_DB_DIR"
    print_info "Export file: $EXPORT_FILE"
    
    # Create tarball
    tar -czf "$EXPORT_FILE" -C "$(dirname "$VECTOR_DB_DIR")" "$(basename "$VECTOR_DB_DIR")"
    
    FILE_SIZE=$(du -h "$EXPORT_FILE" | cut -f1)
    
    print_success "Vector database exported successfully!"
    print_info "Export file: $(pwd)/$EXPORT_FILE"
    print_info "Size: $FILE_SIZE"
    
    # Create README
    README_FILE="${EXPORT_FILE%.tar.gz}_README.txt"
    cat > "$README_FILE" << EOF
Vector Database Export from Nerdbuntu
=====================================

Export Date: $(date)
Export File: $EXPORT_FILE
Size: $FILE_SIZE

USAGE IN LLM ENVIRONMENT:
=========================

1. Extract the archive:
   tar -xzf $EXPORT_FILE

2. The vector_db folder contains a ChromaDB database

3. To use in Python:
   import chromadb
   client = chromadb.PersistentClient(path="./vector_db")
   collection = client.get_collection("markdown_chunks")
   
4. Query example:
   results = collection.query(
       query_texts=["your query"],
       n_results=5
   )

REQUIREMENTS:
============
- chromadb Python package
- sentence-transformers (for embeddings)

Install with: pip install chromadb sentence-transformers
EOF
    
    print_success "README created: $README_FILE"
    print_success "Ready for transfer to LLM environment!"
}

show_usage() {
    echo "Vector Database Backup and Restore Script"
    echo ""
    echo "Usage:"
    echo "  $0 backup              - Create a backup of the vector database"
    echo "  $0 restore <file>      - Restore vector database from backup"
    echo "  $0 list                - List available backups"
    echo "  $0 export [file]       - Export for LLM environment (with README)"
    echo ""
    echo "Examples:"
    echo "  $0 backup"
    echo "  $0 export my_vectors.tar.gz"
    echo "  $0 list"
}

# Main script
case "${1:-help}" in
    backup)
        backup_vector_db
        ;;
    restore)
        restore_vector_db "$2"
        ;;
    list)
        list_backups
        ;;
    export)
        export_for_llm "$2"
        ;;
    help|--help|-h|*)
        show_usage
        ;;
esac
