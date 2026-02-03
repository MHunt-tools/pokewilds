#!/usr/bin/env python3
"""
PokeGen Web Application
Web UI for creating custom Pokémon mods for PokeWilds
"""

import traceback
from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
import secrets
import json
import base64
import io
import sys
from pokemon_mod_generator import PokemonModGenerator, PokemonStats

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global generator instance
generator = None
sprite_gen = None


def get_generator():
    """Get or create mod generator"""
    global generator
    if generator is None:
        # Prefer an existing mods directory in known locations.
        app_dir = Path(__file__).parent
        candidates = [
            app_dir.parent / "mods",  # ../mods (workspace root)
            Path.home() / "Documents" / "pokewilds" / "mods",  # ~/Documents/pokewilds/mods
            Path.home() / "pokewilds" / "mods",  # ~/pokewilds/mods
        ]
        mods_dir = None
        for c in candidates:
            if c.exists():
                mods_dir = c
                break
        if mods_dir is None:
            # fallback to workspace-relative ../mods
            mods_dir = app_dir.parent / "mods"
            mods_dir.mkdir(parents=True, exist_ok=True)
        generator = PokemonModGenerator(mods_dir)
    return generator


def get_sprite_generator():
    """Lazy-load sprite generator (optional)"""
    global sprite_gen
    
    if sprite_gen is False:  # Already tried and failed
        return None
    
    if sprite_gen is None:
        try:
            from sprite_generator import SpriteGenerator
            sprite_gen = SpriteGenerator(device="cpu", low_memory=True)
            print("✓ Sprite generator loaded")
        except ImportError as e:
            print(f"✗ Sprite generator not available: {e}")
            sprite_gen = False  # Mark as unavailable
            return None
    
    return sprite_gen if sprite_gen is not False else None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/create', methods=['POST'])
def create_pokemon():
    """Create a new Pokémon mod"""
    try:
        data = request.json
        print("[DEBUG] Incoming /api/create data:", data)

        # Validate required fields
        required = ['name', 'dex', 'type1']
        for field in required:
            if field not in data:
                print(f"[ERROR] Missing field: {field}")
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

        # Parse parameters
        name = data['name'].strip()
        # dex may be null/empty to auto-assign
        dex_raw = data.get('dex')
        if dex_raw is None or dex_raw == '':
            dex = None
        else:
            dex = int(dex_raw)
        type1 = data['type1'].upper()
        type2 = data.get('type2', '').upper() or None

        stats = PokemonStats(
            hp=int(data.get('hp', 45)),
            attack=int(data.get('attack', 49)),
            defense=int(data.get('defense', 49)),
            sp_atk=int(data.get('sp_atk', 65)),
            sp_def=int(data.get('sp_def', 65)),
            speed=int(data.get('speed', 45))
        )

        ability1 = data.get('ability1', 'STATIC').upper()
        ability2 = data.get('ability2', '').upper() or None
        gender = int(data.get('gender', 50))
        template = data.get('template', '').lower() or None

        gen = get_generator()
        # Generate moveset
        moveset = gen.pick_moveset(type1, type2, stats)

        # Create mod files (this will also attempt AI sprite generation if available)
        try:
            success = gen.create_pokemon(
                name=name,
                dex_number=dex,
                type1=type1,
                type2=type2,
                stats=stats,
                ability1=ability1,
                ability2=ability2,
                gender_ratio=gender,
                template_pokemon=template,
                sprite_prompt=data.get('sprite_prompt'),
                sprite_steps=int(data.get('sprite_steps')) if data.get('sprite_steps') is not None else None
            )
        except Exception as e:
            print(f"[ERROR] Exception in create_pokemon: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Exception in create_pokemon: {e}'}), 500

        # Ensure sprite saved and create preview
        sprite_b64 = None
        if success:
            try:
                sprite_gen = get_sprite_generator()
                if sprite_gen is not None:
                    prompt = data.get('sprite_prompt') or f"{name} {type1.lower()} pokemon"
                    steps = int(data.get('sprite_steps', 20))
                    mod_dir = gen.output_dir / name / "graphics"
                    sprite_path = mod_dir / "front.png"
                    # Regenerate or overwrite front sprite to ensure prompt applied
                    sprite_gen.generate_and_save(prompt=prompt, output_path=sprite_path, num_inference_steps=steps)
                    preview_path = mod_dir / "front_96.png"
                    if preview_path.exists():
                        with open(preview_path, 'rb') as f:
                            sprite_b64 = 'data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')
            except Exception as e:
                print(f"[ERROR] Sprite generation/preview failed: {e}")
                traceback.print_exc()

        if success:
            assigned_dex = getattr(gen, 'last_dex_number', dex)
            print(f"[DEBUG] Successfully created Pokémon: {name} (#{assigned_dex})")
            return jsonify({
                'success': True,
                'message': f'Created Pokémon: {name} (#{assigned_dex})',
                'pokemon': {
                    'name': name,
                    'dex': assigned_dex,
                    'type1': type1,
                    'type2': type2,
                    'types': f"{type1}" + (f"/{type2}" if type2 else ""),
                    'moveset': [ {'level': lvl, 'move': move} for lvl, move in moveset ],
                    'sprite': sprite_b64
                }
            })
        else:
            print(f"[ERROR] Failed to create Pokémon: {name}")
            return jsonify({'success': False, 'error': 'Failed to create Pokémon'}), 500

    except Exception as e:
        print(f"[ERROR] Unhandled exception in /api/create: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

        


@app.route('/api/sprite-available', methods=['GET'])
def sprite_available():
    """Check if sprite generator is available"""
    gen = get_sprite_generator()
    return jsonify({'available': gen is not None})


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({'error': str(e)}), 500


def main():
    """Run the web application"""
    print("=" * 60)
    print("PokeGen - Pokémon Mod Creator for PokeWilds")
    print("=" * 60)
    print()
    print("Starting web server...")
    print("Open browser to: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Check for sprite generator
    gen = get_sprite_generator()
    if gen:
        print("✓ Sprite generator available")
    else:
        print("⚠ Sprite generator not available (optional)")
        print("  Install with: pip install diffusers transformers torch accelerate")
    
    print()
    
    # Run app
    app.run(debug=True, host='localhost', port=5000)


if __name__ == '__main__':
    main()
