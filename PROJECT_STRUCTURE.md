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
├── configure_azure.py      # Auto-configure Azure OpenAI
├── configure_azure.sh      # Azure config wrapper script
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

# Skip Azure configuration for now (basic mode works without it)
```

### 2. Configure Azure (Optional - For AI Features)

**Option A: Automatic Configuration (Recommended)**
```bash
# Make the script executable
chmod +x configure_azure.sh

# Run the auto-configuration
./configure_azure.sh
```

This script will:
- Connect to your Azure account
- Find your Azure OpenAI resources
- Discover your model deployments
- Generate the correct .env file automatically

**Option B: Manual Configuration**
```bash
# Copy environment template
cp .env.template .env
# Edit .env with your Azure credentials
```

### 3. Launch the GUI

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

### 4. Use CLI Examples

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

### Configuration Tools
- **configure_azure.py**: Python script that auto-discovers Azure OpenAI configuration
- **configure_azure.sh**: Bash wrapper for the configuration script

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

### "MissingDependencyException with missing pdfconverter"
```bash
# Reinstall with all PDF dependencies
pip install --upgrade "markitdown[all]"
```

### "Azure credentials not found" or "404 resource not found"
**Option 1: Use Basic Mode (No Azure Needed)**
- Just uncheck the Azure options in the GUI
- PDF conversion works perfectly without Azure!

**Option 2: Fix Azure Configuration**
```bash
# Run the auto-configuration script
./configure_azure.sh
```

Or see `AZURE_SETUP.md` for manual configuration.

### GUI won't launch
```bash
# Make sure tkinter is installed
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo yum install python3-tkinter  # RedHat/CentOS

# Verify virtual environment is activated
source venv/bin/activate

# Launch GUI
python3 launch_gui.py
```

### "Command not found: ./configure_azure.sh"
```bash
# Make the script executable
chmod +x configure_azure.sh

# Then run it
./configure_azure.sh
```

## 📝 Azure Configuration

### Prerequisites for Azure Auto-Configuration
1. **Azure CLI** must be installed
   ```bash
   # Ubuntu/Debian
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # macOS
   brew install azure-cli
   ```

2. **Azure OpenAI Resource** must exist in your subscription
   - Create one at https://portal.azure.com if needed

3. **Model Deployment** must be created
   - In Azure Portal → Your OpenAI Resource → Model deployments

### Running Auto-Configuration
```bash
./configure_azure.sh
```

The script will:
1. Check Azure CLI installation
2. Log you into Azure (if needed)
3. Find all your Azure OpenAI resources
4. Let you select which one to use
5. Find all model deployments
6. Let you select which deployment to use
7. Automatically generate the .env file with correct settings

## 📚 Documentation

- **INSTALLATION.md** - Complete installation guide with troubleshooting
- **AZURE_SETUP.md** - Detailed Azure configuration guide
- **REORGANIZATION_SUMMARY.md** - Summary of recent changes
- **PROJECT_STRUCTURE.md** - This file

## 📝 Migration Notes

If you're updating from an older version:
- Old `app.py` now redirects to new structure
- Core functionality moved to `core/semantic_linker.py`
- GUI moved to `gui/app.py`
- All old scripts still work for backward compatibility
- New Azure auto-configuration available

## 🎯 Two Operating Modes

**Basic Mode** (No Azure Required):
- ✓ PDF to Markdown conversion
- ✓ File conversion
- ✓ Fast and free

**Semantic Mode** (Requires Azure OpenAI):
- ✓ Everything in Basic Mode
- ✓ AI-powered key concept extraction
- ✓ Semantic backlinking
- ✓ Vector database storage
- ⚠ Requires Azure subscription (paid)

Choose the mode that fits your needs!
