#!/usr/bin/env python3
"""Generate moves_db.json by parsing evos_attacks.asm level-up learnsets."""
import re, json
from pathlib import Path

ASM_PATH = Path('/Users/max/Documents/pokewilds/pokemon/credited/backup data 8-21-2021/evos_attacks.asm')
OUT_PATH = Path(__file__).parent / '..' / 'moves_db.json'
OUT_PATH = OUT_PATH.resolve()

# load existing DB if present to preserve metadata
existing = {}
if OUT_PATH.exists():
    try:
        with open(OUT_PATH) as f:
            for e in json.load(f):
                existing[e['move'].upper()] = e
    except Exception:
        existing = {}

moves = set()
line_re = re.compile(r'^\s*db\s+(\d+)\s*,\s*([A-Z0-9_]+)')
# also accept lines like: db 1, MOVE
# Skip evolution directives (EVOLVE_LEVEL/ITEM) which don't start with numeric first arg

if not ASM_PATH.exists():
    print(f"Error: asm file not found: {ASM_PATH}")
    raise SystemExit(2)

with open(ASM_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    for ln in f:
        m = line_re.match(ln)
        if not m:
            continue
        lvl = int(m.group(1))
        tok = m.group(2).strip()
        # filter out non-move tokens that appear (e.g., 0 or labels)
        if tok in ('0',):
            continue
        # Some entries may be Pokemon names or other directives; but most are moves
        moves.add(tok.upper())

print(f"Found {len(moves)} unique move tokens from ASM")

# heuristics for type/power/avg_level (reuse previous keyword maps)
kw_type = {
    'FIRE': ['FIRE','FLAME','EMBER','BLAZE','INFERNO','FLARE','SACRED_FIRE','FLAME_WHEEL','BLAZE'],
    'WATER': ['WATER','HYDRO','SURF','BUBBLE','WHIRL','AQUA','WATERFALL','HYDRO'],
    'GRASS': ['LEAF','VINE','RAZOR','SOLAR','GIGA_DRAIN','SYNTHESIS','MEGA_DRAIN'],
    'ELECTRIC': ['THUNDER','VOLT','SPARK','ZAP','ELECTRO','CHARGE'],
    'ICE': ['ICE','BLIZZARD','POWDER','POWDER_SNOW'],'GROUND': ['EARTH','DIG','QUAKE','BULLDOZE','EARTHQUAKE'],
    'ROCK': ['ROCK','STONE','STONE_EDGE','SMASH'],
    'FIGHTING': ['FIGHT','PUNCH','KICK','KARATE','HAMMER','BRICK','ROLLING_KICK','LOW_KICK'],
    'POISON': ['POISON','SLUDGE','TOXIC'],
    'PSYCHIC': ['PSY','PSYBEAM','PSYCHIC','ZEN'],
    'GHOST': ['GHOST','SHADOW','ASTONISH','NIGHT_SHADE'],
    'BUG': ['BUG','LEECH','TWINEEDLE','FURY_CUTTER','STRING_SHOT'],
    'DRAGON': ['DRAGON','OUTRAGE'],
    'STEEL': ['IRON','METAL','HEAVY','METAL_CLAW','IRON_HEAD'],
    'FLYING': ['FLY','WING','PECK','DRILL','AERIAL','AEROBLAST'],
    'DARK': ['BITE','CRUNCH','DARK','Faint_ATTACK','FAINT_ATTACK','NIGHT_SLASH'],
    'NORMAL': ['TACKLE','SLASH','RETURN','HYPER_BEAM','DOUBLE_EDGE','TAKE_DOWN','POUND','BODY_SLAM','SLAM']
}
kw_power = {
    'BLAST':110,'FLAME':90,'BEAM':90,'HYDRO':110,'SURF':90,'PUMP':110,'ICE':90,'BLIZZARD':110,
    'STRIKE':75,'PUNCH':75,'KICK':75,'EDGE':120,'HYPER':150,'RETURN':70,'TACKLE':40,'BITE':60,'SLASH':70,
    'ROCK':75,'EARTHQUAKE':100,'DRAGON':80
}

out = []
for mv in sorted(moves):
    if mv in existing:
        out.append(existing[mv])
        continue
    mv_lc = mv.lower()
    guessed_type = 'NORMAL'
    for t,kws in kw_type.items():
        for kw in kws:
            if kw.lower() in mv_lc:
                guessed_type = t
                break
        if guessed_type != 'NORMAL':
            break
    guessed_power = 50
    for kw,p in kw_power.items():
        if kw.lower() in mv_lc:
            guessed_power = p
            break
    guessed_avg = 20
    if any(x in mv for x in ('EMBER','TACKLE','GROWL','QUICK','TAIL_WHIP','GROWL','LEER')):
        guessed_avg = 5
    elif any(x in mv for x in ('EDGE','HYPER','GIGA','OUTRAGE','CRUSH','GIGANTAMAX')):
        guessed_avg = 50
    elif any(x in mv for x in ('BLAST','BEAM','BOLT','PUMP','SURF')):
        guessed_avg = 36
    out.append({'move': mv, 'type': guessed_type, 'power': guessed_power, 'avg_level': guessed_avg})

with open(OUT_PATH, 'w') as f:
    json.dump(out, f, indent=2)

print(f"Wrote {len(out)} moves to {OUT_PATH}")
