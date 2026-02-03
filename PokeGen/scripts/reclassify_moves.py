#!/usr/bin/env python3
"""Reclassify moves in moves_db.json using an expanded keyword->type map."""
import json
from pathlib import Path

DB = Path(__file__).parent / '..' / 'moves_db.json'
DB = DB.resolve()

with open(DB) as f:
    data = json.load(f)

# Expanded keyword -> type mapping (substring keys, checked in order)
# Order matters: more specific / exact substrings should come before generic ones
kw_map = [
    # explicit full-move matches (avoid ambiguous substrings)
    ('POISON_POWDER', 'POISON'),
    ('POWER_GEM', 'ROCK'),
    ('AURORA_BEAM', 'ICE'),
    ('PETAL_BLIZZARD', 'GRASS'),
    ('RAGE_POWDER', 'BUG'),
    ('PLAY_NICE', 'NORMAL'),
    ('FLASH_CANNON', 'STEEL'),
    ('VICE_GRIP', 'NORMAL'),

    # ICE-related specific terms
    ('AVALANCHE', 'ICE'), ('POWDER_SNOW', 'ICE'), ('ICICLE', 'ICE'), ('AURORA', 'ICE'), ('BLIZZARD', 'ICE'), ('ICY', 'ICE'), ('FROST', 'ICE'), ('SNOW', 'ICE'),

    # FIRE-related
    ('SACRED_FIRE', 'FIRE'), ('INFERNO', 'FIRE'), ('FIRE_BLAST', 'FIRE'), ('FLAME', 'FIRE'), ('EMBER', 'FIRE'), ('LAVA', 'FIRE'), ('HEAT_WAVE', 'FIRE'),

    # WATER-related
    ('HYDRO', 'WATER'), ('SURF', 'WATER'), ('BUBBLE', 'WATER'), ('AQUA', 'WATER'), ('LIQUID', 'WATER'), ('WHIRLPOOL', 'WATER'),

    # GRASS-related
    ('PETAL', 'GRASS'), ('LEAF', 'GRASS'), ('GIGA_DRAIN', 'GRASS'), ('SYNTHESIS', 'GRASS'), ('SOLAR', 'GRASS'), ('RAZOR_LEAF', 'GRASS'), ('SEED_BOMB', 'GRASS'),

    # ELECTRIC
    ('THUNDER', 'ELECTRIC'), ('VOLT', 'ELECTRIC'), ('SPARK', 'ELECTRIC'), ('ZAP', 'ELECTRIC'), ('ELECTRO', 'ELECTRIC'),

    # GROUND
    ('EARTHQUAKE', 'GROUND'), ('EARTH', 'GROUND'), ('DIG', 'GROUND'), ('BULLDOZE', 'GROUND'), ('MUD', 'GROUND'),

    # ROCK
    ('ROCK', 'ROCK'), ('STONE', 'ROCK'), ('STONE_EDGE', 'ROCK'), ('POWER_GEM', 'ROCK'),

    # DRAGON
    ('OUTRAGE', 'DRAGON'), ('DRAGON', 'DRAGON'),

    # BUG
    ('STRUGGLE_BUG', 'BUG'), ('BUG', 'BUG'), ('TWINEEDLE', 'BUG'), ('X_SCISSOR', 'BUG'), ('LEECH', 'BUG'),

    # PSYCHIC
    ('PSYCHIC', 'PSYCHIC'), ('PSYBEAM', 'PSYCHIC'), ('PSY', 'PSYCHIC'), ('ZEN', 'PSYCHIC'),

    # GHOST
    ('NIGHT_SHADE', 'GHOST'), ('ASTONISH', 'GHOST'), ('SHADOW', 'GHOST'), ('GHOST', 'GHOST'),

    # POISON
    ('TOXIC', 'POISON'), ('SLUDGE', 'POISON'), ('POISON', 'POISON'),

    # FIGHTING
    ('CLOSE_COMBAT', 'FIGHTING'), ('FOCUS_PUNCH', 'FIGHTING'), ('KICK', 'FIGHTING'), ('PUNCH', 'FIGHTING'), ('HAMMER', 'FIGHTING'),

    # FLYING
    ('HURRICANE', 'FLYING'), ('GUST', 'FLYING'), ('WING', 'FLYING'), ('PECK', 'FLYING'), ('AERIAL', 'FLYING'), ('BRAVE_BIRD', 'FLYING'),

    # STEEL
    ('IRON', 'STEEL'), ('METAL', 'STEEL'), ('HEAVY_SLAM', 'STEEL'), ('FLASH_CANNON', 'STEEL'),

    # DARK
    ('NIGHT', 'DARK'), ('BITE', 'DARK'), ('CRUNCH', 'DARK'), ('NIGHT_SLASH', 'DARK'), ('FOUL_PLAY', 'DARK'),

    # fallback/generic catches (keep near the end)
    ('SURF', 'WATER'), ('WATER', 'WATER'), ('FIRE', 'FIRE'), ('ICE', 'ICE'), ('ELECTRIC', 'ELECTRIC'), ('GRASS', 'GRASS'),
    ('ROCK', 'ROCK'), ('DRAGON', 'DRAGON'), ('BUG', 'BUG'), ('PSYCHIC', 'PSYCHIC'), ('GHOST', 'GHOST'), ('POISON', 'POISON'),
    # ambiguous/generic terms last: POWDER near the end to avoid misclassifying POISON_POWDER
    ('POWDER', 'ICE'),
]

# normalize keys: uppercase
kw_map = [(k.upper(), t) for k, t in kw_map]

changed = 0
for entry in data:
    mv = entry.get('move','').upper()
    cur = entry.get('type','').upper()
    if cur != 'NORMAL':
        # keep existing specific types
        continue
    # try to reclassify using keywords
    assigned = None
    for kw, t in kw_map:
        if kw in mv:
            assigned = t
            break
    if assigned and assigned != cur:
        entry['type'] = assigned
        changed += 1

if changed > 0:
    with open(DB, 'w') as f:
        json.dump(data, f, indent=2)
print(f"Reclassified {changed} moves in {DB}")
