#!/usr/bin/env python3
"""
Pokémon Faiths - Launcher Script
Run this from project root after reorganization
"""

import sys
import os
from pathlib import Path

# Ensure we're in the correct working directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

# Add src/ directory to Python path
src_dir = script_dir / 'src'
sys.path.insert(0, str(src_dir))

# Import and run main
from main import main

if __name__ == '__main__':
    sys.exit(main())
