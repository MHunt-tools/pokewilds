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

# Allow overriding host/port via env vars (defaults: localhost:5000)
PORT="${PORT:-5000}"
HOST="${HOST:-localhost}"

echo "Starting on http://${HOST}:${PORT}"

# Start the app as a child process and trap signals so the child is killed
# when this script exits or is interrupted. This ensures the port is freed.
echo "$PYTHON"

$PYTHON - <<PYTHON &
from app import app
# Run without the reloader so the parent process isn't replaced (avoids
# the reloader spawning a child that our trap then immediately kills).
app.run(debug=False, use_reloader=False, host='${HOST}', port=${PORT})
PYTHON

PYTHON_PID=$!

trap 'echo "Stopping PokeGen (pid ${PYTHON_PID})..."; kill ${PYTHON_PID} 2>/dev/null || true; wait ${PYTHON_PID} 2>/dev/null || true' INT TERM EXIT

# Wait for the Python child to exit so the script mirrors its lifecycle
wait ${PYTHON_PID}
