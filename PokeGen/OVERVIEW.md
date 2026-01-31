# PokeGen - Complete System Overview

PokeGen is a comprehensive toolkit for creating custom Pokémon mods for PokeWilds without recompiling the game. It includes a beautiful web UI, powerful CLI tools, and integrated AI sprite generation.

## 🎯 What is PokeGen?

PokeGen enables you to:

1. **Create custom Pokémon** with customizable stats, types, and abilities
2. **Generate unique sprites** using AI (text-to-image with Stable Diffusion)
3. **Manage mods** that load dynamically into PokeWilds
4. **Design balanced games** with your own Pokédex

All without touching a single line of Java code!

## 📁 System Architecture

```
PokeGen/
├── Core Components
│   ├── app.py                        # Flask web server
│   ├── pokemon_mod_generator.py      # Pokémon creation engine
│   └── sprite_generator.py           # AI sprite generation
│
├── User Interfaces
│   ├── templates/index.html          # Web UI (beautiful 3-tab interface)
│   ├── start-web-app.sh              # Web server launcher
│   └── create-pokemon.sh             # CLI launcher
│
├── Configuration
│   ├── requirements.txt              # Python dependencies
│   └── test_setup.py                 # Setup verification
│
├── Documentation
│   ├── README.md                     # Complete guide (this file)
│   ├── QUICK_START.md                # 5-minute quickstart
│   ├── INTEGRATION_GUIDE.md          # How mods work
│   ├── AI_SPRITE_GENERATION.md       # Sprite generator guide
│   └── OVERVIEW.md                   # This file
│
└── Generated at Runtime
    ├── mods/                         # Created Pokémon mods
    └── .cache/                       # AI model cache
```

## 🚀 Quick Start (5 minutes)

### 1. Install

```bash
cd PokeGen
pip install -r requirements.txt
```

### 2. Run Web UI

```bash
./start-web-app.sh
# Open http://localhost:5000
```

### 3. Create Pokémon

- Fill form → Click "Create Pokémon"
- Or CLI: `./create-pokemon.sh MyPokemon 888 FIRE`

### 4. Generate Sprite (optional)

- Enter description → Click "Generate Sprite"
- Or CLI: `python3 sprite_generator.py MySprite "red fire dragon"`

### 5. Play

- Restart PokeWilds
- Your Pokémon appears in game!

## 🎨 Features in Detail

### Web Interface (http://localhost:5000)

Beautiful 3-tab interface:

**Tab 1: Create Pokémon**
- Name and Pokédex number
- Type selection (17 types)
- Base stat customization (HP, ATK, DEF, SpA, SpD, SPE)
- Ability configuration
- Sprite template selection
- Real-time validation

**Tab 2: Generate Sprite**
- Text-to-image AI generation
- Quality slider (10-50 steps)
- Live preview
- One-click download

### CLI Tools

**Create Pokémon:**
```bash
./create-pokemon.sh Name 888 TYPE1 [TYPE2] [options]
```

**Generate Sprite:**
```bash
python3 sprite_generator.py Name "description"
```

**Run Web Server:**
```bash
./start-web-app.sh
```

**Python API:**
```python
from pokemon_mod_generator import PokemonModGenerator

gen = PokemonModGenerator()
gen.create_pokemon(name="MyMon", dex_number=888, type1="FIRE")
```

## 🔧 Technical Details

### Python Components

#### 1. `pokemon_mod_generator.py` (275 lines)

Creates Pokémon mods with:
- **Class**: `PokemonModGenerator`
- **Main method**: `create_pokemon()`
- **Generates**: ASM files, config, sprite directories
- **Features**:
  - Template sprite copying
  - Type/ability mapping
  - Automatic ASM generation
  - Customizable stats

#### 2. `sprite_generator.py` (230 lines)

AI sprite generation with:
- **Class**: `SpriteGenerator`
- **Model**: Stable Diffusion v1.5 from HuggingFace
- **Optimization**: CPU-friendly attention slicing
- **Features**:
  - Text-to-image conversion
  - Prompt enhancement
  - Seed control for reproducibility
  - Memory-optimized for CPU

#### 3. `app.py` (260 lines)

Flask web server with:
- **Framework**: Flask 3.0
- **Routes**: `/api/create`, `/api/generate-sprite`
- **UI**: Serves `templates/index.html`
- **Features**:
  - Lazy-loading of sprite generator
  - JSON REST API
  - Error handling
  - CORS-compatible

### HTML/CSS/JavaScript Interface

**File**: `templates/index.html` (650 lines)

Features:
- Responsive design (works on phone/tablet/desktop)
- Beautiful gradient header
- Tab-based interface
- Type selector buttons
- Stat sliders
- Real-time validation
- Base64 image preview
- Loading indicators
- Error messages

## 📊 Workflow

### Creating a Pokémon

```
User Input (Web/CLI)
    ↓
PokemonModGenerator
    ├─ Validate inputs
    ├─ Create mod directory (mods/NAME/)
    ├─ Copy/generate sprites (graphics/)
    ├─ Generate ASM files (data/pokemon/dex_entries/)
    ├─ Generate config file (pokemon.cfg)
    └─ Success message
    ↓
Mod appears in ../mods/NAME/
    ↓
PokeWilds loads at startup
    ↓
Pokémon available in game
```

### Generating a Sprite

```
Prompt (Web/CLI)
    ↓
SpriteGenerator
    ├─ Enhance prompt with style hints
    ├─ Load Stable Diffusion model (first time only: 4GB)
    ├─ Run diffusion pipeline (20+ steps, ~1-3 min)
    ├─ Convert result to PNG
    └─ Return image
    ↓
Image preview (Web) or saved file (CLI)
    ↓
User downloads or integrates into mod
```

## 🎮 PokeWilds Integration

### How Mods Load

1. PokeWilds starts
2. Checks `mods/` directory
3. For each Pokémon subdirectory:
   - Reads `pokemon.cfg`
   - Loads graphics from `graphics/`
   - Parses ASM stats files
4. Pokémon available in game

### Mod File Structure

```
mods/
└── MyPokemon/
    ├── pokemon.cfg                    # Metadata
    ├── graphics/
    │   ├── front.png                  # Battle sprite (front)
    │   ├── back.png                   # Battle sprite (back)
    │   ├── front_shiny.png            # Shiny variant
    │   └── back_shiny.png             # Shiny variant (back)
    └── data/pokemon/dex_entries/
        ├── mypokemon_base_stats.asm   # Stats: HP, ATK, DEF, etc.
        └── mypokemon_moves.asm        # Moves learnset
```

## 💾 Dependencies

### Required
- **Python 3.9+** - Language runtime
- **Flask 3.0** - Web framework
- **Pillow 10.1** - Image processing

### Optional (for sprite generation)
- **PyTorch 2.1** - Deep learning framework (CPU-only version)
- **Diffusers 0.24** - Stable Diffusion library
- **Transformers 4.35** - Model library
- **Accelerate 0.24** - Optimization utilities

Total disk space:
- Code: ~1-2 MB
- AI model: ~4 GB (downloaded on first use)
- Mods: Varies (typically 100-500 KB per Pokémon)

## ⚙️ Configuration

### app.py

Modify these constants:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB files
app.run(debug=True, host='localhost', port=5000)     # Server config
```

### sprite_generator.py

Modify initialization:
```python
gen = SpriteGenerator(
    device="cpu",                    # 'cpu' or 'cuda'
    low_memory=True,                 # Enable CPU optimizations
    model_name="runwayml/stable-diffusion-v1-5"
)
```

### requirements.txt

Pin specific versions or update to latest:
```
Flask==3.0.0          # Latest: varies
torch==2.1.0          # Latest: varies
```

## 🔍 File Descriptions

| File | Purpose | Lines | Language |
|------|---------|-------|----------|
| `pokemon_mod_generator.py` | Pokémon creation engine | 275 | Python |
| `sprite_generator.py` | AI sprite generation | 230 | Python |
| `app.py` | Flask web server | 260 | Python |
| `templates/index.html` | Web UI | 650 | HTML/CSS/JS |
| `requirements.txt` | Dependencies | 7 | Text |
| `start-web-app.sh` | Web launcher | 35 | Bash |
| `create-pokemon.sh` | CLI launcher | 30 | Bash |
| `test_setup.py` | Setup verification | 85 | Python |
| `README.md` | Complete guide | ~500 | Markdown |
| `QUICK_START.md` | 5-min quickstart | ~150 | Markdown |
| `INTEGRATION_GUIDE.md` | Mod integration | ~250 | Markdown |
| `AI_SPRITE_GENERATION.md` | Sprite guide | ~400 | Markdown |

**Total**: ~2,800 lines of code + docs

## 🧪 Testing

Verify setup:
```bash
python3 test_setup.py
```

Checks:
- Required packages installed
- Optional packages available
- Required files present

## 📈 Scalability

### Single Pokémon
- Time: 1-5 seconds (web UI)
- Space: 100-500 KB

### Many Pokémon (100+)
```python
# Batch creation possible
for i in range(100):
    gen.create_pokemon(f"Pokemon{i}", 1000+i, "FIRE")
```

- Time: ~1-2 seconds each
- Space: 10-50 MB total

### Sprite Generation
- Time: 1-3 min per sprite (CPU)
- Space: 4 GB model + 10-100 KB per sprite
- Scalable: Batch with different seeds/prompts

## 🚨 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "No module named flask" | `pip install -r requirements.txt` |
| Port 5000 in use | Change port in `app.py` |
| Sprite generator missing | `pip install diffusers torch transformers accelerate` |
| Mod not in game | Restart PokeWilds, check `mods/` directory |
| Slow sprite generation | Normal on CPU; reduce steps to 15-20 |

See documentation files for detailed troubleshooting.

## 📚 Documentation

- **README.md** - Full reference guide
- **QUICK_START.md** - Get started in 5 minutes
- **INTEGRATION_GUIDE.md** - How mods work with PokeWilds
- **AI_SPRITE_GENERATION.md** - Comprehensive sprite guide
- **OVERVIEW.md** - This file (architecture & design)

## 🎓 Learning Path

1. **Read** QUICK_START.md (5 min)
2. **Try** web UI (create simple Pokémon)
3. **Experiment** with sprites
4. **Read** README.md (full reference)
5. **Explore** INTEGRATION_GUIDE.md (advanced)
6. **Dive** AI_SPRITE_GENERATION.md (optional)

## 🔮 Future Enhancements

Possible additions:
- Move editor UI
- Evolution chain designer
- Bulk upload feature
- Community mod sharing
- Advanced prompt templates
- Model selection UI

## 📄 License & Credits

- **PokeGen**: Fan-made tool for PokeWilds
- **Stable Diffusion**: Stability AI
- **PyTorch**: Meta AI
- **Flask**: Pallets
- **HuggingFace**: Community

Respects original PokeWilds terms of service.

## 🙋 Support

For issues:
1. Check troubleshooting in relevant doc
2. Run `python3 test_setup.py`
3. Verify Python 3.9+ installed
4. Try clean reinstall: `pip install -r requirements.txt --force-reinstall`

## 🎉 Summary

PokeGen is a complete, user-friendly system for creating custom Pokémon:

- **Simple**: Web UI or command-line
- **Powerful**: Customizable stats, types, abilities
- **Creative**: AI-powered sprite generation
- **Integrated**: Direct loading into PokeWilds
- **Documented**: Multiple guides for all skill levels
- **Accessible**: CPU-compatible, no GPU required

Created to make Pokémon modding accessible to everyone!

---

**Version**: 1.0
**Last Updated**: 2024
**Status**: Ready to use

For questions, see the documentation files in this directory.
