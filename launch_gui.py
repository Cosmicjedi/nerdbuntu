#!/usr/bin/env python3
"""
Nerdbuntu GUI Launcher
Simple script to launch the GUI application
"""

import sys
from pathlib import Path

# Add the repository root to the path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

if __name__ == "__main__":
    from gui.app import main
    main()
