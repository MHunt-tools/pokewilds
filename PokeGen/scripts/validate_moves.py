#!/usr/bin/env python3
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pokemon_mod_generator import PokemonModGenerator

DB = Path(__file__).parent / '..' / 'moves_db.json'
DB = DB.resolve()

if not DB.exists():
    print(f"ERROR: moves_db.json not found at {DB}")
    sys.exit(2)

with open(DB) as f:
    try:
        data = json.load(f)
    except Exception as e:
        print(f"ERROR: could not parse JSON: {e}")
        sys.exit(2)

errors = []
seen = {}
for i, entry in enumerate(data):
    name = str(entry.get('move', '')).upper().strip()
    typ = str(entry.get('type', 'NONE')).upper().strip()
    power = entry.get('power')
    avg = entry.get('avg_level')

    if not name:
        errors.append(f"entry[{i}]: missing move name")
        continue
    if name in seen:
        errors.append(f"duplicate move name '{name}' (entries {seen[name]} and {i})")
    else:
        seen[name] = i
    if not re.match(r'^[A-Z0-9_]+$', name):
        errors.append(f"move '{name}' contains unexpected characters")
    if typ not in PokemonModGenerator.TYPE_MAP:
        errors.append(f"move '{name}' has unknown type '{typ}'")
    if not isinstance(power, (int, float)):
        errors.append(f"move '{name}' has invalid power: {power}")
    else:
        if power < 0 or power > 1000:
            errors.append(f"move '{name}' has suspicious power: {power}")
    if not isinstance(avg, (int, float)):
        errors.append(f"move '{name}' has invalid avg_level: {avg}")
    else:
        if not (1 <= avg <= 100):
            errors.append(f"move '{name}' has avg_level out of range: {avg}")

print("=== moves_db.json validation ===")
if errors:
    for e in errors:
        print(e)
else:
    print("OK - no issues found")
print(f"\nSummary: {len(data)} moves checked, {len(errors)} issues found.")
