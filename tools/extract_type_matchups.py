#!/usr/bin/env python3
import subprocess, re, json, sys, os

def run_javap():
    p = subprocess.run(['javap','-c','-classpath','.','com.pkmngen.game.Battle'], capture_output=True, text=True)
    if p.returncode != 0:
        print('ERROR: javap failed:', p.stderr)
        sys.exit(1)
    return p.stdout.splitlines()


def parse(lines):
    str_re = re.compile(r"ldc(?:_w)?\s+#\d+\s+//\s+String\s+(.+)$")
    float_const_re = re.compile(r'Float\s+([0-9]+\.?[0-9]*)f')
    matchups = {}
    current_attack = None
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        m = str_re.search(line)
        if m:
            s = m.group(1).strip()
            # lookahead block
            look = '\n'.join(lines[i:i+8])
            if 'new           #59' in look or 'new           #59                 // class java/util/HashMap' in look:
                # new inner map for attack type
                current_attack = s.lower()
                matchups.setdefault(current_attack, {})
                i += 1
                continue
            # otherwise possible defender entry for current attack
            if current_attack is not None:
                # search ahead for Float.valueOf within next 12 lines
                snippet = '\n'.join(lines[i:i+12])
                if 'Float.valueOf' in snippet:
                    # find float literal in window
                    fv = None
                    for j in range(i, min(i+12, n)):
                        lj = lines[j]
                        if 'fconst_' in lj:
                            if 'fconst_0' in lj:
                                fv = 0.0
                            elif 'fconst_1' in lj:
                                fv = 1.0
                            elif 'fconst_2' in lj:
                                fv = 2.0
                            break
                        m2 = float_const_re.search(lj)
                        if m2:
                            try:
                                fv = float(m2.group(1))
                                break
                            except:
                                pass
                        if 'ldc2_w' in lj and 'Float' in lj:
                            m3 = float_const_re.search(lj)
                            if m3:
                                fv = float(m3.group(1))
                                break
                    # fallback search previous lines for Float constant comments
                    if fv is None:
                        for k in range(max(0,i-8), i):
                            m3 = float_const_re.search(lines[k])
                            if m3:
                                fv = float(m3.group(1))
                                break
                    if fv is None:
                        # couldn't determine float, skip
                        i += 1
                        continue
                    defender = s.lower()
                    matchups[current_attack][defender] = fv
                    i += 1
                    continue
        i += 1
    return matchups


def main():
    cwd = os.getcwd()
    print('cwd=', cwd)
    lines = run_javap()
    matchups = parse(lines)
    outdir = os.path.join('PokeGen')
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, 'type_matchups.json')
    with open(outpath, 'w') as f:
        json.dump(matchups, f, indent=2, sort_keys=True)
    cnt_atk = len(matchups)
    cnt_pairs = sum(len(v) for v in matchups.values())
    print('WROTE', outpath)
    print(f'attack types: {cnt_atk}, total pairs: {cnt_pairs}')

if __name__ == '__main__':
    main()
