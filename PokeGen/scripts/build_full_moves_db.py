#!/usr/bin/env python3
"""Build a full moves_db.json from attacks/ folder plus existing DB metadata."""
import json, re
from pathlib import Path
ROOT = Path(__file__).parent.parent.parent
ATTACKS = ROOT / 'attacks'
DB_PATH = Path(__file__).parent / '..' / 'moves_db.json'
DB_PATH = DB_PATH.resolve()
print('DEBUG ROOT:', ROOT)
print('DEBUG ATTACKS path:', ATTACKS)
print('DEBUG ATTACKS exists:', ATTACKS.exists())

# load existing metadata
existing = {}
if DB_PATH.exists():
    try:
        with open(DB_PATH) as f:
            for e in json.load(f):
                existing[e['move'].upper()] = e
    except Exception:
        existing = {}

found = set()
if ATTACKS.exists():
    for entry in sorted(ATTACKS.iterdir()):
        n = entry.name
        n = re.sub(r'(_enemy(_gsc)?|_player(_gsc)?|_overworld|_setup|_sheet[0-9]*|_hit|_left|_right|_gsc)$','', n)
        n = re.sub(r'[^A-Za-z0-9]+','_', n).upper()
        if n:
            found.add(n)
print('DEBUG: found count before merging existing:', len(found))
print('DEBUG: sample found:', sorted(list(found))[:20])

# also include existing moves not in attacks
for mv in existing:
    found.add(mv)

# heuristics
kw_type = {
    'FIRE': ['fire','flame','ember','blaze','sacred_fire','flamethrower','flame_wheel','fire_blast'],
    'WATER': ['water','hydro','surf','bubble','whirlpool','water_gun','waterfall'],
    'GRASS': ['leaf','vine','solar','razor_leaf','giga_drain','synthesis'],
    'ELECTRIC': ['thunder','spark','volt','thundershock','thunderbolt'],
    'ICE': ['ice','powder','blizzard','powder_snow'],
    'GROUND': ['earth','dig','quake','earthquake'],
    'ROCK': ['rock','stone'],
    'FIGHTING': ['fight','karate','punch','kick','brick_break'],
    'POISON': ['poison','sludge','toxic'],
    'PSYCHIC': ['psy','psychic','psybeam'],
    'GHOST': ['ghost','shadow'],
    'BUG': ['bug','leech_life','twineedle'],
    'DRAGON': ['dragon','outrage','dragonbreath'],
    'STEEL': ['iron','steel'],
    'FLYING': ['fly','wing','peck','drill_peck'],
    'DARK': ['bite','crunch','dark','faint_attack'],
    'NORMAL': ['tackle','slash','return','hyper_beam','double_edge','take_down','pound']
}
kw_power = {
    'blast':110,'flame':90,'beam':90,'hydro':110,'surf':90,'pump':110,'ice':90,'blizzard':110,
    'strike':75,'punch':75,'kick':75,'edge':120,'hyper':150,'return':70,'tackle':40,'bite':60,'slash':70,
    'rock':75,'earthquake':100,'dragon':80
}

out = []
for mv in sorted(found):
    if mv in existing:
        out.append(existing[mv])
        continue
    mv_lc = mv.lower()
    guessed_type = 'NORMAL'
    for t,kws in kw_type.items():
        for kw in kws:
            if kw in mv_lc:
                guessed_type = t
                break
        if guessed_type != 'NORMAL':
            break
    guessed_power = 50
    for kw,p in kw_power.items():
        if kw in mv_lc:
            guessed_power = p
            break
    guessed_avg = 20
    if any(x in mv for x in ('EMBER','TACKLE','GROWL','QUICK')):
        guessed_avg = 5
    elif any(x in mv for x in ('EDGE','HYPER','GIGA','OUTRAGE')):
        guessed_avg = 50
    elif any(x in mv for x in ('BLAST','BEAM','BOLT','PUMP')):
        guessed_avg = 36
    out.append({'move': mv, 'type': guessed_type, 'power': guessed_power, 'avg_level': guessed_avg})

with open(DB_PATH, 'w') as f:
    json.dump(out, f, indent=2)

print(f'Wrote {len(out)} moves to {DB_PATH}')
