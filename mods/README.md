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
