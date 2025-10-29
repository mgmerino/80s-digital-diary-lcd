#!/usr/bin/env python3
"""
LCD-GFX Simulator Runner

This script runs the LCD-GFX project in simulator mode.
It automatically sets the SIM environment variable and handles dependencies.
"""

import os
import sys
import subprocess


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import pygame
        return True
    except ImportError:
        return False


def install_dependencies():
    """Install required dependencies"""
    print("Installing simulator dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])  # pyright: ignore[reportAttributeAccessIssue]


def main():
    """Main entry point"""
    # Set simulator mode
    os.environ['SIM'] = '1'
    
    # Check dependencies
    if not check_dependencies():
        print("pygame is not installed.")
        response = input("Would you like to install it now? (y/n): ")
        if response.lower() == 'y':
            install_dependencies()
        else:
            print("Cannot run simulator without pygame. Exiting.")
            sys.exit(1)
    
    # Print info
    print("=" * 60)
    print("LCD-GFX SIMULATOR")
    print("=" * 60)
    print("\nKeyboard mappings:")
    print("  Arrow keys     -> CardKB arrow keys")
    print("  Enter          -> Enter")
    print("  Backspace      -> Backspace")
    print("  Escape         -> Escape")
    print("  Letters/Numbers -> CardKB keys")
    print("\nPress Ctrl+C to exit")
    print("=" * 60)
    print()
    
    # Import and run main
    try:
        import main
        main.main()
    except KeyboardInterrupt:
        print("\n\nSimulator stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError running simulator: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

