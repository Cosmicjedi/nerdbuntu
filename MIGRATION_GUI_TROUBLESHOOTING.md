# Migration GUI Troubleshooting

Common issues and solutions for the ChromaDB to Qdrant Migration GUI.

## Package Detection Issues

### Issue: "chromadb not installed" but it is installed

**Cause**: The launcher script is not using the correct Python environment.

**Solutions**:

#### Solution 1: Run from the nerdbuntu directory with virtual environment

```bash
cd ~/nerdbuntu
source venv/bin/activate
./launch_migration_gui.sh
```

#### Solution 2: Check if packages are installed in the venv

```bash
cd ~/nerdbuntu
source venv/bin/activate
python -c "import chromadb; print('ChromaDB OK')"
python -c "import qdrant_client; print('Qdrant Client OK')"
python -c "import sentence_transformers; print('Sentence Transformers OK')"
```

If any fail, install them:

```bash
pip install chromadb qdrant-client sentence-transformers
```

#### Solution 3: Reinstall all dependencies

```bash
cd ~/nerdbuntu
source venv/bin/activate
pip install -r requirements.txt
```

#### Solution 4: Run setup script again

```bash
cd ~/nerdbuntu
./setup.sh
```

### Issue: "tkinter not available"

**Cause**: Tkinter is a system package, not a Python package.

**Solution for Ubuntu/Debian**:

```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**Solution for macOS**:

Tkinter should be included with Python. If not:
1. Download Python from python.org
2. Run the installer
3. Make sure "tcl/tk" is selected during installation

**Solution for Windows**:

Reinstall Python from python.org and ensure "tcl/tk and IDLE" is checked.

## Python Environment Issues

### Issue: Script uses wrong Python version

**Check which Python is being used**:

```bash
which python3
python3 --version
```

**If you have multiple Python versions**, specify the correct one:

```bash
cd ~/nerdbuntu
python3.10 launch_migration_gui.py
# or
python3.11 launch_migration_gui.py
```

### Issue: Virtual environment not activating

**Manual activation**:

```bash
cd ~/nerdbuntu
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

**Verify activation**:

```bash
which python  # Should show path in venv
pip list | grep chromadb  # Should show chromadb
```

## Import Errors

### Issue: "ModuleNotFoundError: No module named 'chromadb'"

**Quick fix**:

```bash
cd ~/nerdbuntu
source venv/bin/activate
pip install chromadb
./launch_migration_gui.sh
```

### Issue: "ModuleNotFoundError: No module named 'qdrant_client'"

**Quick fix**:

```bash
cd ~/nerdbuntu
source venv/bin/activate
pip install qdrant-client
./launch_migration_gui.sh
```

### Issue: "ModuleNotFoundError: No module named 'sentence_transformers'"

**Quick fix**:

```bash
cd ~/nerdbuntu
source venv/bin/activate
pip install sentence-transformers
./launch_migration_gui.sh
```

## GUI Launch Issues

### Issue: GUI window doesn't appear

**Check for errors**:

```bash
cd ~/nerdbuntu
source venv/bin/activate
python launch_migration_gui.py 2>&1 | tee gui_error.log
```

**Common causes**:
1. Display not available (SSH without X11 forwarding)
2. Tkinter not installed
3. Python error in the code

**For SSH users**:

```bash
# Enable X11 forwarding
ssh -X user@host

# Or use VNC/remote desktop instead
```

### Issue: GUI crashes immediately

**Check Python version**:

```bash
python3 --version  # Needs 3.8 or higher
```

**Check for conflicts**:

```bash
cd ~/nerdbuntu
source venv/bin/activate
python -c "from gui.migration_gui import main; main()"
```

## Runtime Errors

### Issue: "No such file or directory" errors in GUI

**Cause**: Running from wrong directory.

**Solution**:

```bash
cd ~/nerdbuntu  # Must be in nerdbuntu directory
./launch_migration_gui.sh
```

### Issue: Cannot save configuration

**Check permissions**:

```bash
ls -la ~/.nerdbuntu_migration_config.json
# Should be writable by your user

# If it doesn't exist, the GUI will create it
# If it exists but isn't writable:
chmod 644 ~/.nerdbuntu_migration_config.json
```

## Export/Import Errors

### Issue: "ChromaDB not found" during export

**Check ChromaDB path**:

```bash
ls ~/nerdbuntu/data/vector_db/
# Should contain chroma.sqlite3 and other files
```

**If empty**, you need to process some PDFs first:

```bash
cd ~/nerdbuntu
./launch_gui.sh
# Process some PDFs with semantic processing enabled
```

### Issue: "Cannot connect to Qdrant" during import

**Check if Qdrant is running**:

```bash
docker ps | grep qdrant
# Should show a running container
```

**If not running**:

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

**Test connection manually**:

```bash
curl http://localhost:6333/
# Should return Qdrant version info
```

## Complete Reinstall

If all else fails, here's a complete clean reinstall:

```bash
# 1. Backup your data
cd ~/nerdbuntu
cp -r data data_backup
cp -r exports exports_backup

# 2. Remove virtual environment
rm -rf venv

# 3. Run setup again
./setup.sh

# 4. Verify packages
source venv/bin/activate
pip list | grep -E "chromadb|qdrant|sentence"

# 5. Try launching
./launch_migration_gui.sh
```

## Manual Launch (Bypass Script)

If the shell script continues to have issues:

```bash
cd ~/nerdbuntu
source venv/bin/activate
python launch_migration_gui.py
```

Or directly:

```bash
cd ~/nerdbuntu
source venv/bin/activate
python -m gui.migration_gui
```

## Getting Debug Information

Create a debug report to share when asking for help:

```bash
cd ~/nerdbuntu

echo "=== System Info ===" > debug_report.txt
uname -a >> debug_report.txt
python3 --version >> debug_report.txt

echo -e "\n=== Python Packages ===" >> debug_report.txt
source venv/bin/activate
pip list | grep -E "chromadb|qdrant|sentence|tkinter" >> debug_report.txt

echo -e "\n=== ChromaDB Status ===" >> debug_report.txt
ls -lh data/vector_db/ >> debug_report.txt

echo -e "\n=== Virtual Environment ===" >> debug_report.txt
ls -lh venv/bin/ | head -n 20 >> debug_report.txt

echo -e "\n=== Import Test ===" >> debug_report.txt
python -c "
try:
    import chromadb
    print('✅ chromadb imported')
except Exception as e:
    print(f'❌ chromadb error: {e}')

try:
    import qdrant_client
    print('✅ qdrant_client imported')
except Exception as e:
    print(f'❌ qdrant_client error: {e}')

try:
    import sentence_transformers
    print('✅ sentence_transformers imported')
except Exception as e:
    print(f'❌ sentence_transformers error: {e}')

try:
    import tkinter
    print('✅ tkinter imported')
except Exception as e:
    print(f'❌ tkinter error: {e}')
" >> debug_report.txt

cat debug_report.txt
```

## Common Questions

**Q: Do I need to run setup.sh again?**

Not usually. Just activate the venv and install missing packages. Only run setup.sh if you want a fresh start.

**Q: Can I use the CLI tools instead of the GUI?**

Yes! The CLI tools work independently:

```bash
cd ~/nerdbuntu
source venv/bin/activate

# Export
python export_to_qdrant.py

# Import
python import_to_qdrant.py --json-file exports/qdrant/TIMESTAMP/export.json
```

**Q: Why does it say tkinter is missing when I can import it?**

The check script might be checking the wrong Python. Try running the GUI directly:

```bash
cd ~/nerdbuntu
source venv/bin/activate
python launch_migration_gui.py
```

## Still Having Issues?

1. **Check the main documentation**: [MIGRATION_GUI_GUIDE.md](MIGRATION_GUI_GUIDE.md)
2. **Try CLI tools**: They don't require tkinter
3. **Create an issue**: Include your debug_report.txt
4. **Discord/Forum**: Share your issue with the community

---

**Last Updated**: October 2024
