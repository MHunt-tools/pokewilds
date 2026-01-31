#!/usr/bin/env python3
"""
PokeGen - Complete System Setup
Run this to verify and display setup information
"""

import sys
from pathlib import Path


def print_header(text):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(title):
    """Print subsection"""
    print(f"\n📌 {title}")
    print("-" * 70)


def main():
    """Display system information and setup status"""
    
    print_header("PokeGen - Pokémon Mod Creator for PokeWilds")
    
    # Paths
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    mods_dir = parent_dir / "mods"
    
    print_section("Installation")
    print(f"PokeGen Location: {script_dir}")
    print(f"Parent (PokeWilds): {parent_dir}")
    print(f"Mods Directory: {mods_dir}")
    
    # Check files
    print_section("Files Installed")
    files = {
        "Core Python": [
            ("app.py", "Flask web server"),
            ("pokemon_mod_generator.py", "Pokémon creator"),
            ("sprite_generator.py", "AI sprite generator"),
        ],
        "Launchers": [
            ("start-web-app.sh", "Start web UI"),
            ("create-pokemon.sh", "CLI tool"),
            ("init-mods.sh", "Initialize mods"),
        ],
        "Configuration": [
            ("requirements.txt", "Python dependencies"),
            ("test_setup.py", "Setup test"),
        ],
        "Documentation": [
            ("README.md", "Complete guide"),
            ("QUICK_START.md", "Quick start (5 min)"),
            ("INTEGRATION_GUIDE.md", "How mods work"),
            ("AI_SPRITE_GENERATION.md", "Sprite guide"),
            ("OVERVIEW.md", "System overview"),
        ],
        "Web UI": [
            ("templates/index.html", "Web interface"),
        ],
    }
    
    all_exist = True
    for category, file_list in files.items():
        print(f"\n{category}:")
        for filename, description in file_list:
            filepath = script_dir / filename
            exists = "✓" if filepath.exists() else "✗"
            print(f"  {exists} {filename:<30} ({description})")
            if not filepath.exists():
                all_exist = False
    
    # Check mods directory
    print_section("Mods Directory")
    if mods_dir.exists():
        print(f"✓ Mods directory exists: {mods_dir}")
        mods_readme = mods_dir / "README.md"
        if mods_readme.exists():
            print(f"✓ Mods README exists")
    else:
        print(f"✗ Mods directory missing: {mods_dir}")
        all_exist = False
    
    # Check Python
    print_section("Python Environment")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 9):
        print(f"✓ Python {python_version}")
    else:
        print(f"✗ Python {python_version} (need 3.9+)")
        all_exist = False
    
    # Quick start instructions
    print_section("Getting Started")
    
    print("\n1️⃣  Install Dependencies")
    print(f"   cd {script_dir}")
    print(f"   pip install -r requirements.txt")
    
    print("\n2️⃣  Start Web UI")
    print(f"   ./start-web-app.sh")
    print(f"   Then open: http://localhost:5000")
    
    print("\n3️⃣  OR Use Command Line")
    print(f"   ./create-pokemon.sh MyPokemon 888 FIRE")
    
    print("\n4️⃣  Generate Sprite (Optional)")
    print(f"   python3 sprite_generator.py MyMon 'red fire dragon'")
    
    print("\n5️⃣  Test in Game")
    print(f"   Restart PokeWilds")
    print(f"   Your Pokémon appears in Pokédex")
    
    # Documentation quick links
    print_section("Documentation")
    docs = [
        ("QUICK_START.md", "⚡ Get started in 5 minutes"),
        ("README.md", "📚 Complete reference guide"),
        ("INTEGRATION_GUIDE.md", "🔧 How mods integrate"),
        ("AI_SPRITE_GENERATION.md", "🎨 Sprite generation guide"),
        ("OVERVIEW.md", "🏗️  System architecture"),
    ]
    
    for filename, description in docs:
        print(f"  • {description}")
        print(f"    See: {filename}")
    
    # Features
    print_section("Features")
    features = [
        "✨ Beautiful web UI (http://localhost:5000)",
        "🎨 AI sprite generation (text-to-image)",
        "⚡ CLI tools for automation",
        "🐍 Python API for developers",
        "📊 Customizable stats and abilities",
        "🎮 Direct PokeWilds integration",
        "💾 Automatic mod packaging",
        "📖 Comprehensive documentation",
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    # Next steps
    print_section("Next Steps")
    
    if not all_exist:
        print("⚠️  Some files are missing!")
        print("Run: pip install -r requirements.txt")
    
    print("\n1. Run setup test:")
    print(f"   python3 test_setup.py")
    
    print("\n2. Start web server:")
    print(f"   ./start-web-app.sh")
    
    print("\n3. Or use CLI directly:")
    print(f"   ./create-pokemon.sh TestMon 1000 FIRE --hp 50 --att 60")
    
    print("\n4. Generate AI sprites (optional):")
    print(f"   python3 sprite_generator.py TestMon 'red fire dragon'")
    
    print("\n5. Play PokeWilds and find your Pokémon!")
    
    # Summary
    print_section("Summary")
    
    if all_exist:
        print("✓ PokeGen is properly installed!")
        print("✓ All required files are present")
        print("✓ Ready to create Pokémon")
    else:
        print("⚠️  Some setup steps may be needed")
        print("   Run: pip install -r requirements.txt")
    
    print("\nStart with: ./start-web-app.sh")
    print("Then open: http://localhost:5000")
    
    print_header("Happy Pokémon Creating! 🎨")
    print()


if __name__ == "__main__":
    main()
