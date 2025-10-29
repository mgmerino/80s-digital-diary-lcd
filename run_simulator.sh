#!/bin/bash
# Run the LCD-GFX simulator

# Set simulator mode
export SIM=1

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "pygame is not installed. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the simulator
echo "Starting LCD-GFX Simulator..."
echo "Press Ctrl+C to exit"
echo ""
echo "Keyboard mappings:"
echo "  Arrow keys -> CardKB arrow keys"
echo "  Enter -> Enter"
echo "  Backspace -> Backspace"
echo "  Escape -> Escape"
echo "  Letters/Numbers -> CardKB keys"
echo ""

python3 main.py "$@"

