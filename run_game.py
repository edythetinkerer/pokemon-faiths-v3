#!/usr/bin/env python3
"""
Pokémon Faiths - New Launcher Script
Specifically designed to work when double-clicked
"""

import sys
import os
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent.absolute()

# Change to the script directory (project root)
os.chdir(script_dir)

# Add src/ directory to Python path
src_dir = script_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Print debug info
print(f"Script directory: {script_dir}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path includes: {src_dir}")
print(f"Assets directory exists: {(script_dir / 'assets').exists()}")

try:
    # Import and run main
    from main import main
    print("Successfully imported main module")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Available files in src/:")
    src_files = list((script_dir / 'src').glob('*.py'))
    for f in src_files:
        print(f"  - {f.name}")
    input("Press Enter to exit...")
    sys.exit(1)
    
except Exception as e:
    print(f"Error importing game: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

# Run the game
if __name__ == '__main__':
    try:
        print("Starting game...")
        sys.exit(main())
    except Exception as e:
        print(f"Error starting game: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
