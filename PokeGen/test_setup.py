#!/usr/bin/env python3
"""
PokeGen Setup Test
Verifies that all components are installed and working
"""

import sys
from pathlib import Path


def test_imports():
    """Test if required packages are installed"""
    print("Testing imports...")
    
    required = {
        'flask': 'Flask',
        'PIL': 'Pillow',
        'pathlib': 'Standard Library (pathlib)',
    }
    
    optional = {
        'diffusers': 'Diffusers (for sprite generation)',
        'torch': 'PyTorch (for sprite generation)',
        'transformers': 'Transformers (for sprite generation)',
    }
    
    print("\nRequired packages:")
    missing_required = []
    for package, name in required.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name}")
            missing_required.append(package)
    
    print("\nOptional packages (for AI sprite generation):")
    missing_optional = []
    for package, name in optional.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ⊘ {name} - not installed")
            missing_optional.append(package)
    
    return missing_required, missing_optional


def test_files():
    """Test if required files exist"""
    print("\n\nChecking files...")
    
    script_dir = Path(__file__).parent
    required_files = [
        'app.py',
        'pokemon_mod_generator.py',
        'requirements.txt',
        'templates/index.html',
    ]
    
    missing = []
    for file in required_files:
        path = script_dir / file
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file}")
            missing.append(file)
    
    return missing


def main():
    """Run all tests"""
    print("=" * 60)
    print("PokeGen Setup Test")
    print("=" * 60)
    print()
    
    # Test imports
    missing_req, missing_opt = test_imports()
    
    # Test files
    missing_files = test_files()
    
    print("\n" + "=" * 60)
    
    # Summary
    if missing_req:
        print(f"\n✗ Missing required packages: {', '.join(missing_req)}")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        return False
    
    if missing_files:
        print(f"\n✗ Missing files: {', '.join(missing_files)}")
        return False
    
    print("\n✓ Setup test PASSED!")
    print("\nReady to use!")
    
    if missing_opt:
        print(f"\nOptional features disabled: {', '.join([n for _, n in [(p, optional.get(p, p)) for p in missing_opt]])}")
        print("To enable AI sprite generation:")
        print("  pip install diffusers transformers torch accelerate")
    
    print("\n" + "=" * 60)
    print("\nNext steps:")
    print("  1. Web UI:  ./start-web-app.sh")
    print("  2. CLI:     ./create-pokemon.sh MyPokemon 888 FIRE")
    print("\nRead README.md for more information.")
    print("=" * 60 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
