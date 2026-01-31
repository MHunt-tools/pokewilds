# PokeGen - Quick Start Guide

Get started with PokeGen in 5 minutes!

## 1. Install Dependencies

```bash
cd PokeGen
pip install -r requirements.txt
```

This installs Flask (required) and AI dependencies (optional).

## 2. Run Web UI

```bash
./start-web-app.sh
```

Open browser: **http://localhost:5000**

Or start Python directly:
```bash
python3 app.py
```

## 3. Create Your First Pokémon

### Via Web UI (Easiest)

1. Open http://localhost:5000
2. Enter name: "Flamewing"
3. Pokédex #: 888
4. Type: FIRE / FLYING
5. Click "Create Pokémon"

### Via Command Line

```bash
./create-pokemon.sh Flamewing 888 FIRE FLYING
```

## 4. Generate a Sprite (Optional)

### Via Web UI

1. Click "Generate Sprite" tab
2. Type: "red fire-type dragon with golden wings"
3. Click "Generate Sprite"
4. Download image

### Via CLI

```bash
python3 sprite_generator.py Flamewing "red fire-type dragon"
```

**Note:** First generation downloads 4GB AI model (one-time).

## 5. Test in PokeWilds

1. Restart PokeWilds game
2. Your Pokémon should appear in the Pokédex
3. Catch it in the wild!

## Example: Complete Custom Pokémon

Web UI or CLI:

```bash
./create-pokemon.sh Thunderbird 889 ELECTRIC FLYING \
  --hp 70 --att 85 --def 80 --spa 120 --spd 90 --spe 100 \
  --ability1 STATIC \
  --ability2 LIGHTNING_ROD \
  --template pikachu
```

Then generate a sprite:

```bash
python3 sprite_generator.py Thunderbird "yellow electric bird with lightning"
```

## Common Tasks

### List available types

```
NORMAL, FIRE, WATER, GRASS, ELECTRIC, ICE, FIGHTING,
POISON, GROUND, FLYING, PSYCHIC, BUG, ROCK, GHOST,
DRAGON, DARK, STEEL, FAIRY
```

### Use template sprites

```bash
./create-pokemon.sh MyPokemon 890 WATER --template squirtle
```

### Adjust stats

Stats are configured via command line:
```bash
./create-pokemon.sh MyPokemon 890 WATER \
  --hp 100 --att 80 --def 120 --spa 90 --spd 120 --spe 50
```

In web UI, use the stat sliders.

### Check setup

```bash
python3 test_setup.py
```

## Troubleshooting

### "No module named 'flask'"

```bash
pip install -r requirements.txt
```

### Port 5000 already in use

Edit `app.py`, change:
```python
app.run(host='localhost', port=5001)
```

### Sprite generator not found

Install optional dependencies:
```bash
pip install diffusers transformers torch accelerate
```

### Mod doesn't appear in game

1. Make sure it's in `../mods/MyPokemon/`
2. Restart PokeWilds
3. Check game console for errors

## Next Steps

- Read **README.md** for complete documentation
- Read **INTEGRATION_GUIDE.md** for how mods work
- Customize sprites in `mods/[name]/graphics/`
- Edit stats in `mods/[name]/data/pokemon/dex_entries/`

## Tips

- **Fast creation**: Use templates to copy existing sprites
- **Quality sprites**: Use 2-3 word descriptions ("red fire dragon")
- **Balanced stats**: Look at real Pokémon for reference
- **Multiple mods**: Create as many as you want!

---

**Have fun creating!** 🎨

For help: See README.md and INTEGRATION_GUIDE.md
