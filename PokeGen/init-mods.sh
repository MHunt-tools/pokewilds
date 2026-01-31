#!/bin/bash
# Initialize mods directory structure
# Creates the mods/ directory with proper structure for PokeGen

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
MODS_DIR="$PARENT_DIR/mods"

echo "Initializing PokeGen mods directory..."
echo ""

# Create mods directory
mkdir -p "$MODS_DIR"
echo "✓ Created $MODS_DIR"

# Create a README for the mods directory
cat > "$MODS_DIR/README.md" << 'EOF'
# PokeWilds Mods Directory

This directory contains custom Pokémon mods created with PokeGen.

## Structure

Each Pokémon mod should follow this structure:

```
[PokemonName]/
├── pokemon.cfg              # Configuration file
├── graphics/
│   ├── front.png           # Front battle sprite
│   ├── back.png            # Back battle sprite
│   ├── front_shiny.png     # Shiny front sprite
│   └── back_shiny.png      # Shiny back sprite
└── data/pokemon/dex_entries/
    ├── [name]_base_stats.asm   # Stats (HP, ATK, DEF, etc.)
    └── [name]_moves.asm        # Moves and evolution data
```

## Auto-Generated Mods

Mods created with PokeGen will automatically appear here with this structure.

## Manual Mods

You can also create mods manually following the structure above.

## Loading

PokeWilds automatically loads all mods from this directory at startup.
Restart the game to load new mods.

## Support

For help creating mods, see the PokeGen documentation:
- QUICK_START.md
- README.md
- INTEGRATION_GUIDE.md
EOF

echo "✓ Created $MODS_DIR/README.md"
echo ""
echo "Mods directory is ready!"
echo "Location: $MODS_DIR"
echo ""
echo "Next steps:"
echo "  1. cd $SCRIPT_DIR"
echo "  2. ./start-web-app.sh"
echo "  3. Open http://localhost:5000"
echo ""
