#!/bin/bash
# PokeGen Web App Launcher
# Starts the PokeGen web application at http://localhost:5000

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use conda Python if available, otherwise fall back to system python3
if [ -f "$HOME/miniconda3/bin/python" ]; then
    PYTHON="$HOME/miniconda3/bin/python"
    PIP="$HOME/miniconda3/bin/pip"
else
    PYTHON="python3"
    PIP="pip"
fi

echo "=========================================="
echo "PokeGen - Pokémon Mod Creator"
echo "=========================================="
echo ""

# Check Python
if ! command -v $PYTHON &> /dev/null; then
    echo "✗ Python not found. Please install Python 3.9+"
    exit 1
fi

echo "✓ Python: $($PYTHON --version)"

# Check dependencies
echo ""
echo "Checking dependencies..."
if ! $PYTHON -c "import flask" 2>/dev/null; then
    echo ""
    echo "Installing dependencies (this may take a few minutes)..."
    $PIP install -r requirements.txt
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "Starting PokeGen web server..."
echo "Open your browser: http://localhost:5000"
echo ""
echo "Features:"
echo "  • Create custom Pokémon mods"
echo "  • Generate sprites with AI (GPU optional)"
echo "  • Save mods to ../mods/ directory"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

$PYTHON app.py
