#!/usr/bin/env python3
"""
Launch script for ChromaDB to Qdrant Migration GUI
"""

import sys
from pathlib import Path

# Add gui directory to path
gui_dir = Path(__file__).parent / "gui"
sys.path.insert(0, str(gui_dir))

from migration_gui import main

if __name__ == "__main__":
    main()
