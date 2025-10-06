#!/usr/bin/env python3
"""
Nerdbuntu - Legacy app.py redirect
This file redirects to the new GUI launcher for backward compatibility
"""

import sys
from pathlib import Path

print("=" * 70)
print("NOTICE: app.py has been reorganized!")
print("=" * 70)
print()
print("The GUI has been moved to: gui/app.py")
print("Core functionality is now in: core/semantic_linker.py")
print()
print("To launch the GUI, use one of these methods:")
print("  1. Run: python3 launch_gui.py")
print("  2. Run: ./launch_gui.sh (Linux/Mac)")
print("  3. For CLI examples: python3 examples.py")
print()
print("Launching GUI now...")
print("=" * 70)
print()

# Redirect to the new launcher
if __name__ == "__main__":
    from gui.app import main
    main()
