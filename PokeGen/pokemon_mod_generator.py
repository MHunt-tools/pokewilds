#!/usr/bin/env python3
"""
PokeGen - Pokémon Mod Generator for PokeWilds
Programmatically create custom Pokémon mods without recompiling the JAR
"""

import argparse
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
import shutil
import json
from functools import lru_cache
from PIL import Image
import traceback


@dataclass
class PokemonStats:
    """Base stats for a Pokémon"""
    hp: int = 45
    attack: int = 49
    defense: int = 49
    sp_atk: int = 65
    sp_def: int = 65
    speed: int = 45


class PokemonModGenerator:
    # Moveset selection tuning
    MOVESET_MEAN = 15.66
    MOVESET_STDDEV = 4.15
    # Type preference: 'mild' (weighted) or 'strict' (guarantee fraction of same-type moves)
    TYPE_PREFERENCE_MODE = 'strict'
    STRICT_TYPE_SHARE = 0.6
    # Basic type mapping (game-specific numeric type IDs)
    TYPE_MAP = {
        'NORMAL': 0,
        'FIGHTING': 1,
        'FLYING': 2,
        'POISON': 3,
        'GROUND': 4,
        'ROCK': 5,
        'BUG': 6,
        'GHOST': 7,
        'STEEL': 8,
        'FIRE': 9,
        'WATER': 10,
        'GRASS': 11,
        'ELECTRIC': 12,
        'PSYCHIC': 13,
        'ICE': 14,
        'DRAGON': 15,
        'DARK': 16,
        'FAIRY': 17,
        'NONE': 0,
    }
    # Basic ability mapping (placeholder values)
    ABILITY_MAP = {
        'STATIC': 1,
        'INTIMIDATE': 2,
        'BLAZE': 3,
        'TORRENT': 4,
        'SHIELD_DUST': 5,
        'RUN_AWAY': 6,
        'SYNCHRONIZE': 7,
        'LEVITATE': 8,
    }
    def _load_moves_db(self):
        db_path = Path(__file__).parent / 'moves_db.json'
        if db_path.exists():
            try:
                with open(db_path, 'r') as fh:
                    return json.load(fh)
            except Exception:
                return []
        return []

    @lru_cache(maxsize=1)
    def _moves_db(self):
        return self._load_moves_db()

    def pick_moveset(self, type1, type2, stats):
            """Generate a moveset based on type(s) and strength

            Rules:
            - Determine desired number of moves from MOVESET_MEAN +/- BST-derived offset
            - Prefer moves that match primary/secondary type
            - Stronger Pokémon (higher BST) favor higher-power moves
            - We produce unique moves; if pool is small we sample with replacement
            """
            # Load move DB (fallback to small built-in list)
            db = self._moves_db() or [
                {'move': 'TACKLE', 'type': 'NORMAL', 'power': 40, 'avg_level': 1},
                {'move': 'GROWL', 'type': 'NORMAL', 'power': 0, 'avg_level': 3},
                {'move': 'QUICK_ATTACK', 'type': 'NORMAL', 'power': 40, 'avg_level': 10},
                {'move': 'BITE', 'type': 'DARK', 'power': 60, 'avg_level': 15},
                {'move': 'HYPER_BEAM', 'type': 'NORMAL', 'power': 150, 'avg_level': 50},
            ]

            # Compute total stats and k (strength factor)
            total_stats = stats.hp + stats.attack + stats.defense + stats.sp_atk + stats.sp_def + stats.speed
            mean_bst = 325
            k = (total_stats - mean_bst) / 60.0

            # Desired number of moves (use configured mean/stddev), clamp to reasonable range
            n_moves = int(round(self.MOVESET_MEAN + k * self.MOVESET_STDDEV))
            n_moves = max(3, min(12, n_moves))

            # Build candidate pool: include moves that match either type or are neutral
            t1 = (type1 or 'NONE').upper()
            t2 = (type2 or '').upper()
            candidates = []
            for m in db:
                m_type = (m.get('type') or 'NONE').upper()
                # score base on type match (will be used later as weight)
                candidates.append({
                    'move': m.get('move').upper(),
                    'type': m_type,
                    'power': int(m.get('power', 0)),
                    'avg_level': int(m.get('avg_level', 1))
                })

            # If the DB is very small, also attempt to pull from attacks/ folder names
            if len(candidates) < 8:
                attacks_dir = Path(__file__).parent.parent / "attacks"
                if attacks_dir.exists():
                    for entry in attacks_dir.iterdir():
                        if entry.is_dir():
                            name = entry.name.split('_')[0].upper()
                            candidates.append({'move': name, 'type': 'NORMAL', 'power': 50, 'avg_level': 20})

            # Remove exact duplicates while preserving one instance
            seen = set()
            unique = []
            for c in candidates:
                if c['move'] not in seen:
                    unique.append(c)
                    seen.add(c['move'])

            # Extremely strict behavior: only allow moves that are the primary type
            # or the default 'NORMAL' type. If this filter would produce an empty
            # pool, fall back to the unfiltered list to avoid failures.
            if t1 and t1 != 'NONE':
                allowed = {t1, 'NORMAL'}
                strict_unique = [c for c in unique if c.get('type') in allowed]
                if strict_unique:
                    unique = strict_unique

            import random

            # Compute weights for sampling
            weights = []
            for c in unique:
                w = 1.0
                # Type match multiplier (base weighted preference)
                if c['type'] == t1 or (t2 and c['type'] == t2):
                    w *= 3.0
                # Power influence: strong Pokémon favor higher-power moves
                power = c.get('power', 0)
                if k >= 0:
                    w *= 1.0 + (power / 150.0) * (1.0 + k)
                else:
                    w *= 1.0 + (power / 150.0) * max(0.2, 1.0 + k)
                # Slight bias toward moves learned earlier for variety
                w *= 1.0 + max(0.0, (50 - c.get('avg_level', 50)) / 200.0)
                weights.append(max(0.01, w))

            # Helper: weighted pick without replacement among indices
            def weighted_pick(indices, wlist, count):
                picks = []
                idx_pool = indices.copy()
                w_pool = [wlist[i] for i in idx_pool]
                while len(picks) < count and idx_pool:
                    total_w = sum(w_pool)
                    if total_w <= 0:
                        i = random.randrange(len(idx_pool))
                    else:
                        r = random.random() * total_w
                        upto = 0.0
                        i = 0
                        for j, w in enumerate(w_pool):
                            upto += w
                            if r <= upto:
                                i = j
                                break
                    picks.append(idx_pool.pop(i))
                    w_pool.pop(i)
                return picks

            moveset = []

            # Strict preference mode: guarantee fraction of moves match types
            if self.TYPE_PREFERENCE_MODE == 'strict':
                required_same = max(1, int(n_moves * self.STRICT_TYPE_SHARE))
                same_idxs = [i for i, c in enumerate(unique) if c['type'] == t1 or (t2 and c['type'] == t2)]
                other_idxs = [i for i in range(len(unique)) if i not in same_idxs]

                # Pick required same-type moves first (weighted by weights)
                same_picks = weighted_pick(same_idxs, weights, required_same)
                for idx in same_picks:
                    moveset.append(unique[idx])

                # Fill the rest from others (weighted), excluding already picked
                remaining = n_moves - len(moveset)
                available_idxs = [i for i in range(len(unique)) if i not in same_picks]
                other_picks = weighted_pick(available_idxs, weights, remaining)
                for idx in other_picks:
                    moveset.append(unique[idx])
            else:
                # Mild/default behavior: weighted sampling across all moves
                all_idxs = list(range(len(unique)))
                picked = weighted_pick(all_idxs, weights, n_moves)
                for idx in picked:
                    moveset.append(unique[idx])

            # If still short (very small db), sample with replacement until full
            while len(moveset) < n_moves and unique:
                moveset.append(random.choice(unique))

            # Assign levels: base on move.avg_level but spread across progression
            levels = []
            for i, m in enumerate(moveset):
                base = m.get('avg_level', 1)
                # Add small randomness and bias earlier moves toward lower levels
                jitter = random.randint(-3, 5)
                lvl = int(max(1, min(100, base + jitter)))
                levels.append(lvl)

            # Ensure ascending and unique levels for cleanliness
            levels = sorted(levels)
            for i in range(len(levels)):
                if i > 0 and levels[i] <= levels[i-1]:
                    levels[i] = min(100, levels[i-1] + 1)

            return list(zip(levels, [m['move'] for m in moveset]))
    def _find_next_available_dex_number(self):
        import re
        used = set()
        # Scan base game
        base_stats_dir = Path(__file__).parent.parent / "pokemon" / "base_stats"
        if base_stats_dir.exists():
            for f in base_stats_dir.glob("*.asm"):
                with open(f, "r") as fh:
                    line = fh.readline()
                    m = re.search(r';\s*(\d+)', line)
                    if m:
                        used.add(int(m.group(1)))
        # Scan mods
        mods_dir = Path(__file__).parent.parent / "mods"
        if mods_dir.exists():
            for cfg in mods_dir.glob("*/pokemon.cfg"):
                with open(cfg, "r") as fh:
                    for line in fh:
                        m = re.match(r'dex_number\s*=\s*(\d+)', line)
                        if m:
                            used.add(int(m.group(1)))
        # Find next available
        n = 1
        while n in used:
            n += 1
        return n
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize generator with optional output directory"""
        if output_dir is None:
            # Try to find mods directory relative to parent pokewilds
            current = Path(__file__).parent
            pokewilds_parent = current.parent
            output_dir = pokewilds_parent / "mods"
            
            if not output_dir.exists():
                output_dir = Path.home() / "pokewilds" / "mods"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_pokemon(
        self,
        name: str,
        dex_number: Optional[int],
        type1: str,
        type2: Optional[str] = None,
        stats: Optional[PokemonStats] = None,
        ability1: str = "STATIC",
        ability2: Optional[str] = None,
        gender_ratio: int = 50,
        template_pokemon: Optional[str] = None,
        sprite_prompt: Optional[str] = None,
        sprite_steps: Optional[int] = None,
    ) -> bool:
        """
        Create a new Pokémon mod
        
        Args:
            name: Pokémon name (for mod directory)
            dex_number: National Pokédex number
            type1: Primary type (FIRE, WATER, GRASS, etc.)
            type2: Secondary type (optional)
            stats: PokemonStats object (uses defaults if None)
            ability1: Primary ability
            ability2: Secondary ability (optional)
            gender_ratio: 0-100 (0=always male, 100=always female)
            template_pokemon: Copy sprites from this Pokémon (e.g., 'pikachu')
        
        Returns:
            True if successful, False otherwise
        """
        
        if stats is None:
            stats = PokemonStats()

        # Auto-assign dex_number if not provided or 0/None
        if not dex_number:
            dex_number = self._find_next_available_dex_number()
        self.last_dex_number = dex_number

        # Create mod directory
        mod_dir = self.output_dir / name
        mod_dir.mkdir(exist_ok=True)

        # Create graphics directory
        graphics_dir = mod_dir / "graphics"
        graphics_dir.mkdir(exist_ok=True)
        
        try:
            # Generate sprite files
            if template_pokemon:
                self._copy_template_sprites(template_pokemon, graphics_dir)
            else:
                # Try to use AI sprite generator if available
                try:
                    from sprite_generator import SpriteGenerator
                    sprite_gen = SpriteGenerator(device="cpu", low_memory=True)
                    # Use custom prompt/steps if provided, else fallback
                    prompt = sprite_prompt or f"{name} {type1.lower()} pokemon"
                    steps = sprite_steps if sprite_steps is not None else 20
                    # Generate only the front sprite with AI
                    sprite_gen.generate_and_save(prompt=prompt, output_path=graphics_dir/"front.png", num_inference_steps=steps)
                    # For other sprites, use placeholders for now
                    for sprite_name in ["back.png", "front_shiny.png", "back_shiny.png"]:
                        sprite_path = graphics_dir / sprite_name
                        if not sprite_path.exists():
                            img = Image.new('RGBA', (96, 96), color=(200, 200, 200, 255))
                            img.save(sprite_path)
                except Exception as e:
                    print(f"AI sprite generation failed: {e}")
                    self._create_default_sprites(graphics_dir)
            
            # Generate ASM files
            asm_dir = mod_dir / "data" / "pokemon" / "dex_entries"
            asm_dir.mkdir(parents=True, exist_ok=True)
            
            # Create base stats file
            stats_asm = self._generate_base_stats_asm(
                name, dex_number, type1, type2, stats, ability1, ability2, gender_ratio
            )
            (asm_dir / f"{name.lower()}_base_stats.asm").write_text(stats_asm)
            
            # Create moves/evos file
            moves_asm = self._generate_evos_attacks_asm(name, dex_number, type1, type2, stats)
            (asm_dir / f"{name.lower()}_moves.asm").write_text(moves_asm)
            
            # Create config file
            config = self._generate_config(name, dex_number, type1, type2)
            (mod_dir / "pokemon.cfg").write_text(config)
            
            print(f"✓ Created Pokémon mod: {name}")
            print(f"  Location: {mod_dir}")
            print(f"  Dex #: {dex_number}")
            print(f"  Types: {type1}" + (f"/{type2}" if type2 else ""))
            print(f"  Stats: HP={stats.hp} Att={stats.attack} Def={stats.defense} " +
                  f"SpA={stats.sp_atk} SpD={stats.sp_def} Spe={stats.speed}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error creating Pokémon: {e}")
            return False
    
    def _generate_base_stats_asm(
        self, name: str, dex: int, type1: str, type2: Optional[str],
        stats: PokemonStats, ability1: str, ability2: Optional[str], gender_ratio: int
    ) -> str:
        """Generate Pokemon Crystal ASM base stats file"""
        
        type1_val = self.TYPE_MAP.get(type1.upper(), 0)
        type2_val = self.TYPE_MAP.get(type2.upper(), type1_val) if type2 else type1_val
        ability2_val = self.ABILITY_MAP.get(ability2.upper(), self.ABILITY_MAP.get(ability1.upper(), 0)) if ability2 else 0
        ability1_val = self.ABILITY_MAP.get(ability1.upper(), 0)
        
        asm = f"""; {name} Base Stats
; Auto-generated by PokeGen

db  {stats.hp:3d}            ; HP
db  {stats.attack:3d}        ; Attack
db  {stats.defense:3d}       ; Defense
db  {stats.sp_atk:3d}        ; Special Attack
db  {stats.sp_def:3d}        ; Special Defense
db  {stats.speed:3d}         ; Speed

db  {type1_val:<2d}, {type2_val:<2d}      ; Type1, Type2

db  {gender_ratio:<3d}       ; Gender ratio (0=always M, 100=always F)
db  {100:<3d}       ; Catch rate
db  {stats.hp * 2 + 5:<3d}   ; Base Experience (estimate)

db  GROWTH_MEDIUM_FAST  ; Growth rate
db  NO_ITEM             ; Item 1
db  NO_ITEM             ; Item 2

db  100                 ; Egg cycles

; Abilities
db  {ability1_val}, {ability2_val}
"""
        return asm.strip()
    
    def _generate_evos_attacks_asm(self, name: str, dex: int, type1=None, type2=None, stats=None) -> str:
        """Generate Pokemon Crystal evolutions and moves file, with generated moveset"""
        moveset = self.pick_moveset(type1, type2, stats or PokemonStats())
        asm = f"""; {name} Evolutions and Moves
; Auto-generated by PokeGen

; Evolutions (none for custom Pokémon)
db  0  ; No evolutions defined

; Learnset (generated moves)
"""
        for level, move in moveset:
            asm += f"db {level}, {move}\n"
        asm += "db 0, 0    ; End learnset\n"
        return asm.strip()
    
    def _generate_config(self, name: str, dex: int, type1: str, type2: Optional[str]) -> str:
        """Generate mod configuration file"""
        
        config = f"""# {name} Pokémon Configuration
# Auto-generated by PokeGen

[pokemon]
name = {name}
dex_number = {dex}
type1 = {type1.upper()}
type2 = {type2.upper() if type2 else "NONE"}
version = 1.0

[graphics]
sprite_front = graphics/front.png
sprite_back = graphics/back.png
sprite_front_shiny = graphics/front_shiny.png
sprite_back_shiny = graphics/back_shiny.png
"""
        return config.strip()
    
    def _copy_template_sprites(self, template: str, target_dir: Path):
        """Copy sprites from template Pokémon"""
        
        # Look for template in pokemon/sprites or pokewilds pokemon directory
        template_paths = [
            Path.home() / "pokewilds" / "pokemon" / f"{template.lower()}_*.png",
            self.output_dir.parent / "pokemon" / f"{template.lower()}_*.png",
        ]
        
        files_copied = 0
        for template_path in template_paths:
            for sprite_file in template_path.parent.glob(template_path.name):
                new_name = sprite_file.name.replace(template.lower(), "").lstrip("_")
                if not new_name:
                    new_name = "front.png"
                
                target_file = target_dir / new_name
                try:
                    shutil.copy2(sprite_file, target_file)
                    files_copied += 1
                except Exception as e:
                    print(f"  Warning: Could not copy {sprite_file}: {e}")
        
        if files_copied == 0:
            print(f"  Note: Template '{template}' sprites not found, creating defaults")
            self._create_default_sprites(target_dir)
    
    def _create_default_sprites(self, target_dir: Path):
        """Create default placeholder sprites"""
        
        sprite_names = ["front.png", "back.png", "front_shiny.png", "back_shiny.png"]
        
        for sprite_name in sprite_names:
            sprite_path = target_dir / sprite_name
            if not sprite_path.exists():
                # Create a 96x96 placeholder image
                img = Image.new('RGBA', (96, 96), color=(200, 200, 200, 255))
                img.save(sprite_path)


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='PokeGen - Create custom Pokémon mods for PokeWilds'
    )
    
    parser.add_argument('name', help='Pokémon name (mod directory name)')
    parser.add_argument('--dex', type=int, default=888, help='National Pokédex number (default: 888)')
    parser.add_argument('--type1', default='NORMAL', help='Primary type (FIRE, WATER, etc.)')
    parser.add_argument('--type2', help='Secondary type (optional)')
    parser.add_argument('--hp', type=int, default=45, help='HP stat (default: 45)')
    parser.add_argument('--att', type=int, default=49, help='Attack stat (default: 49)')
    parser.add_argument('--defense', type=int, default=49, help='Defense stat (default: 49)')
    parser.add_argument('--spa', type=int, default=65, help='Sp. Atk stat (default: 65)')
    parser.add_argument('--spd', type=int, default=65, help='Sp. Def stat (default: 65)')
    parser.add_argument('--spe', type=int, default=45, help='Speed stat (default: 45)')
    parser.add_argument('--ability1', default='STATIC', help='Primary ability')
    parser.add_argument('--ability2', help='Secondary ability')
    parser.add_argument('--gender', type=int, default=50, help='Gender ratio 0-100 (default: 50)')
    parser.add_argument('--template', help='Template Pokémon for sprites (e.g., pikachu)')
    parser.add_argument('--output', type=Path, help='Output directory (defaults to mods/)')
    
    args = parser.parse_args()
    
    gen = PokemonModGenerator(args.output)
    stats = PokemonStats(
        hp=args.hp, attack=args.att, defense=args.defense,
        sp_atk=args.spa, sp_def=args.spd, speed=args.spe
    )
    
    success = gen.create_pokemon(
        name=args.name,
        dex_number=args.dex,
        type1=args.type1,
        type2=args.type2,
        stats=stats,
        ability1=args.ability1,
        ability2=args.ability2,
        gender_ratio=args.gender,
        template_pokemon=args.template
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
