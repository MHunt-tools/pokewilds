# PokeGen - Pokémon Mod Creator for PokeWilds

Create custom Pokémon mods for PokeWilds without recompiling the JAR! PokeGen includes both a beautiful web UI and powerful CLI tools.

## Features

✨ **Web Interface**
- Beautiful, intuitive UI for creating Pokémon
- Real-time type selection
- Stat customization with sliders
- Sprite generation with AI (text-to-image)
- Support for custom sprites and templates

🎮 **CLI Tools**
- Create Pokémon from command line
- Batch generation support
- Programmatic access via Python API

🤖 **AI Sprite Generation**
- Generate unique sprites from text descriptions
- CPU-optimized (no GPU required)
- Customizable quality/speed tradeoff
- Integrates with web UI

## Quick Start

### Prerequisites

- Python 3.9+
- PokeWilds game installed
- 4GB free disk space (for AI model, one-time download)

### Installation

```bash
cd PokeGen
pip install -r requirements.txt
```

### Web UI

```bash
./start-web-app.sh
```

Then open: **http://localhost:5000**

### Command Line

```bash
# Create a simple Pokémon
./create-pokemon.sh MyPokemon 900 FIRE

# With custom stats and template
./create-pokemon.sh Flamewing 901 FIRE FLYING \
  --hp 70 --att 100 --def 90 --spa 80 --spd 100 --spe 95 \
  --template charizard
```

## Usage Examples

### Web UI - Create Pokémon

1. Open http://localhost:5000
2. Fill in the form:
   - **Name**: Your Pokémon name
   - **Pokédex #**: Unique number (888+)
   - **Types**: Select primary and optional secondary type
   - **Stats**: Set base stats (or use defaults)
   - **Abilities**: Configure ability names
   - **Template**: Optional - copy sprites from existing Pokémon
3. Click "Create Pokémon"

The mod will be saved to `../mods/<name>/` and automatically loaded by PokeWilds!

### Web UI - Generate Sprite

1. Click the "Generate Sprite" tab
2. Describe your Pokémon:
   - "red fire-type dragon with golden wings"
   - "blue water penguin with spikes"
   - "purple ghost-type with multiple eyes"
3. Adjust quality slider (20 steps recommended)
4. Click "Generate Sprite"
5. Download when ready

**First use note:** The AI model downloads ~4GB on first generation (one-time). Subsequent generations are much faster.

### CLI - Create Pokémon

```bash
# Basic
python3 pokemon_mod_generator.py MyPokemon --dex 888 --type1 FIRE

# With all options
python3 pokemon_mod_generator.py Flamewing \
  --dex 901 \
  --type1 FIRE \
  --type2 FLYING \
  --hp 70 --att 100 --def 90 --spa 80 --spd 100 --spe 95 \
  --ability1 BLAZE \
  --ability2 SOLAR_POWER \
  --gender 87.5 \
  --template charizard
```

### CLI - Generate Sprite

```bash
python3 sprite_generator.py MySprite "red fire-type dragon"
```

## Type References

Valid types:
```
NORMAL, FIRE, WATER, GRASS, ELECTRIC, ICE, FIGHTING,
POISON, GROUND, FLYING, PSYCHIC, BUG, ROCK, GHOST,
DRAGON, DARK, STEEL, FAIRY
```

## Ability Names

Common abilities (use UPPERCASE):
```
STATIC, LIGHTNING_ROD, VOLT_ABSORB, OVERGROW, CHLOROPHYLL,
RAINDISH, TORRENT, SWIFT_SWIM, BLAZE, FLASH_FIRE,
VITAL_SPIRIT, and more...
```

## Stat Guidelines

Typical stat ranges:
- **Weak Pokémon**: 35-45 per stat
- **Average Pokémon**: 65-75 per stat  
- **Strong Pokémon**: 100-120 per stat
- **Legendary**: 130-140+ per stat

Total BST (Base Stat Total) typically: 300-680

## Sprite Templates

You can copy sprites from existing Pokémon:

```bash
./create-pokemon.sh MyPokemon 888 FIRE --template pikachu
./create-pokemon.sh MyPokemon 889 FIRE --template charizard
```

Available templates depend on what Pokémon sprites are in the game.

## Generated Mod Structure

```
mods/
└── MyPokemon/
    ├── pokemon.cfg           # Configuration
    ├── graphics/
    │   ├── front.png
    │   ├── back.png
    │   ├── front_shiny.png
    │   └── back_shiny.png
    └── data/pokemon/dex_entries/
        ├── mypokemon_base_stats.asm
        └── mypokemon_moves.asm
```

## AI Sprite Generation Guide

### Prompt Engineering Tips

**Good prompts:**
- "red fire-type dragon with golden wings"
- "blue water-type penguin with spikes"
- "purple ghost-type with multiple eyes, transparent"
- "green grass-type bird with leaves on wings"

**Less effective prompts:**
- Just "dragon"
- "pikachu" (avoid using existing Pokémon names directly)
- Very long descriptions

### Quality Settings

- **10-15 steps**: Fast, lower quality, ~30 seconds
- **20-25 steps**: Good balance, ~1 minute (recommended)
- **30+ steps**: High quality, slower, ~2+ minutes

### Performance Notes

- **First generation**: ~10 minutes (downloads 4GB model)
- **Subsequent**: 1-3 minutes depending on quality
- **CPU-only**: Yes, but slower than GPU
- **Memory**: ~4GB needed during generation

## Troubleshooting

### "Module not found" error

Install dependencies:
```bash
pip install -r requirements.txt
```

### Sprite generator unavailable

The AI sprite generator is optional. Create Pokémon without it or:

```bash
pip install diffusers transformers torch accelerate
```

### Flask port 5000 already in use

Change port in `app.py`:
```python
app.run(host='localhost', port=5001)  # Use different port
```

### Mod not appearing in game

1. Make sure mod directory is in `../mods/`
2. Restart PokeWilds
3. Check that the mod name matches the directory name

### Sprite generation very slow

- This is normal on CPU-only
- Try reducing inference steps to 15-20
- First generation downloads model (downloads happen once)

## Development

### Using the Python API

```python
from pokemon_mod_generator import PokemonModGenerator, PokemonStats

gen = PokemonModGenerator()

stats = PokemonStats(hp=70, attack=100, defense=90)

gen.create_pokemon(
    name="MyPokemon",
    dex_number=888,
    type1="FIRE",
    type2="FLYING",
    stats=stats,
    ability1="BLAZE",
    template_pokemon="charizard"
)
```

### Sprite Generation API

```python
from sprite_generator import SpriteGenerator

gen = SpriteGenerator(device="cpu")

image = gen.generate_sprite(
    prompt="red fire-type dragon",
    num_inference_steps=20
)

image.save("my_sprite.png")
```

## File Reference

- `app.py` - Flask web application
- `pokemon_mod_generator.py` - Core Pokémon mod generator
- `sprite_generator.py` - AI sprite generation
- `requirements.txt` - Python dependencies
- `templates/index.html` - Web UI
- `start-web-app.sh` - Web app launcher
- `create-pokemon.sh` - CLI launcher

## License

PokeGen is a fan-made tool for PokeWilds. Respect the original game's terms of service.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the generated mod structure
3. Ensure Python 3.9+ and all dependencies are installed

---

**Happy Pokémon creating!** 🎨
