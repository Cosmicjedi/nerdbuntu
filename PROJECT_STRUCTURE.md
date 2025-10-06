# Nerdbuntu - Project Structure

## 📁 Directory Structure

```
nerdbuntu/
├── core/                    # Core functionality modules
│   ├── __init__.py
│   └── semantic_linker.py  # Semantic analysis and backlinking
├── gui/                     # GUI application
│   ├── __init__.py
│   └── app.py              # Main GUI application
├── launch_gui.py           # Python GUI launcher
├── launch_gui.sh           # Bash GUI launcher (Linux/Mac)
├── app.py                  # Legacy redirect (for backward compatibility)
├── examples.py             # CLI usage examples
├── setup.sh                # Setup script
├── requirements.txt        # Python dependencies
└── .env.template          # Environment configuration template
```

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Run the setup script
./setup.sh

# Copy environment template and configure
cp .env.template .env
# Edit .env with your Azure credentials
```

### 2. Launch the GUI

**Option 1: Using bash script (recommended for Linux/Mac)**
```bash
./launch_gui.sh
```

**Option 2: Using Python directly**
```bash
python3 launch_gui.py
```

**Option 3: Legacy method (still works)**
```bash
python3 app.py
```

### 3. Use CLI Examples

**Batch process PDFs:**
```bash
python3 examples.py batch /path/to/input/dir /path/to/output/dir
```

**Query the vector database:**
```bash
python3 examples.py query "search term"
```

## 📦 Components

### Core Module (`core/`)
Contains the business logic and core functionality:
- **semantic_linker.py**: Handles semantic analysis, embeddings, and vector database operations

### GUI Module (`gui/`)
Contains the graphical user interface:
- **app.py**: Tkinter-based GUI for PDF to Markdown conversion

### Launcher Scripts
- **launch_gui.py**: Cross-platform Python launcher
- **launch_gui.sh**: Bash launcher with environment checks

### CLI Tools
- **examples.py**: Command-line interface for batch processing and queries

## 🔧 Development

### Import Structure
When developing, import from the organized modules:

```python
# Import core functionality
from core.semantic_linker import SemanticLinker

# Import GUI components (if needed)
from gui.app import NerdbuntuApp
```

### Adding New Features
1. Core logic → Add to `core/` directory
2. GUI features → Add to `gui/` directory
3. CLI tools → Create new scripts in root or update `examples.py`

## 🐛 Troubleshooting

### "No module named dotenv"
```bash
pip install python-dotenv
# Or install all dependencies:
pip install -r requirements.txt
```

### "Azure credentials not found"
1. Check if `.env` file exists in project root
2. Ensure `AZURE_ENDPOINT` and `AZURE_API_KEY` are set
3. Copy from `.env.template` if needed

### GUI won't launch
1. Ensure virtual environment is activated
2. Run `./setup.sh` to reinstall dependencies
3. Check Python 3 is installed: `python3 --version`

## 📝 Migration Notes

If you're updating from an older version:
- Old `app.py` now redirects to new structure
- Core functionality moved to `core/semantic_linker.py`
- GUI moved to `gui/app.py`
- All old scripts still work for backward compatibility
