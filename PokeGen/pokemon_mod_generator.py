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
from PIL import Image


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
    """Generate custom Pokémon mod files for PokeWilds"""
    
    # Type mappings for Pokemon Crystal ASM format
    TYPE_MAP = {
        'NORMAL': 0, 'FLYING': 1, 'POISON': 2, 'GROUND': 3, 'ROCK': 4,
        'BUG': 5, 'GHOST': 6, 'STEEL': 7, 'FIRE': 8, 'WATER': 9,
        'GRASS': 10, 'ELECTRIC': 11, 'PSYCHIC': 12, 'ICE': 13, 'DRAGON': 14,
        'DARK': 15, 'FAIRY': 16
    }
    
    # Ability mappings
    ABILITY_MAP = {
        'STATIC': 9, 'LIGHTNING_ROD': 31, 'VOLT_ABSORB': 10,
        'OVERGROW': 65, 'CHLOROPHYLL': 34, 'RAINDISH': 44,
        'TORRENT': 67, 'SWIFT_SWIM': 33, 'BLAZE': 66,
        'FLASH_FIRE': 18, 'STATIC': 9, 'VITAL_SPIRIT': 72
    }
    
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
        dex_number: int,
        type1: str,
        type2: Optional[str] = None,
        stats: Optional[PokemonStats] = None,
        ability1: str = "STATIC",
        ability2: Optional[str] = None,
        gender_ratio: int = 50,
        template_pokemon: Optional[str] = None,
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
            moves_asm = self._generate_evos_attacks_asm(name, dex_number)
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
    
    def _generate_evos_attacks_asm(self, name: str, dex: int) -> str:
        """Generate Pokemon Crystal evolutions and moves file"""
        
        asm = f"""; {name} Evolutions and Moves
; Auto-generated by PokeGen

; Evolutions (none for custom Pokémon)
db  0  ; No evolutions defined

; Learnset (basic moves)
db  TACKLE,  1
db  GROWL,   1
db  0, 0    ; End learnset
"""
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
