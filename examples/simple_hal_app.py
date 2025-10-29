#!/usr/bin/env python3
"""
Simple example showing how to use the HAL (Hardware Abstraction Layer)
This same code runs on both Raspberry Pi Pico and PC simulator!
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hal import get_platform, is_simulator


def main():
    """Simple app demonstrating HAL usage"""
    
    # Get platform (auto-detects based on SIM env var)
    platform = get_platform()
    
    # Initialize hardware
    display = platform.init_display(width=240, height=240, scale=3)
    input_dev = platform.init_input()
    clock = platform.init_clock()
    
    print(f"Running on: {'Simulator' if is_simulator() else 'Real Hardware'}")
    
    # Draw initial screen
    display.fill(0)
    display.set_pen(15)
    display.text(10, 10, "HAL Demo App", 15)
    display.text(10, 30, "Press keys to interact", 15)
    display.text(10, 50, "ESC to exit", 15)
    
    # Draw some shapes
    display.rectangle(10, 70, 100, 30)
    display.circle(180, 85, 20)
    
    display.update()
    
    # Main loop
    key_count = 0
    last_key = None
    
    while True:
        # Read input
        key = input_dev.read_key()
        
        if key is not None:
            key_count += 1
            last_key = key
            
            print(f"Key pressed: {key} (0x{key:02X}) - Count: {key_count}")
            
            # Exit on ESC
            if key == 0x1B:
                print("ESC pressed, exiting...")
                break
            
            # Update display
            display.set_pen(0)
            display.rectangle(10, 110, 220, 120)
            
            display.set_pen(15)
            display.text(10, 110, f"Keys pressed: {key_count}", 15)
            display.text(10, 130, f"Last key: 0x{key:02X}", 15)
            
            if 32 <= key < 127:
                char = chr(key)
                display.text(10, 150, f"Character: {char}", 15)
            
            # Draw a circle for each keypress
            x = 20 + (key_count % 10) * 20
            y = 180 + ((key_count // 10) % 3) * 20
            display.circle(x, y, 8)
            
            display.update()
        
        # Small delay to avoid busy-waiting
        clock.sleep_ms(10)
    
    print("Demo finished!")


if __name__ == "__main__":
    # Set simulator mode if not already set
    if 'SIM' not in os.environ:
        print("Tip: Set SIM=1 to run in simulator mode")
        print("Example: SIM=1 python3 simple_hal_app.py")
        print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

