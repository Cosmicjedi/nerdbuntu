# Bulk Processing Guide

Complete guide for processing multiple PDFs at once using Nerdbuntu's bulk directory processing feature.

## 🎯 Overview

Nerdbuntu GUI now supports two processing modes:

1. **Single File Mode** - Process one PDF at a time (original functionality)
2. **Bulk Directory Mode** - Process all PDFs in a directory automatically (NEW!)

## 🚀 Quick Start

### Single File Processing

1. Launch the GUI: `./launch_gui.sh` or `python launch_gui.py`
2. Select "Single File - Process one PDF file" mode
3. Click "Browse File" and select your PDF
4. Click "Process PDF File"

### Bulk Directory Processing

1. Launch the GUI: `./launch_gui.sh` or `python launch_gui.py`
2. Select "Bulk Directory - Process all PDFs in a directory" mode
3. Click "Browse Directory" and select folder containing PDFs
4. (Optional) Customize the file pattern (default: `*.pdf`)
5. Click "Process All PDFs in Directory"
6. Confirm the number of files found
7. Wait for processing to complete

## 📋 Features

### Bulk Processing Features

✅ **Automatic File Discovery**
- Finds all PDFs matching your pattern
- Supports wildcards (e.g., `report_*.pdf`)
- Recursive directory search option

✅ **Smart Skip Logic**
- Automatically skips files with existing output
- Prevents duplicate processing
- Saves time on re-runs

✅ **Progress Tracking**
- Shows current file being processed
- Displays running count (e.g., "Processing 5/20")
- Real-time log updates

✅ **Detailed Statistics**
- Total files found
- Successfully processed
- Failed conversions
- Skipped files
- Summary at completion

✅ **Error Handling**
- Continues processing even if one file fails
- Logs all errors for review
- Final summary shows all failures

## 🎨 File Pattern Examples

The file pattern determines which files to process:

### Common Patterns

```
*.pdf                    # All PDF files
report_*.pdf            # Files starting with "report_"
*_2024.pdf              # Files ending with "_2024"
monthly_report_*.pdf    # Specific prefix
[0-9]*.pdf              # Files starting with a number
```

### Advanced Patterns

```
chapter[1-5].pdf        # chapter1.pdf through chapter5.pdf
section_??.pdf          # section_01.pdf, section_99.pdf, etc.
```

## 📊 Processing Options

### Skip Existing Files

**Enabled (Default):**
- Skips files where output `.md` already exists
- Useful for resuming interrupted batch jobs
- Prevents overwriting existing work

**Disabled:**
- Processes all files regardless of existing output
- Overwrites existing `.md` files
- Use when you want to re-process everything

### Semantic Processing

**Enabled (requires Azure AI):**
- Adds AI-powered features to all files
- Generates semantic backlinks
- Extracts key concepts
- Much slower (1-2 min per file)

**Disabled:**
- Fast basic conversion only
- No AI features
- Good for large batches

## 🔄 Workflow Examples

### Example 1: Process All PDFs in Downloads

```
1. Select "Bulk Directory" mode
2. Browse to ~/Downloads
3. Pattern: *.pdf
4. Enable "Skip existing files"
5. Click "Process All PDFs"
6. Result: All PDFs converted to markdown
```

### Example 2: Process Specific Report Series

```
1. Select "Bulk Directory" mode
2. Browse to ~/Documents/Reports/2024
3. Pattern: monthly_*.pdf
4. Disable "Skip existing files" (re-process)
5. Enable semantic processing
6. Click "Process All PDFs"
7. Result: All monthly reports with AI features
```

### Example 3: Resume Interrupted Job

```
Scenario: You processed 50 of 100 files, then stopped

1. Select "Bulk Directory" mode
2. Browse to same directory
3. Pattern: *.pdf
4. Keep "Skip existing files" ENABLED
5. Click "Process All PDFs"
6. Result: Only the remaining 50 files are processed
```

### Example 4: Fast Batch Conversion (No AI)

```
Scenario: Convert 500 PDFs quickly

1. Select "Bulk Directory" mode
2. Browse to directory with PDFs
3. Pattern: *.pdf
4. DISABLE semantic processing
5. Enable "Skip existing files"
6. Click "Process All PDFs"
7. Result: Fast conversion, ~10-30 sec per file
```

## 📈 Performance

### Processing Speed

| Mode | Speed per File | Use Case |
|------|---------------|----------|
| Basic (no AI) | 10-30 seconds | Large batches, documentation |
| Semantic (with AI) | 1-3 minutes | Research papers, RAG systems |

### Batch Size Recommendations

| Files | Recommended Approach |
|-------|---------------------|
| 1-10 | Either mode, semantic OK |
| 10-50 | Bulk mode, consider basic |
| 50-100 | Bulk mode, basic recommended |
| 100+ | Bulk mode, basic only, run overnight |

## 🎯 Best Practices

### Before Starting

1. **Organize your PDFs**
   - Put related PDFs in same directory
   - Use consistent naming (helps with patterns)
   - Remove any non-PDF files if using `*` pattern

2. **Test with small batch**
   - Process 2-3 files first
   - Verify output quality
   - Then run full batch

3. **Check disk space**
   - Markdown files are usually smaller than PDFs
   - Vector DB can be large if using semantic mode
   - Ensure adequate space in output directory

### During Processing

1. **Don't close the application**
   - Let it run to completion
   - Progress is shown in real-time
   - Can take hours for large batches

2. **Monitor the log**
   - Watch for repeated errors
   - Check if files are being skipped as expected
   - Look for any warnings

3. **Be patient**
   - Semantic processing is slow (embedding generation)
   - Each file shows progress
   - Final summary shows completion

### After Processing

1. **Review the summary**
   - Check number of successful conversions
   - Note any failures
   - Review skipped files

2. **Spot-check outputs**
   - Open a few random `.md` files
   - Verify formatting looks good
   - Check semantic links if enabled

3. **Handle failures**
   - Review error messages in log
   - Try processing failed files individually
   - Check if source PDFs are corrupted

## 🐛 Troubleshooting

### Issue: No files found

**Cause:** Pattern doesn't match any files

**Solution:**
- Check the file pattern syntax
- Verify you're in the correct directory
- Try broader pattern (e.g., `*.pdf`)
- Ensure files have `.pdf` extension

### Issue: All files skipped

**Cause:** Output files already exist

**Solution:**
- Disable "Skip existing files" option
- Or delete existing output files first
- Or use a different output directory

### Issue: Processing very slow

**Cause:** Semantic processing enabled

**Solution:**
- Disable semantic processing for speed
- Process smaller batches
- Run overnight for large sets
- Use faster machine if available

### Issue: Some files failed

**Cause:** Various (corrupted PDFs, special formatting, etc.)

**Solution:**
- Review error messages in log
- Try processing failed files individually
- Check if source PDF opens normally
- Some PDFs may be image-only (OCR needed)

### Issue: Out of memory

**Cause:** Too many large PDFs at once

**Solution:**
- Process in smaller batches
- Close other applications
- Disable semantic processing
- Increase system RAM if possible

## 📊 Sample Output Log

```
[14:30:15] ============================================================
[14:30:15] BULK PROCESSING MODE
[14:30:15] Total files: 25
[14:30:15] Input directory: /home/user/Documents/Reports
[14:30:15] Output directory: /home/user/nerdbuntu/data/output
[14:30:15] ============================================================
[14:30:15] 
[14:30:15] 📄 File 1/25: annual_report_2023.pdf
[14:30:16] Step 1: Converting PDF to Markdown...
[14:30:18] ✓ PDF converted successfully (45823 characters)
[14:30:18] Step 2: Skipping semantic processing (not enabled)
[14:30:18] Step 3: Writing output file...
[14:30:18] ✓ File written successfully: annual_report_2023.md
[14:30:18]   File size: 45,823 bytes
[14:30:18] Step 4: Verifying completion...
[14:30:18] ✓ Output file verified on disk
[14:30:18]   ✅ Success: annual_report_2023.md
[14:30:18] 
[14:30:18] 📄 File 2/25: quarterly_q1.pdf
[14:30:18]   ⏭️  Skipping (output already exists): quarterly_q1.md
[14:30:18] 
[14:30:18] 📄 File 3/25: quarterly_q2.pdf
...
[14:35:42] ============================================================
[14:35:42] BULK PROCESSING COMPLETE
[14:35:42] Total files: 25
[14:35:42] Processed: 23
[14:35:42] Successful: 22
[14:35:42] Failed: 1
[14:35:42] Skipped: 2
[14:35:42] ============================================================
```

## 🔄 Comparison: Single vs Bulk Mode

| Feature | Single File | Bulk Directory |
|---------|-------------|----------------|
| Files per run | 1 | Unlimited |
| File selection | Browse one file | Browse directory |
| Pattern matching | N/A | Yes (`*.pdf`) |
| Skip existing | N/A | Yes (optional) |
| Progress tracking | Per-file steps | Per-file + overall |
| Error handling | Stop on error | Continue on error |
| Summary stats | N/A | Yes (detailed) |
| Use case | Individual files | Batch processing |

## 💡 Tips & Tricks

### Tip 1: Organize by Date

```
2024/
  01_January/
    *.pdf
  02_February/
    *.pdf
  ...
```

Process each month's directory separately for easier management.

### Tip 2: Use Descriptive Patterns

Instead of processing all files, use patterns:
- `invoice_*.pdf` - Only invoices
- `*_final.pdf` - Only final versions
- `report_2024_*.pdf` - Specific year

### Tip 3: Test Before Full Run

```
1. Copy 5 sample files to test directory
2. Run bulk processing on test directory
3. Verify output quality
4. Then process main directory
```

### Tip 4: Schedule Large Batches

For 100+ files:
```
1. Start processing in the evening
2. Let it run overnight
3. Review results in the morning
```

### Tip 5: Create Output Subdirectories

Organize outputs by source:
- Input: `~/Documents/Reports/2024/`
- Output: `~/nerdbuntu/data/output/reports_2024/`

## 🎓 Advanced Usage

### Processing Nested Directories

To process PDFs in subdirectories:

```bash
# Create a script to process multiple directories
for dir in ~/Documents/Reports/*/; do
    python gui/app.py "$dir"
done
```

### Custom Processing Pipeline

Combine with other tools:

```bash
# Convert PDFs
./launch_gui.sh  # Process in bulk mode

# Then organize outputs
./organize_outputs.sh

# Then backup
./backup_vector_db.sh
```

## 📞 Support

### Common Questions

**Q: Can I process different file types?**  
A: Yes, change pattern to `*.docx` or `*.pptx` etc.

**Q: Can I cancel a bulk job?**  
A: Yes, close the window. Already processed files are saved.

**Q: Does it preserve directory structure?**  
A: No, all outputs go to single output directory.

**Q: Can I process PDFs in nested folders?**  
A: Not in GUI. Use command line tools for recursive processing.

### Getting Help

- Check the log for error details
- Try processing failed files individually
- Consult main README.md
- Open GitHub issue with log excerpt

---

**Last Updated:** October 2025  
**Feature Added:** Bulk Directory Processing v1.0  
**GUI Version:** 2.0
