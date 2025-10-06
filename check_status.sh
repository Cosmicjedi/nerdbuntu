#!/bin/bash

# Status Check Script - Run on your LOCAL machine
# This will diagnose what's happening with your processing

echo "======================================================================"
echo "NERDBUNTU PROCESSING STATUS CHECK"
echo "======================================================================"

# Check output folder
echo ""
echo "1. OUTPUT FOLDER CHECK:"
echo "----------------------------------------------------------------------"
OUTPUT_DIR="$HOME/nerdbuntu/data/output"
if [ -d "$OUTPUT_DIR" ]; then
    MD_COUNT=$(find "$OUTPUT_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
    echo "   Location: $OUTPUT_DIR"
    echo "   Markdown files: $MD_COUNT"
    
    if [ $MD_COUNT -gt 0 ]; then
        echo ""
        echo "   Files found:"
        find "$OUTPUT_DIR" -name "*.md" -type f -exec sh -c '
            file="$1"
            name=$(basename "$file")
            size=$(du -h "$file" | cut -f1)
            mtime=$(stat -c %y "$file" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$file" 2>/dev/null)
            echo "      - $name ($size)"
            echo "        Last modified: $mtime"
        ' _ {} \;
    else
        echo "   ⚠ Folder exists but is EMPTY"
        echo "   This means processing started but didn't complete"
    fi
else
    echo "   ✗ Output directory does NOT exist: $OUTPUT_DIR"
    echo "   Processing may have never started"
fi

# Check vector database
echo ""
echo "2. VECTOR DATABASE CHECK:"
echo "----------------------------------------------------------------------"
VECTOR_DIR="$HOME/nerdbuntu/data/vector_db"
if [ -d "$VECTOR_DIR" ]; then
    SIZE=$(du -sh "$VECTOR_DIR" 2>/dev/null | cut -f1)
    FILE_COUNT=$(find "$VECTOR_DIR" -type f 2>/dev/null | wc -l)
    echo "   Location: $VECTOR_DIR"
    echo "   Size: $SIZE"
    echo "   Files: $FILE_COUNT"
    
    # Check last modified time
    if [ "$FILE_COUNT" -gt 0 ]; then
        LAST_MOD=$(find "$VECTOR_DIR" -type f -exec stat -c %y {} \; 2>/dev/null | sort -r | head -1)
        if [ -z "$LAST_MOD" ]; then
            LAST_MOD=$(find "$VECTOR_DIR" -type f -exec stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" {} \; 2>/dev/null | sort -r | head -1)
        fi
        echo "   Last modified: $LAST_MOD"
        
        # This means embeddings were generated!
        echo ""
        echo "   ✓ Vector database HAS data"
        echo "   This means embedding generation COMPLETED"
    fi
else
    echo "   ✗ Vector database does NOT exist: $VECTOR_DIR"
    echo "   Semantic processing was never started or enabled"
fi

# Check running processes
echo ""
echo "3. RUNNING PROCESSES CHECK:"
echo "----------------------------------------------------------------------"
PROCS=$(ps aux | grep -E "python.*[g]ui|python.*app\.py" 2>/dev/null)
if [ -n "$PROCS" ]; then
    echo "   ✓ Found GUI process(es) running:"
    echo "$PROCS" | while read line; do
        PID=$(echo "$line" | awk '{print $2}')
        CPU=$(echo "$line" | awk '{print $3}')
        MEM=$(echo "$line" | awk '{print $4}')
        TIME=$(echo "$line" | awk '{print $10}')
        echo "      PID: $PID | CPU: $CPU% | MEM: $MEM% | Time: $TIME"
    done
    
    # Check if process is actually doing work
    echo ""
    echo "   Checking if process is active..."
    sleep 2
    PROCS_AFTER=$(ps aux | grep -E "python.*[g]ui|python.*app\.py" 2>/dev/null)
    if [ "$PROCS" = "$PROCS_AFTER" ]; then
        echo "   ⚠ Process exists but CPU time hasn't changed"
        echo "   It might be HUNG or WAITING"
    fi
else
    echo "   ✗ No GUI processes are running"
    echo "   Processing either completed, crashed, or was never started"
fi

# Check Azure configuration
echo ""
echo "4. AZURE CONFIGURATION CHECK:"
echo "----------------------------------------------------------------------"
cd ~/nerdbuntu 2>/dev/null || cd .
if [ -f ".env" ]; then
    if grep -q "AZURE_ENDPOINT" .env && grep -q "AZURE_API_KEY" .env; then
        ENDPOINT=$(grep "AZURE_ENDPOINT" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        echo "   ✓ Azure IS configured"
        echo "   Endpoint: $ENDPOINT"
        
        # Check if semantic features were likely enabled
        echo ""
        echo "   If vector DB has data but no output files:"
        echo "   → Processing likely STUCK or CRASHED after embeddings"
    else
        echo "   ✗ Azure NOT properly configured in .env"
        echo "   Semantic features would be disabled"
    fi
else
    echo "   ✗ No .env file found"
    echo "   Processing would run in BASIC mode (no semantic features)"
fi

# Summary and diagnosis
echo ""
echo "======================================================================"
echo "DIAGNOSIS & RECOMMENDATIONS:"
echo "======================================================================"
echo ""

# Determine what happened
HAS_OUTPUT=false
HAS_VECTORS=false

if [ -d "$OUTPUT_DIR" ] && [ $(find "$OUTPUT_DIR" -name "*.md" -type f 2>/dev/null | wc -l) -gt 0 ]; then
    HAS_OUTPUT=true
fi

if [ -d "$VECTOR_DIR" ] && [ $(find "$VECTOR_DIR" -type f 2>/dev/null | wc -l) -gt 0 ]; then
    HAS_VECTORS=true
fi

if $HAS_OUTPUT && $HAS_VECTORS; then
    echo "✓✓✓ PROCESSING COMPLETED SUCCESSFULLY ✓✓✓"
    echo ""
    echo "Your files are ready:"
    echo "  - Markdown files: $OUTPUT_DIR"
    echo "  - Vector database: $VECTOR_DIR"
    echo ""
    echo "To process MORE PDFs:"
    echo "  ./launch_gui.sh"
    
elif $HAS_VECTORS && ! $HAS_OUTPUT; then
    echo "⚠⚠⚠ PROCESSING INCOMPLETE - LIKELY CRASHED ⚠⚠⚠"
    echo ""
    echo "What happened:"
    echo "  ✓ Embedding generation completed (vector DB has data)"
    echo "  ✗ Markdown files NOT created (processing stopped)"
    echo ""
    echo "This means processing crashed AFTER embedding generation"
    echo "but BEFORE writing the markdown files."
    echo ""
    echo "Possible causes:"
    echo "  1. Azure API call failed (check token usage - should be 0)"
    echo "  2. Out of memory"
    echo "  3. Disk space full"
    echo "  4. GUI was force-closed"
    echo "  5. Python crashed"
    echo ""
    echo "What to do:"
    echo "  1. Close any hung GUI windows"
    echo "  2. Kill any hung Python processes"
    echo "  3. Re-run GUI and try again: ./launch_gui.sh"
    echo "  4. Try with semantic features DISABLED (faster, simpler)"
    echo "  5. Check system resources: free -h && df -h"
    
elif ! $HAS_VECTORS && ! $HAS_OUTPUT; then
    echo "⚠⚠⚠ NO PROCESSING OUTPUT FOUND ⚠⚠⚠"
    echo ""
    echo "Possible causes:"
    echo "  1. Processing never started (didn't click Process button?)"
    echo "  2. Processing failed immediately"
    echo "  3. Wrong PDF file selected"
    echo "  4. Permission errors"
    echo ""
    echo "What to do:"
    echo "  1. Launch GUI: ./launch_gui.sh"
    echo "  2. Select a PDF file"
    echo "  3. Click 'Process PDF' button"
    echo "  4. Watch the log window for errors"
    echo "  5. Wait for 'Processing complete' message"
    
else
    echo "⚠ UNUSUAL STATE"
    echo ""
    echo "Please check the output above for details"
fi

echo ""
echo "======================================================================"
echo "For more help, check the logs or re-run with: ./launch_gui.sh"
echo "======================================================================"
