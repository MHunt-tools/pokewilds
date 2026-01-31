#!/usr/bin/env python3
"""
PokeGen Web Application
Web UI for creating custom Pokémon mods for PokeWilds
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
import secrets
import json
import base64
import io
import sys
import traceback
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
        # Find mods directory relative to app.py location
        app_dir = Path(__file__).parent
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
        
        # Validate required fields
        required = ['name', 'dex', 'type1']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Get parameters
        name = data['name'].strip()
        dex = int(data['dex'])
        type1 = data['type1'].upper()
        type2 = data.get('type2', '').upper() or None
        
        # Stats
        stats = PokemonStats(
            hp=int(data.get('hp', 45)),
            attack=int(data.get('attack', 49)),
            defense=int(data.get('defense', 49)),
            sp_atk=int(data.get('sp_atk', 65)),
            sp_def=int(data.get('sp_def', 65)),
            speed=int(data.get('speed', 45))
        )
        
        # Abilities and other stats
        ability1 = data.get('ability1', 'STATIC').upper()
        ability2 = data.get('ability2', '').upper() or None
        gender = int(data.get('gender', 50))
        template = data.get('template', '').lower() or None
        
        # Generate
        gen = get_generator()
        success = gen.create_pokemon(
            name=name,
            dex_number=dex,
            type1=type1,
            type2=type2,
            stats=stats,
            ability1=ability1,
            ability2=ability2,
            gender_ratio=gender,
            template_pokemon=template
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Created Pokémon: {name} (#{dex})',
                'pokemon': {
                    'name': name,
                    'dex': dex,
                    'type1': type1,
                    'type2': type2,
                    'types': f"{type1}" + (f"/{type2}" if type2 else "")
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create Pokémon'}), 500
    
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-sprite', methods=['POST'])
def generate_sprite():
    """Generate a Pokémon sprite from text description"""
    try:
        data = request.json
        
        if 'prompt' not in data:
            return jsonify({'success': False, 'error': 'Missing prompt'}), 400
        
        prompt = data['prompt'].strip()
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt cannot be empty'}), 400
        
        # Get generator
        gen = get_sprite_generator()
        if gen is None:
            return jsonify({
                'success': False,
                'error': 'Sprite generator not available. Install dependencies: pip install -r requirements.txt'
            }), 503
        
        # Generate parameters
        steps = int(data.get('steps', 20))
        steps = min(50, max(10, steps))  # Clamp to 10-50
        
        seed = data.get('seed')
        if seed:
            seed = int(seed)
        
        print(f"Generating sprite from prompt: {prompt}")

        # Prepare save directory and random name
        app_dir = Path(__file__).parent
        save_dir = app_dir / "generated_sprites"
        save_dir.mkdir(parents=True, exist_ok=True)

        name = secrets.token_hex(3)  # 6-hex characters
        output_path = save_dir / f"{name}.png"

        # Generate and save both high-res and downscaled images
        success = gen.generate_and_save(
            prompt=prompt,
            output_path=output_path,
            num_inference_steps=steps,
            seed=seed
        )

        if not success:
            return jsonify({'success': False, 'error': 'Failed to generate and save sprite'}), 500

        high_path = save_dir / f"{name}_512.png"
        low_path = save_dir / f"{name}_96.png"

        # Read low-res image for immediate preview (base64)
        try:
            with low_path.open('rb') as f:
                data = f.read()
            image_base64 = base64.b64encode(data).decode('utf-8')
        except Exception:
            image_base64 = None

        return jsonify({
            'success': True,
            'name': name,
            'saved_paths': {
                'high': str(high_path),
                'low': str(low_path)
            },
            'image': f'data:image/png;base64,{image_base64}' if image_base64 else None,
            'message': f'Generated and saved sprite: {name}'
        })
    
    except Exception as e:
        print(f"Error generating sprite: {e}")
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
