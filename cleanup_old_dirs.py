#!/usr/bin/env python3
"""
Cleanup script for old directories after reorganization
Removes empty core/ and game/ directories
"""

import os
import shutil
from pathlib import Path

def remove_directory(path):
    """Safely remove a directory"""
    if path.exists():
        try:
            shutil.rmtree(path)
            print(f"✓ Removed: {path}")
            return True
        except Exception as e:
            print(f"✗ Failed to remove {path}: {e}")
            return False
    else:
        print(f"ℹ Directory doesn't exist: {path}")
        return True

def main():
    """Main cleanup function"""
    project_root = Path(__file__).parent
    
    print("=" * 60)
    print("CLEANUP OLD DIRECTORIES")
    print("=" * 60)
    print()
    
    # Directories to remove
    old_dirs = [
        project_root / 'core',
        project_root / 'game',
        project_root / 'saves'
    ]
    
    print("The following directories will be removed:")
    for d in old_dirs:
        if d.exists():
            print(f"  - {d}")
    print()
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Aborted")
        return
    
    print()
    success_count = 0
    for directory in old_dirs:
        if remove_directory(directory):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"Cleanup complete! {success_count}/{len(old_dirs)} directories removed")
    print("=" * 60)

if __name__ == '__main__':
    main()
