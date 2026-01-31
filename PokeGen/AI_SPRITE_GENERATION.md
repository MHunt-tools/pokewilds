# AI Sprite Generation Guide

PokeGen includes integrated AI sprite generation using Stable Diffusion. Generate unique Pokémon sprites directly from text descriptions!

## Overview

The sprite generator uses **Stable Diffusion 1.5** to create pixel-art style Pokémon sprites from natural language descriptions. It's:

- **Local**: Runs entirely on your computer (no API calls)
- **CPU-compatible**: Works without GPU (slow but functional)
- **Customizable**: Control quality vs. speed tradeoff
- **Integrated**: Use from web UI, CLI, or Python API

## Installation

### Basic Setup

```bash
cd PokeGen
pip install -r requirements.txt
```

This installs:
- `torch` - PyTorch deep learning framework (CPU version)
- `diffusers` - Hugging Face Stable Diffusion
- `transformers` - Hugging Face model library
- `accelerate` - Optimization utilities

### First Run

**First generation takes ~10 minutes** and downloads ~4GB model from Hugging Face. Subsequent generations take 1-3 minutes.

Models are cached in `~/.cache/huggingface/`

## Usage

### Web UI

1. Open http://localhost:5000
2. Click "Generate Sprite" tab
3. Enter description: "red fire-type dragon with golden wings"
4. Adjust quality slider (20 recommended)
5. Click "Generate Sprite"
6. Download or save directly to mod

### Command Line

```bash
# Basic
python3 sprite_generator.py MySprite "red fire dragon"

# With options
python3 sprite_generator.py MySprite "blue water penguin" \
  --steps 25 \
  --seed 12345 \
  --output ./sprites/
```

### Python API

```python
from sprite_generator import SpriteGenerator

# Initialize
gen = SpriteGenerator(device="cpu", low_memory=True)

# Generate single image
image = gen.generate_sprite(
    prompt="red fire-type dragon",
    num_inference_steps=20,
    seed=42
)

# Save
image.save("dragon_sprite.png")

# Generate and save in one call
gen.generate_and_save(
    prompt="electric mouse",
    output_path=Path("sprite.png"),
    num_inference_steps=20
)
```

## Prompt Engineering

### Good Prompts

**Detailed descriptions work best:**

```
"red fire-type dragon with golden wings and spikes"
"blue water penguin with icy spikes on back"
"purple ghost-type with multiple floating eyes"
"green grass-type bird with leaf-shaped wings"
"yellow electric mouse with red cheeks and black stripes"
```

**Include:**
- Color (red, blue, green, etc.)
- Type or element (fire, water, grass, etc.)
- Shape hints (dragon, bird, penguin, mouse)
- Special features (wings, spikes, patterns)

### Less Effective

**Avoid:**
- Just names: "Pikachu" (AI doesn't know Pokémon)
- Vague descriptions: "cool animal"
- Very long prompts (50+ words)
- Conflicting descriptions: "fire water dragon"

### Style Hints

**PokeGen automatically adds** to all prompts:
- "Pokémon sprite"
- "Game Boy art style"
- "Pixel art"
- "4-color palette"
- "Official Nintendo style"

You don't need to add these.

## Quality Settings

### Inference Steps

Controls how many steps the diffusion process runs:

- **10-15 steps**: Fast (~30 sec), lower quality
- **20 steps**: Balanced (~1 min), good quality ⭐ Recommended
- **25-30 steps**: Higher quality (~1.5-2 min)
- **40-50 steps**: Highest quality (~3-4 min)

### Guidance Scale

How strongly the model follows your prompt (default: 7.5):

- **Lower (5-6)**: More creative, looser interpretation
- **Default (7.5)**: Balanced
- **Higher (9-10)**: Strictly follows prompt

## Performance

### On CPU (default)

- **First run**: ~10 minutes (model download)
- **Subsequent**: 1-3 minutes per sprite (depending on steps)
- **Memory needed**: 4GB+ free RAM
- **Disk needed**: 4GB for model cache

### On GPU (if available)

If your system has NVIDIA GPU and CUDA installed:

```bash
# Modify sprite_generator.py:
gen = SpriteGenerator(device="cuda", low_memory=False)
```

Approximately **5-10x faster** than CPU.

## Tips for Best Results

### 1. Experiment with Descriptions

Same concept, different phrasings:

```
❌ "dragon"
✓ "red fire-type dragon"
✓ "crimson dragon with golden wings"
✓ "red dragon, Game Boy style, pixel art"
```

All produce good results, but phrasing matters.

### 2. Iterate

Generate multiple versions with different seeds:

```python
for seed in [1, 2, 3, 4, 5]:
    gen.generate_sprite(prompt="red fire dragon", seed=seed)
```

Pick your favorite.

### 3. Use Consistent Style

For a cohesive Pokédex:
- Consistent art style (all pixel art)
- Similar color palettes
- Similar pose (side view, front view)

### 4. Refine Based on Output

If result is too detailed:
```
✗ "red dragon with lots of spikes and patterns and details"
✓ "red spiky dragon"
```

If too simple:
```
✗ "dragon"
✓ "detailed red fire dragon with golden accents"
```

## Examples

### Creating a Legendary

```
"golden god-like dragon with crystalline wings, 
divine aura, majestic pose"
```

Steps: 30+, Seed: Random

### Simple Early-Game Pokémon

```
"tiny blue water puppy with big eyes"
```

Steps: 15-20, Seed: Random

### Specific Type Design

```
"electric yellow mouse with black stripes and red cheeks,
Game Boy style, retro pixel art"
```

Steps: 20-25, Seed: Random

### Hybrid Type

```
"grass and flying type, green bird with flower petals,
Game Boy Color style"
```

Steps: 20, Seed: Random

## Troubleshooting

### "CUDA out of memory" on GPU

The CPU path is fine:
```python
gen = SpriteGenerator(device="cpu", low_memory=True)
```

### Model takes very long to download

- Check internet connection
- First model download is ~4GB
- Subsequent runs use cached model (much faster)

### Generated sprite looks nothing like prompt

- Try simplifying the prompt
- Adjust guidance scale (lower = more creative)
- Try different seeds
- Increase steps (better quality = better prompt following)

### "Out of memory" on CPU

Reduce steps or use smaller resolution:
```python
gen.generate_sprite(
    prompt="...",
    num_inference_steps=15,
    height=64,  # Smaller
    width=64
)
```

### Model won't download

Check:
1. Internet connection
2. Disk space (4GB needed)
3. Hugging Face is reachable
4. Enough permissions to write to home directory

## Advanced Usage

### Batch Generation

```python
from sprite_generator import SpriteGenerator
from pathlib import Path

gen = SpriteGenerator()
pokemon_list = [
    ("Flamewing", "red fire dragon"),
    ("Aquadrift", "blue water penguin"),
    ("Verdant", "green grass dinosaur"),
]

for name, description in pokemon_list:
    output_path = Path(f"sprites/{name}.png")
    gen.generate_and_save(description, output_path, num_inference_steps=20)
```

### Custom Model

```python
gen = SpriteGenerator(
    model_name="runwayml/stable-diffusion-v1-5",  # Or another model
    device="cpu"
)
```

Available models:
- `runwayml/stable-diffusion-v1-5` (default)
- `runwayml/stable-diffusion-inpainting` (for editing)
- Other HuggingFace models

### Programmatic Style Control

```python
def generate_pokemon_set(name, description):
    """Generate front, back, shiny variants"""
    gen = SpriteGenerator()
    
    styles = {
        "front": f"{description}, front view, Game Boy",
        "back": f"{description}, back view, Game Boy",
        "shiny": f"{description}, shiny version, sparkles, Game Boy"
    }
    
    for variant, prompt in styles.items():
        image = gen.generate_sprite(prompt, num_inference_steps=20)
        image.save(f"sprites/{name}_{variant}.png")
```

## Performance Optimization

### For CPU Performance

Current defaults already optimize for CPU:

```python
# sprite_generator.py uses:
self.pipe.enable_attention_slicing()  # Save memory
# torch.float32 (better for CPU than float16)
```

To further optimize:
1. Reduce `num_inference_steps` (15-20 instead of 25+)
2. Use smaller resolution (64x64 instead of 96x96)
3. Run on GPU if available

### Memory Management

The model stays in memory after first load. To free it:

```python
import torch

# Between generations
torch.cuda.empty_cache()  # On GPU
# Or restart Python process
```

## Hardware Requirements

### Minimum (CPU-only)
- Python 3.9+
- 4GB RAM
- 4GB disk space
- ~2-3 min per sprite

### Recommended (With GPU)
- NVIDIA GPU with CUDA support
- 8GB GPU VRAM
- 4GB disk space
- ~15-30 sec per sprite

### Not Supported
- AMD GPU (would need HIP)
- Intel Arc (would need oneAPI)
- Apple Silicon (would need Metal)

(Can still run on CPU on any platform)

## License & Attribution

- **Stable Diffusion**: Stability AI (RAIL license)
- **PyTorch**: Meta (BSD)
- **Diffusers**: HuggingFace (Apache 2.0)

Models are downloaded from HuggingFace on first use.

## Summary

- **Quick start**: `python3 sprite_generator.py MyMon "red fire dragon"`
- **Web UI**: Open http://localhost:5000 → "Generate Sprite"
- **Prompt tips**: Specific descriptions work best
- **Quality**: 20 steps is recommended balance
- **First run**: Downloads 4GB model (one-time)
- **Performance**: CPU-compatible, GPU optional

---

**Happy sprite generating!** 🎨

For more info, see README.md and QUICK_START.md
