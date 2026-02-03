import re
from collections import defaultdict

MOVES_PATH = '../pokewilds/pokemon/moves.asm'
EVOS_ATTACKS_PATH = '../pokewilds/pokemon/credited/evos_attacks.asm'

# Parse moves.asm for move type and power
def parse_moves():
    moves = {}
    with open(MOVES_PATH, 'r') as f:
        for line in f:
            m = re.match(r'\s*move ([A-Z0-9_]+),\s*[^,]+,\s*([0-9]+),\s*([A-Z_]+),', line)
            if m:
                move, power, type_ = m.group(1), int(m.group(2)), m.group(3)
                moves[move] = {'type': type_, 'power': power}
    return moves

# Parse evos_attacks.asm for move learn levels
def parse_learn_levels():
    move_levels = defaultdict(list)
    with open(EVOS_ATTACKS_PATH, 'r', encoding='latin-1') as f:
        for line in f:
            m = re.match(r'\s*db ([0-9]+), ([A-Z0-9_]+)', line)
            if m:
                level, move = int(m.group(1)), m.group(2)
                move_levels[move].append(level)
    return move_levels

def build_move_db():
    moves = parse_moves()
    move_levels = parse_learn_levels()
    move_db = defaultdict(list)
    for move, info in moves.items():
        levels = move_levels.get(move, [])
        avg_level = sum(levels) / len(levels) if levels else None
        move_db[info['type']].append({
            'move': move,
            'power': info['power'],
            'avg_level': avg_level
        })
    return move_db

if __name__ == '__main__':
    import json
    db = build_move_db()
    with open('move_db.json', 'w') as f:
        json.dump(db, f, indent=2)
    print('Move DB written to move_db.json')
