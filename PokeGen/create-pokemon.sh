#!/bin/bash
# PokeGen CLI Generator
# Creates Pokémon from command line

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Usage
if [ $# -eq 0 ]; then
    echo "PokeGen - Create Pokémon from Command Line"
    echo ""
    echo "Usage: ./create-pokemon.sh <name> <dex> <type1> [options]"
    echo ""
    echo "Examples:"
    echo "  ./create-pokemon.sh Flamewing 888 FIRE FLYING --hp 70 --att 100"
    echo "  ./create-pokemon.sh Aquadrift 889 WATER FLYING --template pelipper"
    echo ""
    echo "Options:"
    echo "  --dex N              Pokédex number"
    echo "  --type2 TYPE         Secondary type"
    echo "  --hp N               HP stat"
    echo "  --att N              Attack stat"
    echo "  --def N              Defense stat"
    echo "  --spa N              Special Attack stat"
    echo "  --spd N              Special Defense stat"
    echo "  --spe N              Speed stat"
    echo "  --ability1 ABILITY   Primary ability"
    echo "  --ability2 ABILITY   Secondary ability"
    echo "  --gender N           Gender ratio (0-100)"
    echo "  --template POKEMON   Copy sprites from template"
    exit 0
fi

python3 pokemon_mod_generator.py "$@"
