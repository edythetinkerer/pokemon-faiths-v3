"""
Import Path Updater for Pokémon Faiths
Updates all import statements after project reorganization
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict

class ImportPathUpdater:
    """Updates import statements to match new project structure"""
    
    # Map of old imports to new imports
    IMPORT_MAPPINGS = {
        # Core imports
        r'from core\.': 'from src.core.',
        r'import core\.': 'import src.core.',
        
        # Game imports
        r'from game\.': 'from src.game.',
        r'import game\.': 'import src.game.',
        
        # UI imports
        r'from ui_components import': 'from src.ui.ui_components import',
        r'import ui_components': 'import src.ui.ui_components',
        
        # Constants
        r'from constants import': 'from src.constants import',
        r'import constants': 'import src.constants',
    }
    
    def __init__(self, project_root: Path, dry_run: bool = True):
        self.root = project_root
        self.dry_run = dry_run
        self.changes = []
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in src/ directory"""
        src_dir = self.root / 'src'
        if not src_dir.exists():
            print(f"⚠️  src/ directory not found at {src_dir}")
            return []
        
        python_files = list(src_dir.rglob('*.py'))
        print(f"Found {len(python_files)} Python files to update")
        return python_files
    
    def update_file_imports(self, file_path: Path) -> int:
        """Update imports in a single file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            changes_in_file = 0
            file_changes = []
            
            # Apply each mapping
            for old_pattern, new_pattern in self.IMPORT_MAPPINGS.items():
                matches = list(re.finditer(old_pattern, content))
                if matches:
                    for match in matches:
                        old_text = match.group(0)
                        new_text = re.sub(old_pattern, new_pattern, old_text)
                        file_changes.append((old_text, new_text))
                    
                    content = re.sub(old_pattern, new_pattern, content)
                    changes_in_file += len(matches)
            
            # Check if anything changed
            if content != original_content:
                relative_path = file_path.relative_to(self.root)
                
                if self.dry_run:
                    print(f"\n📝 {relative_path}")
                    for old, new in file_changes:
                        print(f"  {old} → {new}")
                else:
                    file_path.write_text(content, encoding='utf-8')
                    print(f"✓ Updated {relative_path} ({changes_in_file} changes)")
                
                self.changes.append({
                    'file': str(relative_path),
                    'count': changes_in_file,
                    'changes': file_changes
                })
            
            return changes_in_file
            
        except Exception as e:
            print(f"✗ Error updating {file_path}: {e}")
            return 0
    
    def update_save_manager_paths(self):
        """Update path constants in save_manager.py"""
        save_manager = self.root / 'src' / 'core' / 'save_manager.py'
        
        if not save_manager.exists():
            return
        
        try:
            content = save_manager.read_text(encoding='utf-8')
            original = content
            
            # Update save directory path
            content = re.sub(
                r"SAVE_DIR = 'saves'",
                "SAVE_DIR = 'data/saves'",
                content
            )
            
            if content != original:
                if self.dry_run:
                    print(f"\n📝 src/core/save_manager.py")
                    print(f"  SAVE_DIR = 'saves' → SAVE_DIR = 'data/saves'")
                else:
                    save_manager.write_text(content, encoding='utf-8')
                    print(f"✓ Updated save_manager.py paths")
                
                self.changes.append({
                    'file': 'src/core/save_manager.py',
                    'type': 'path_update',
                    'change': 'SAVE_DIR'
                })
        
        except Exception as e:
            print(f"✗ Error updating save_manager.py: {e}")
    
    def update_asset_manager_paths(self):
        """Update base path calculation in asset_manager.py"""
        asset_manager = self.root / 'src' / 'core' / 'asset_manager.py'
        
        if not asset_manager.exists():
            return
        
        try:
            content = asset_manager.read_text(encoding='utf-8')
            original = content
            
            # Find the _get_base_path method
            old_base_path = r"""def _get_base_path\(self\) -> str:
        \"\"\"Get the correct base path for assets\"\"\"
        if getattr\(sys, 'frozen', False\):
            # Running as executable
            return sys\._MEIPASS
        else:
            # Running as script - go up one level from core/ to project root
            return os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)"""
            
            new_base_path = """def _get_base_path(self) -> str:
        \"\"\"Get the correct base path for assets\"\"\"
        if getattr(sys, 'frozen', False):
            # Running as executable
            return sys._MEIPASS
        else:
            # Running as script - go up from src/core/ to project root
            # __file__ is in src/core/, go up 2 levels
            core_dir = os.path.dirname(os.path.abspath(__file__))  # src/core/
            src_dir = os.path.dirname(core_dir)  # src/
            return os.path.dirname(src_dir)  # project root"""
            
            content = re.sub(old_base_path, new_base_path, content, flags=re.MULTILINE)
            
            if content != original:
                if self.dry_run:
                    print(f"\n📝 src/core/asset_manager.py")
                    print(f"  Updated _get_base_path() to handle src/ structure")
                else:
                    asset_manager.write_text(content, encoding='utf-8')
                    print(f"✓ Updated asset_manager.py base path")
                
                self.changes.append({
                    'file': 'src/core/asset_manager.py',
                    'type': 'path_update',
                    'change': '_get_base_path'
                })
        
        except Exception as e:
            print(f"✗ Error updating asset_manager.py: {e}")
    
    def update_main_entry_point(self):
        """Update main.py to work from src/ directory"""
        main_file = self.root / 'src' / 'main.py'
        
        if not main_file.exists():
            return
        
        try:
            content = main_file.read_text(encoding='utf-8')
            original = content
            
            # Add sys.path adjustment at the top if not already there
            if 'sys.path.insert' not in content:
                import_section = """#!/usr/bin/env python3
\"\"\"
Pokemon Faiths - Main Launcher
A dark Pokemon-style game with atmospheric storytelling
\"\"\"

import pygame
import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

"""
                # Replace the existing shebang and docstring
                content = re.sub(
                    r'^#!/usr/bin/env python3\n"""[\s\S]*?"""\n\nimport pygame\nimport sys',
                    import_section.rstrip() + '\nimport pygame\nimport sys',
                    content,
                    count=1
                )
            
            if content != original:
                if self.dry_run:
                    print(f"\n📝 src/main.py")
                    print(f"  Added sys.path adjustment for project root")
                else:
                    main_file.write_text(content, encoding='utf-8')
                    print(f"✓ Updated main.py entry point")
                
                self.changes.append({
                    'file': 'src/main.py',
                    'type': 'sys_path_update',
                    'change': 'Added project root to sys.path'
                })
        
        except Exception as e:
            print(f"✗ Error updating main.py: {e}")
    
    def create_run_script(self):
        """Create a run script in project root"""
        run_script = self.root / 'run.py'
        
        script_content = """#!/usr/bin/env python3
\"\"\"
Pokémon Faiths - Launcher Script
Run this from project root
\"\"\"

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run main
from src.main import main

if __name__ == '__main__':
    sys.exit(main())
"""
        
        if self.dry_run:
            print(f"\n📝 Would create: run.py (launcher script)")
        else:
            run_script.write_text(script_content)
            print(f"✓ Created run.py launcher script")
        
        self.changes.append({
            'file': 'run.py',
            'type': 'new_file',
            'change': 'Created launcher script'
        })
    
    def update_all(self):
        """Update all import paths in the project"""
        print("=" * 60)
        print("IMPORT PATH UPDATER")
        print("=" * 60)
        
        if self.dry_run:
            print("\n🔍 DRY RUN MODE - Showing planned changes\n")
        else:
            print("\n⚠️  LIVE MODE - Applying changes\n")
        
        # Find and update Python files
        python_files = self.find_python_files()
        total_changes = 0
        
        print("\n📦 Updating import statements...")
        for file in python_files:
            changes = self.update_file_imports(file)
            total_changes += changes
        
        # Update specific files with path changes
        print("\n🔧 Updating path configurations...")
        self.update_save_manager_paths()
        self.update_asset_manager_paths()
        self.update_main_entry_point()
        
        # Create convenience scripts
        print("\n📝 Creating helper scripts...")
        self.create_run_script()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"Total files modified: {len(self.changes)}")
        print(f"Total import changes: {total_changes}")
        
        if self.dry_run:
            print("\n✓ Dry run complete - review changes above")
            print("Run with --live to apply changes")
        else:
            print("\n✓ All imports updated successfully!")
        print("=" * 60)


def main():
    """Main entry point"""
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).parent.absolute()
    
    # Check for live mode
    dry_run = '--live' not in sys.argv
    
    if not dry_run:
        confirm = input("⚠️  This will modify Python files. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted")
            return
    
    updater = ImportPathUpdater(project_root, dry_run=dry_run)
    updater.update_all()
    
    if dry_run:
        print("\n💡 To apply changes, run:")
        print("   python update_imports.py --live")


if __name__ == '__main__':
    main()
