# 🚀 Project Reorganization Guide

## 📋 Overview

This guide walks you through safely reorganizing your Pokémon Faiths project into a clean, professional structure.

**Time Required:** ~1 hour  
**Risk Level:** Low (full backup created)  
**Recommended When:** After wild encounters are working

---

## 🎯 What You'll Get

**Before (Current):**
```
Faith/
├── 15+ docs in root (messy!)
├── test_*.py scattered
├── core/ mixed with root files
├── 80+ logs cluttering logs/
└── Duplicate/backup files everywhere
```

**After (Clean):**
```
Faith/
├── README.md (user docs)
├── run.py (easy launcher)
├── src/ (all source code)
├── docs/ (organized by user/dev)
├── tests/ (all tests together)
├── data/ (saves, settings)
└── .gitignore (proper exclusions)
```

---

## ⚠️ IMPORTANT: When to Reorganize

### ✅ Good Time to Reorganize:
- After wild encounters are implemented
- When code is stable and tested
- Before adding more contributors
- When you need better organization

### ❌ Bad Time to Reorganize:
- **Right now** (only 2 days into dev!)
- When actively debugging
- During major feature work
- When you're about to push changes

**Recommendation:** Wait until after wild encounters work, then reorganize.

---

## 🛠️ Tools Provided

### 1. `reorganize_project.py`
**What it does:**
- Creates new directory structure
- Moves files to correct locations
- Organizes logs into archive
- Moves backups to dedicated folder
- Creates .gitignore
- Generates detailed report

**Safety features:**
- Full project backup before changes
- Dry-run mode (test first)
- Detailed logging of all moves
- Rollback from backup if needed

### 2. `update_imports.py`
**What it does:**
- Updates all `from core.` → `from src.core.`
- Updates all `from game.` → `from src.game.`
- Fixes path constants in save_manager.py
- Fixes asset path calculation
- Creates run.py launcher
- Generates change report

**Safety features:**
- Dry-run mode to preview
- Backups before changes
- Per-file change tracking
- Can be reverted

---

## 📖 Step-by-Step Instructions

### Step 0: Backup First! (CRITICAL)
```bash
# Manual backup - do this no matter what!
cd C:\Users\edy\Desktop
xcopy Faith Faith_backup_manual /E /I /H

# Or create a ZIP
# Right-click Faith folder → Send to → Compressed folder
```

---

### Step 1: Test Reorganization (Dry Run)

```bash
cd C:\Users\edy\Desktop\Faith

# Run in dry-run mode (no changes made)
python reorganize_project.py
```

**What to look for:**
- ✅ All files found correctly
- ✅ Destinations make sense
- ✅ No errors or warnings
- ✅ Log output looks reasonable

**Review the output carefully!** Make sure:
- Important files aren't being deleted
- Paths look correct
- Nothing unexpected

---

### Step 2: Apply Reorganization (Live Run)

```bash
# Apply changes (creates backup automatically)
python reorganize_project.py --live

# Type 'yes' when prompted
```

**This will:**
1. Create timestamped backup folder
2. Create new directory structure
3. Move all files to new locations
4. Organize logs into archives
5. Create .gitignore
6. Generate reorganization_report.json

**Time:** ~30 seconds

---

### Step 3: Test Import Updates (Dry Run)

```bash
# Preview import changes (no modifications)
python update_imports.py
```

**What to look for:**
- ✅ Import statements found in all files
- ✅ Replacements look correct
- ✅ Path updates make sense
- ✅ No unexpected changes

---

### Step 4: Apply Import Updates (Live Run)

```bash
# Update all imports
python update_imports.py --live

# Type 'yes' when prompted
```

**This will:**
1. Update imports in all Python files
2. Fix save_manager.py paths
3. Fix asset_manager.py paths
4. Update main.py entry point
5. Create run.py launcher

**Time:** ~10 seconds

---

### Step 5: Test the Game!

```bash
# Try the new launcher
python run.py

# Or run main.py directly
python src/main.py
```

**Test checklist:**
- [ ] Game launches without errors
- [ ] Assets load correctly
- [ ] Can create new game
- [ ] Can load existing save
- [ ] Can move player
- [ ] Can interact with objects
- [ ] Teleport between rooms works
- [ ] Pause menu works
- [ ] Settings menu works
- [ ] Game saves correctly
- [ ] Logs are written to logs/

**If anything breaks, see "Rollback" section below.**

---

### Step 6: Clean Up Old Directories

```bash
# After confirming everything works, remove old empty directories

# Remove old core/ if now empty
rmdir core  # Windows
rm -rf core  # Linux/Mac

# Remove old game/ if now empty
rmdir game /s /q  # Windows
rm -rf game  # Linux/Mac

# Remove old saves/ if now empty
rmdir saves  # Windows
rm -rf saves  # Linux/Mac
```

**Only do this after testing!**

---

## 🔄 Rollback Procedure

### If Something Goes Wrong:

**Option 1: Use Auto-Backup**
```bash
# Find the backup folder (will be named _backup_YYYYMMDD_HHMMSS)
dir | findstr backup  # Windows
ls | grep backup  # Linux/Mac

# Copy everything back from backup
xcopy _backup_20241003_120000 . /E /I /H /Y  # Windows (example)
cp -r _backup_20241003_120000/* .  # Linux/Mac
```

**Option 2: Use Manual Backup**
```bash
# Restore from your manual backup
cd C:\Users\edy\Desktop
rmdir Faith /s /q  # Windows - CAREFUL!
xcopy Faith_backup_manual Faith /E /I /H

# Or restore from ZIP
# Extract Faith_backup.zip to overwrite
```

---

## 📊 After Reorganization

### New Workflow

**Running the game:**
```bash
python run.py
# or
python src/main.py
```

**Running tests:**
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_battle_system.py
```

**Viewing docs:**
```bash
# User docs
cat README.md

# Dev docs
cat docs/dev/QUICK_REFERENCE.md
cat docs/dev/TODO.md
```

**Finding files:**
```
Source code → src/
Documentation → docs/
Tests → tests/
Saves → data/saves/
Logs → logs/
Screenshots → screenshots/
```

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'core'"
**Cause:** Imports not updated  
**Fix:** Run `python update_imports.py --live`

### Issue: "FileNotFoundError: saves/save_data.json"
**Cause:** Save path not updated  
**Fix:** Check `src/core/save_manager.py` has `SAVE_DIR = 'data/saves'`

### Issue: "Asset not found" errors
**Cause:** Asset manager base path incorrect  
**Fix:** Check `src/core/asset_manager.py` `_get_base_path()` method

### Issue: Game won't launch
**Cause:** Main.py can't find modules  
**Fix:** Use `python run.py` instead of `python src/main.py`

### Issue: Old logs still in root logs/
**Cause:** Script only moved some logs  
**Fix:** Manually move remaining logs to `logs/archive/`

---

## ✅ Verification Checklist

After reorganization, verify:

**Structure:**
- [ ] `src/` contains all source code
- [ ] `docs/dev/` contains all dev docs
- [ ] `tests/` contains all test files
- [ ] `data/saves/` contains save file
- [ ] `logs/` is organized
- [ ] Root directory is clean

**Functionality:**
- [ ] Game launches
- [ ] Assets load
- [ ] Saves load
- [ ] Logging works
- [ ] All imports work
- [ ] Tests run
- [ ] No errors in console

**Cleanup:**
- [ ] Old empty directories removed
- [ ] Backup created successfully
- [ ] .gitignore in place
- [ ] No duplicate files

---

## 📈 Benefits You'll See

### Immediate:
✅ **Cleaner root directory** - Easy to find things  
✅ **Better organization** - Everything has a place  
✅ **Professional structure** - Follows Python standards  

### Long-term:
✅ **Easier collaboration** - Clear where to add code  
✅ **Better version control** - .gitignore handles artifacts  
✅ **Faster onboarding** - New devs can navigate easily  
✅ **Scalable** - Room to grow without clutter  

---

## 🎓 What the Scripts Do (Technical)

### reorganize_project.py

**Directory Creation:**
- Creates `src/`, `tests/`, `docs/`, `data/`
- Creates subdirectories (`src/core/`, `docs/dev/`, etc.)

**File Movement:**
- Moves `*.py` from root to `src/`
- Moves `core/*.py` to `src/core/`
- Moves `game/states/*.py` to `src/game/states/`
- Moves docs to `docs/dev/`
- Moves tests to `tests/`
- Moves saves to `data/saves/`
- Archives old logs to `logs/archive/YYYY-MM/`
- Moves backups to `backups/`

**Generated Files:**
- `.gitignore` with proper exclusions
- `__init__.py` files where needed
- `reorganization_report.json` with change log

### update_imports.py

**Import Updates:**
- `from core.X` → `from src.core.X`
- `from game.X` → `from src.game.X`
- `import core.X` → `import src.core.X`
- `import game.X` → `import src.game.X`

**Path Updates:**
- `save_manager.py`: `SAVE_DIR = 'data/saves'`
- `asset_manager.py`: Updated base path calculation
- `main.py`: Added sys.path adjustment

**Generated Files:**
- `run.py` launcher script
- Change tracking for each file

---

## 💡 Pro Tips

1. **Run dry-run first ALWAYS** - Never skip this step
2. **Test immediately after** - Don't wait to discover issues
3. **Keep the backup** - Don't delete it for a few days
4. **Commit to git after** - Once tested, commit the changes
5. **Update README** - Mention new structure in docs

---

## 🚨 Critical Warnings

❌ **Don't reorganize during active development**  
❌ **Don't skip the dry-run step**  
❌ **Don't delete backups immediately**  
❌ **Don't reorganize without testing after**  
❌ **Don't run scripts from wrong directory**  

✅ **Do create manual backup first**  
✅ **Do test thoroughly after**  
✅ **Do run dry-run before live**  
✅ **Do keep backup for a while**  
✅ **Do commit to git after testing**  

---

## 📞 Need Help?

If something goes wrong:

1. **Don't panic** - You have backups!
2. **Check console output** - Errors are usually clear
3. **Review the report** - `reorganization_report.json`
4. **Rollback if needed** - Use backup procedure above
5. **Test step-by-step** - Isolate the issue

---

## 🎯 Final Recommendation

**Wait until:**
- Wild encounters are implemented
- Battle integration works
- Code is stable and tested

**Then reorganize.**

The scripts are ready when you are! 🚀

---

**Questions? Check `REORGANIZATION_PLAN.md` for detailed technical info.**
