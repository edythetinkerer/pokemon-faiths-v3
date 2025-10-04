# 🎮 QUICK START GUIDE

## Run the Game

```bash
cd C:\Users\edy\Desktop\Faith
python run.py
```

**That's it!** The game will start immediately.

---

## Common Tasks

### Play the Game
```bash
python run.py
```

### Clean Up Old Directories
```bash
python cleanup_old_dirs.py
```

### View Logs
```
logs/game_YYYYMMDD_HHMMSS.log
```

### Check Save File
```
data/saves/save_data.json
```

---

## In-Game Controls

| Action | Key |
|--------|-----|
| Move | WASD or Arrow Keys |
| Sprint | Shift |
| Interact | E |
| Pause | ESC |
| Debug Mode | F1 |
| Screenshot | F2 |
| Fullscreen | F11 |

---

## Project Status

**✅ FULLY OPERATIONAL**

- All files organized in `src/`
- All imports working correctly
- No errors in logs
- All game systems functional
- Save/load working
- All scenes accessible

---

## Important Files

| File | Purpose |
|------|---------|
| `run.py` | **Main launcher - use this to start the game** |
| `src/main.py` | Game entry point |
| `data/saves/save_data.json` | Your save file |
| `settings.json` | Game settings |
| `GAME_STATUS.md` | Detailed status report |
| `README.md` | Full documentation |

---

## Project Structure

```
Faith/
├── run.py              ← START HERE
├── src/                ← All code
│   ├── main.py
│   ├── core/          ← Core systems
│   └── game/states/   ← Game scenes
├── assets/            ← Images, audio
├── data/saves/        ← Save files
└── logs/              ← Game logs
```

---

## Troubleshooting

### Game Won't Start
1. Make sure you're in the project directory
2. Check Python is installed: `python --version`
3. Install pygame: `pip install pygame`
4. Run: `python run.py`

### Import Errors
- Always run from project root using `run.py`
- Don't run files directly from `src/` folder

### Save Issues
- Save file is at: `data/saves/save_data.json`
- Old saves were in `saves/` (copy if needed)

---

## Development Quick Tips

### Add a New Scene
1. Create file in `src/game/states/`
2. Add scene logic
3. Update `src/main.py` to include transition

### Add Assets
1. Place in `assets/images/` or `assets/audio/`
2. Load with `get_asset_manager()`

### View Debug Info
- Press **F1** in-game for debug overlay
- Press **F2** for screenshot
- Press **F3** to log game state
- Check `logs/` folder for detailed logs

---

## Next Steps

1. **Play the game** - It's ready!
2. **Optional**: Run `cleanup_old_dirs.py` to remove empty folders
3. **Read** `GAME_STATUS.md` for detailed information
4. **Develop**: Add new features, scenes, content

---

## Documentation Files

| File | What It Contains |
|------|------------------|
| `README.md` | Complete project documentation |
| `GAME_STATUS.md` | Current operational status |
| `REORGANIZATION_COMPLETE.md` | Reorganization details |
| `REORGANIZATION_SUMMARY.md` | What was done today |
| This file | Quick reference guide |

---

**Status:** 🟢 Everything Working  
**Last Updated:** October 3, 2025  
**Version:** 0.2.0

---

## Have Fun! 🎮

The game is fully functional and ready to play. Enjoy exploring the dark world of Pokémon Faiths!
