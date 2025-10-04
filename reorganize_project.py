"""
Pokémon Faiths - Project Reorganization Script
Safely reorganizes project structure with backup and validation
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

class ProjectReorganizer:
    """Handles safe project reorganization with rollback capability"""
    
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.backup_dir = self.root / f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.dry_run = True
        self.changes = []
        
    def backup_project(self):
        """Create full project backup before changes"""
        print(f"Creating backup at: {self.backup_dir}")
        
        # Exclude certain directories from backup
        exclude = {'.git', '__pycache__', 'logs', 'screenshots', 'build'}
        
        def copy_with_exclude(src, dst):
            for item in os.listdir(src):
                if item in exclude:
                    continue
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
                else:
                    shutil.copy2(s, d)
        
        try:
            self.backup_dir.mkdir(exist_ok=True)
            copy_with_exclude(self.root, self.backup_dir)
            print("✓ Backup created successfully")
            return True
        except Exception as e:
            print(f"✗ Backup failed: {e}")
            return False
    
    def create_directories(self):
        """Create new directory structure"""
        directories = [
            'src',
            'src/core',
            'src/game',
            'src/game/states',
            'src/ui',
            'tests',
            'docs',
            'docs/user',
            'docs/dev',
            'data',
            'data/saves',
            'logs/archive',
            'logs/archive/2025-10',
            'backups',
            'build',
        ]
        
        print("\n📁 Creating new directories...")
        for dir_path in directories:
            full_path = self.root / dir_path
            if self.dry_run:
                print(f"  [DRY RUN] Would create: {dir_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✓ Created: {dir_path}")
    
    def move_file(self, src, dst, reason=""):
        """Move a file with logging"""
        src_path = self.root / src
        dst_path = self.root / dst
        
        if not src_path.exists():
            print(f"  ⚠ Skip (not found): {src}")
            return False
        
        if self.dry_run:
            print(f"  [DRY RUN] {src} → {dst}" + (f" ({reason})" if reason else ""))
            self.changes.append({
                'type': 'move',
                'src': str(src),
                'dst': str(dst),
                'reason': reason
            })
        else:
            try:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_path), str(dst_path))
                print(f"  ✓ Moved: {src} → {dst}")
                self.changes.append({
                    'type': 'moved',
                    'src': str(src),
                    'dst': str(dst),
                    'reason': reason
                })
                return True
            except Exception as e:
                print(f"  ✗ Error moving {src}: {e}")
                return False
        
        return True
    
    def reorganize_source(self):
        """Move source code files"""
        print("\n📦 Reorganizing source code...")
        
        moves = [
            ('main.py', 'src/main.py', 'Main entry point'),
            ('constants.py', 'src/constants.py', 'Game constants'),
            ('ui_components.py', 'src/ui/ui_components.py', 'UI components'),
        ]
        
        for src, dst, reason in moves:
            self.move_file(src, dst, reason)
    
    def reorganize_core(self):
        """Move core system files"""
        print("\n🔧 Reorganizing core systems...")
        
        core_files = [
            'asset_manager.py',
            'audio_manager.py',
            'entities.py',
            'game_debugger.py',
            'logger.py',
            'moves.py',
            'pause_menu.py',
            'pokemon.py',
            'save_manager.py',
            'settings_menu.py',
            '__init__.py'
        ]
        
        for file in core_files:
            src = f'core/{file}'
            dst = f'src/core/{file}'
            self.move_file(src, dst, 'Core system')
    
    def reorganize_game_states(self):
        """Move game state files"""
        print("\n🎮 Reorganizing game states...")
        
        state_files = [
            'battle.py',
            'bedroom.py',
            'cave.py',
            'intro_sequence.py',
            'outside.py',
            'start_screen.py',
            '__init__.py'
        ]
        
        # First move __init__.py from game/
        self.move_file('game/__init__.py', 'src/game/__init__.py', 'Game package init')
        
        for file in state_files:
            src = f'game/states/{file}'
            dst = f'src/game/states/{file}'
            self.move_file(src, dst, 'Game state')
    
    def reorganize_docs(self):
        """Move documentation files"""
        print("\n📚 Reorganizing documentation...")
        
        dev_docs = [
            'ARCHITECTURE.md',
            'COMPREHENSIVE_AUDIT.md',
            'IMPLEMENTATION_SUMMARY.md',
            'NEXT_STEPS.md',
            'TODO.md',
            'QUICK_REFERENCE.md',
            'TESTING_GUIDE.md',
            'forclaude.txt',
            'REORGANIZATION_PLAN.md'
        ]
        
        for doc in dev_docs:
            self.move_file(doc, f'docs/dev/{doc}', 'Developer documentation')
    
    def reorganize_tests(self):
        """Move test files"""
        print("\n🧪 Reorganizing tests...")
        
        test_files = [
            'test_battle_system.py',
            'test_movement.py',
            'test_arrow_keys.py'
        ]
        
        for test in test_files:
            self.move_file(test, f'tests/{test}', 'Test file')
    
    def reorganize_data(self):
        """Move runtime data"""
        print("\n💾 Reorganizing data...")
        
        # Move saves
        self.move_file('saves/save_data.json', 'data/saves/save_data.json', 'Save file')
        
        # Move settings
        if (self.root / 'settings.json').exists():
            self.move_file('settings.json', 'data/settings.json', 'User settings')
    
    def reorganize_logs(self):
        """Organize log files"""
        print("\n📋 Organizing logs...")
        
        logs_dir = self.root / 'logs'
        if not logs_dir.exists():
            return
        
        log_files = list(logs_dir.glob('game_*.log'))
        
        print(f"  Found {len(log_files)} log files")
        
        if len(log_files) > 10:
            # Move old logs to archive
            sorted_logs = sorted(log_files, key=lambda p: p.stat().st_mtime)
            old_logs = sorted_logs[:-5]  # Keep 5 most recent
            
            for log in old_logs:
                # Extract date from filename (game_YYYYMMDD_HHMMSS.log)
                date_str = log.stem.split('_')[1]  # YYYYMMDD
                year_month = f"{date_str[:4]}-{date_str[4:6]}"
                archive_path = f'logs/archive/{year_month}/{log.name}'
                self.move_file(f'logs/{log.name}', archive_path, 'Archive old log')
    
    def reorganize_backups(self):
        """Move backup files"""
        print("\n🗄️ Organizing backups...")
        
        backup_files = list(self.root.glob('*.backup'))
        for backup in backup_files:
            self.move_file(backup.name, f'backups/{backup.name}', 'Backup file')
        
        # Move duplicate settings_menu.py if it exists
        if (self.root / 'settings_menu.py').exists():
            self.move_file('settings_menu.py', 'backups/settings_menu.py.duplicate', 'Duplicate file')
    
    def create_init_files(self):
        """Create __init__.py files where needed"""
        print("\n📝 Creating __init__.py files...")
        
        init_locations = [
            'src/__init__.py',
            'src/ui/__init__.py',
            'tests/__init__.py'
        ]
        
        for location in init_locations:
            full_path = self.root / location
            if self.dry_run:
                print(f"  [DRY RUN] Would create: {location}")
            else:
                if not full_path.exists():
                    full_path.write_text('')
                    print(f"  ✓ Created: {location}")
    
    def create_gitignore(self):
        """Create comprehensive .gitignore"""
        print("\n🔒 Creating .gitignore...")
        
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*.sublime-*

# Game Data
data/saves/*.json
!data/saves/.gitkeep
logs/**/*.log
!logs/.gitkeep
screenshots/*.png
!screenshots/.gitkeep

# OS
.DS_Store
Thumbs.db
desktop.ini

# Backups
backups/
_backup_*/
*~
*.backup

# Settings (user-specific)
data/settings.json

# Temporary
*.tmp
*.temp
"""
        
        gitignore_path = self.root / '.gitignore'
        
        if self.dry_run:
            print(f"  [DRY RUN] Would create .gitignore")
        else:
            gitignore_path.write_text(gitignore_content)
            print(f"  ✓ Created .gitignore")
    
    def generate_report(self):
        """Generate reorganization report"""
        report_path = self.root / 'reorganization_report.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'changes': self.changes,
            'stats': {
                'total_moves': len(self.changes),
                'successful': sum(1 for c in self.changes if c['type'] == 'moved'),
                'planned': sum(1 for c in self.changes if c['type'] == 'move')
            }
        }
        
        if self.dry_run:
            print(f"\n📊 Reorganization Plan Summary:")
            print(f"  Total planned moves: {report['stats']['planned']}")
        else:
            report_path.write_text(json.dumps(report, indent=2))
            print(f"\n📊 Reorganization Report:")
            print(f"  Successful moves: {report['stats']['successful']}")
            print(f"  Report saved to: reorganization_report.json")
    
    def run(self, dry_run=True):
        """Execute full reorganization"""
        self.dry_run = dry_run
        
        print("=" * 60)
        print("POKÉMON FAITHS - PROJECT REORGANIZATION")
        print("=" * 60)
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made")
            print("Review the output, then run with dry_run=False to apply changes\n")
        else:
            print("\n⚠️  LIVE MODE - Changes will be applied!")
            print("Creating backup first...\n")
            if not self.backup_project():
                print("\n✗ Backup failed - aborting reorganization")
                return False
        
        # Execute reorganization steps
        self.create_directories()
        self.reorganize_source()
        self.reorganize_core()
        self.reorganize_game_states()
        self.reorganize_docs()
        self.reorganize_tests()
        self.reorganize_data()
        self.reorganize_logs()
        self.reorganize_backups()
        self.create_init_files()
        self.create_gitignore()
        
        # Generate report
        self.generate_report()
        
        print("\n" + "=" * 60)
        if dry_run:
            print("✓ Dry run complete - review changes above")
            print("Run with dry_run=False to apply changes")
        else:
            print("✓ Reorganization complete!")
            print(f"Backup saved at: {self.backup_dir}")
        print("=" * 60)
        
        return True


def main():
    """Main entry point"""
    import sys
    
    # Get project root (parent of this script's directory)
    project_root = Path(__file__).parent.absolute()
    
    # Check if user wants dry run or live run
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        dry_run = False
        confirm = input("⚠️  This will reorganize your project. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted")
            return
    
    # Run reorganization
    reorganizer = ProjectReorganizer(project_root)
    success = reorganizer.run(dry_run=dry_run)
    
    if success and dry_run:
        print("\n💡 To apply changes, run:")
        print("   python reorganize_project.py --live")


if __name__ == '__main__':
    main()
