#!/usr/bin/env python3
"""Regenerate moves_db.json by scanning the attacks/ folder and merging with existing DB."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).parent.parent
ATTACKS = ROOT / 'attacks'
DB_PATH = Path(__file__).parent / '..' / 'moves_db.json'
DB_PATH = DB_PATH.resolve()

# existing db
existing = {}
if DB_PATH.exists():
    with open(DB_PATH) as f:
        try:
            for e in json.load(f):
                existing[e['move'].upper()] = e
        except Exception:
            existing = {}

# keywords -> type heuristics
kw_type = {
    'FIRE': ['fire', 'flame', 'ember', 'blaze', 'sacred_fire', 'flamethrower', 'flame_wheel', 'fire_blast'],
    'WATER': ['water', 'hydro', 'surf', 'bubble', 'whirlpool', 'water_gun', 'waterfall'],
    'GRASS': ['leaf', 'vine', 'solar', 'razor_leaf', 'giga_drain', 'synthesis'],
    'ELECTRIC': ['thunder', 'spark', 'volt', 'thundershock', 'thunderbolt'],
    'ICE': ['ice', 'powder', 'blizzard', 'powder_snow'],
    'GROUND': ['earth', 'dig', 'quake', 'earthquake'],
    'ROCK': ['rock', 'stone'],
    'FIGHTING': ['fight', 'karate', 'punch', 'kick', 'brick_break'],
    'POISON': ['poison', 'sludge', 'toxic'],
    'PSYCHIC': ['psy', 'psychic', 'psybeam'],
    'GHOST': ['ghost', 'shadow'],
    'BUG': ['bug', 'leech_life', 'twineedle'],
    'DRAGON': ['dragon', 'outrage', 'dragonbreath'],
    'STEEL': ['iron', 'steel'],
    'FLYING': ['fly', 'wing', 'peck', 'drill_peck'],
    'DARK': ['bite', 'crunch', 'dark', 'faint_attack'],
    'NORMAL': ['tackle', 'slash', 'return', 'hyper_beam', 'double_edge', 'take_down', 'pound']
}

# power heuristics by keyword
kw_power = {
    'blast': 110,
    'flame': 90,
    'beam': 90,
    'hydro': 110,
    'surf': 90,
    'pump': 110,
    'ice': 90,
    'blizzard': 110,
    'strike': 75,
    'punch': 75,
    'kick': 75,
    'edge': 120,
    'hyper': 150,
    'return': 70,
    'tackle': 40,
    'bite': 60,
    'slash': 70,
    'rock': 75,
    'earthquake': 100,
    'dragon': 80,
}

# gather move names from attacks/ directory
moves = set(existing.keys())
if ATTACKS.exists():
    for entry in ATTACKS.iterdir():
        name = entry.name
        # strip suffixes like _enemy_gsc, _player_gsc, _overworld, _setup
        # remove common suffix patterns used in this repo
        name = re.sub(r'(_enemy(_gsc)?|_player(_gsc)?|_overworld|_setup|_sheet[0-9]*|_hit|_left|_right|_gsc)$', '', name)
        name = re.sub(r'\.png$', '', name)
        name = name.strip()
        if not name:
            continue
        # convert to uppercase and replace non-alnum with underscore
        name_key = re.sub(r'[^A-Za-z0-9]+', '_', name).upper()
        moves.add(name_key)

# build new entries
new_entries = {}
for mv in sorted(moves):
    if mv in existing:
        new_entries[mv] = existing[mv]
        continue
    # guess type
    mv_lc = mv.lower()
    guessed_type = 'NORMAL'
    for t, kws in kw_type.items():
        for kw in kws:
            if kw in mv_lc:
                guessed_type = t
                break
        if guessed_type != 'NORMAL' and guessed_type in kw_type:
            break
    # guess power
    guessed_power = 50
    for kw, p in kw_power.items():
        if kw in mv_lc:
            guessed_power = p
            break
    # avg level heuristic
    guessed_avg = 20
    if 'EMBER' in mv or 'TACKLE' in mv or 'GROWL' in mv or 'QUICK' in mv:
        guessed_avg = 5
    elif 'EDGE' in mv or 'HYPER' in mv or 'GIGA' in mv or 'OUTRAGE' in mv:
        guessed_avg = 50
    elif 'BLAST' in mv or 'BEAM' in mv or 'BOLT' in mv or 'PUMP' in mv:
        guessed_avg = 36

    new_entries[mv] = {
        'move': mv,
        'type': guessed_type,
        'power': guessed_power,
        'avg_level': guessed_avg
    }

# write merged DB back sorted by name
out = [new_entries[k] for k in sorted(new_entries.keys())]
with open(DB_PATH, 'w') as f:
    json.dump(out, f, indent=2, sort_keys=False)

print(f"Regenerated moves_db.json with {len(out)} moves (incl. existing). Saved to {DB_PATH}")
