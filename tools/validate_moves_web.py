#!/usr/bin/env python3
"""
Validate and (optionally) fix move `type` values in PokeGen/moves_db.json
by querying Pokemondb.net and Bulbapedia. Designed to be run locally where
internet access is available.

Usage:
  python3 tools/validate_moves_web.py [--apply]

Options:
  --apply   : update PokeGen/moves_db.json with types discovered on the web

Notes:
- Requires: requests, beautifulsoup4, lxml
  pip install requests beautifulsoup4 lxml
- Network errors will be reported; script will not change files unless --apply is passed.
"""

import json
import re
import sys
import time
from urllib.parse import quote

try:
    import requests
    from bs4 import BeautifulSoup
except Exception as e:
    print('Missing dependency:', e)
    print('Run: pip install requests beautifulsoup4 lxml')
    sys.exit(1)

MOVES_PATH = 'PokeGen/moves_db.json'
HEADERS = {
    'User-Agent': 'PokeGen/validate-moves (+https://example.com)'
}


def load_moves():
    with open(MOVES_PATH, 'r') as f:
        return json.load(f)


def slug_for_pokemondb(move_name):
    # move_name like 'AURORA_BEAM' or 'U_TURN' -> 'aurora-beam' or 'u-turn'
    name = move_name.replace('_', ' ').lower()
    name = name.replace("'", '')
    name = re.sub(r'[^a-z0-9\s\-]', '', name)
    slug = re.sub(r'\s+', '-', name)
    return slug


def fetch_pokemondb_type(move_name):
    slug = slug_for_pokemondb(move_name)
    url = f'https://pokemondb.net/move/{quote(slug)}'
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, 'lxml')
    # try to find the vitals table row with 'Type'
    table = soup.find('table', class_='vitals-table')
    if table:
        for tr in table.find_all('tr'):
            th = tr.find('th')
            if th and 'Type' in th.text:
                td = tr.find('td')
                if td:
                    a = td.find('a')
                    if a:
                        return a.text.strip().upper()
                    return td.text.strip().upper()
    # fallback: find first element with class 'type-icon' and get text
    a = soup.find('a', class_='type-icon')
    if a:
        return a.text.strip().upper()
    return None


def slug_for_bulbapedia(move_name):
    # Bulbapedia uses Title_Case with underscores; special cases exist.
    parts = move_name.split('_')
    parts = [p.capitalize() for p in parts]
    return '_'.join(parts)


def fetch_bulbapedia_type(move_name):
    title = slug_for_bulbapedia(move_name)
    url = f'https://bulbapedia.bulbagarden.net/wiki/{quote(title)}_(move)'
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        # Try without suffix
        url2 = f'https://bulbapedia.bulbagarden.net/wiki/{quote(title)}'
        r = requests.get(url2, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
    soup = BeautifulSoup(r.text, 'lxml')
    # Bulbapedia uses an infobox table; look for th with 'Type' then the following td
    infobox = soup.find('table', class_='roundy') or soup.find('table', class_='toccolours')
    if infobox:
        for th in infobox.find_all('th'):
            if th.text and 'Type' in th.text:
                td = th.find_next_sibling('td')
                if td:
                    a = td.find('a')
                    if a:
                        return a.text.strip().upper()
                    return td.text.strip().upper()
    # fallback: search for 'Type' label anywhere
    for strong in soup.find_all(['th','strong']):
        if strong.text and 'Type' in strong.text:
            nxt = strong.find_next()
            if nxt:
                return nxt.text.strip().upper()
    return None


def determine_move_type(move_name):
    # try Pokemondb first (usually reliable), then Bulbapedia
    try:
        t = fetch_pokemondb_type(move_name)
        if t:
            return t
    except Exception:
        pass
    try:
        t = fetch_bulbapedia_type(move_name)
        if t:
            return t
    except Exception:
        pass
    return None


def main():
    moves = load_moves()
    mismatches = []
    updates = {}
    for entry in moves:
        move = entry.get('move')
        local_type = entry.get('type', '').upper()
        found = determine_move_type(move)
        if found is None:
            print(f'?: {move} -> not found online')
        else:
            if found != local_type:
                mismatches.append((move, local_type, found))
                updates[move] = found
                print(f'DIFF: {move}: local={local_type} web={found}')
            else:
                print(f'OK:   {move}: {local_type}')
        # be gentle to remote sites
        time.sleep(0.5)
    print('\nSummary:')
    print(f'  total moves checked: {len(moves)}')
    print(f'  mismatches found: {len(mismatches)}')

    if '--apply' in sys.argv and updates:
        # apply updates to file
        for e in moves:
            mv = e.get('move')
            if mv in updates:
                e['type'] = updates[mv]
        with open(MOVES_PATH, 'w') as f:
            json.dump(moves, f, indent=2, sort_keys=False)
        print('Applied updates to', MOVES_PATH)

if __name__ == '__main__':
    main()
