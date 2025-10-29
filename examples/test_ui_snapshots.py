#!/usr/bin/env python3
"""
Example of snapshot testing for UI components

This demonstrates how to use the simulator for automated UI testing
by capturing and comparing screenshots.
"""

import os
import sys

# Set simulator mode
os.environ['SIM'] = '1'

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hal import get_platform
import pygame


def setup_display():
    """Initialize display for testing"""
    platform = get_platform()
    return platform.init_display(width=240, height=240, scale=2)


def render_button(display, x, y, width, height, text):
    """Render a button component"""
    # Draw button background
    display.set_pen(15)
    display.rectangle(x, y, width, height)
    
    # Draw button border
    display.set_pen(0)
    display.rect(x, y, width, height, 0, fill=False)
    
    # Draw button text (centered)
    text_x = x + (width - len(text) * 6) // 2
    text_y = y + (height - 8) // 2
    display.text(text_x, text_y, text, 0)


def render_list_item(display, x, y, width, height, text, selected=False):
    """Render a list item component"""
    # Background
    if selected:
        display.set_pen(15)
        display.rectangle(x, y, width, height)
        text_color = 0
    else:
        display.set_pen(0)
        display.rectangle(x, y, width, height)
        text_color = 15
    
    # Text
    display.text(x + 5, y + (height - 8) // 2, text, text_color)
    
    # Border
    display.set_pen(15)
    display.line(x, y + height - 1, x + width, y + height - 1, 15)


def test_button_rendering(display, screenshot_dir):
    """Test button component rendering"""
    print("Testing button rendering...")
    
    # Clear display
    display.fill(0)
    
    # Render buttons in different states
    render_button(display, 10, 10, 100, 30, "Click Me")
    render_button(display, 120, 10, 100, 30, "Cancel")
    render_button(display, 10, 50, 210, 40, "Wide Button")
    render_button(display, 65, 100, 110, 25, "Small")
    
    # Update and save
    display.update()
    
    filename = os.path.join(screenshot_dir, "test_buttons.png")
    display.save_screenshot(filename)
    print(f"  ✓ Saved: {filename}")


def test_list_rendering(display, screenshot_dir):
    """Test list component rendering"""
    print("Testing list rendering...")
    
    # Clear display
    display.fill(0)
    
    # Render list items
    items = ["Item 1", "Item 2", "Item 3 (Selected)", "Item 4", "Item 5"]
    y = 10
    for i, item in enumerate(items):
        selected = (i == 2)
        render_list_item(display, 10, y, 220, 25, item, selected)
        y += 27
    
    # Update and save
    display.update()
    
    filename = os.path.join(screenshot_dir, "test_list.png")
    display.save_screenshot(filename)
    print(f"  ✓ Saved: {filename}")


def test_layout_grid(display, screenshot_dir):
    """Test grid layout"""
    print("Testing grid layout...")
    
    # Clear display
    display.fill(0)
    
    # Draw grid of boxes
    cols = 3
    rows = 3
    box_size = 60
    gap = 10
    start_x = 20
    start_y = 20
    
    display.set_pen(15)
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (box_size + gap)
            y = start_y + row * (box_size + gap)
            display.rect(x, y, box_size, box_size, 15, fill=False)
            
            # Draw number in center
            num = str(row * cols + col + 1)
            text_x = x + (box_size - len(num) * 6) // 2
            text_y = y + (box_size - 8) // 2
            display.text(text_x, text_y, num, 15)
    
    # Update and save
    display.update()
    
    filename = os.path.join(screenshot_dir, "test_grid.png")
    display.save_screenshot(filename)
    print(f"  ✓ Saved: {filename}")


def test_text_rendering(display, screenshot_dir):
    """Test text rendering at different sizes"""
    print("Testing text rendering...")
    
    # Clear display
    display.fill(0)
    display.set_pen(15)
    
    # Different text samples
    y = 10
    texts = [
        "The quick brown fox",
        "jumps over the lazy dog",
        "UPPERCASE TEXT",
        "lowercase text",
        "Numbers: 0123456789",
        "Symbols: !@#$%^&*()",
    ]
    
    for text in texts:
        display.text(10, y, text, 15)
        y += 15
    
    # Update and save
    display.update()
    
    filename = os.path.join(screenshot_dir, "test_text.png")
    display.save_screenshot(filename)
    print(f"  ✓ Saved: {filename}")


def test_shapes(display, screenshot_dir):
    """Test shape rendering"""
    print("Testing shape rendering...")
    
    # Clear display
    display.fill(0)
    display.set_pen(15)
    
    # Rectangles
    display.rectangle(10, 10, 50, 30)
    display.rect(70, 10, 50, 30, 15, fill=False)
    
    # Circles
    display.circle(35, 70, 20)
    display.circle(95, 70, 20)
    
    # Lines
    display.line(10, 110, 110, 110, 15)
    display.line(10, 120, 110, 150, 15)
    display.line(110, 120, 10, 150, 15)
    
    # Pixels (pattern)
    for x in range(130, 230, 5):
        for y in range(10, 110, 5):
            display.pixel(x, y, 15)
    
    # Update and save
    display.update()
    
    filename = os.path.join(screenshot_dir, "test_shapes.png")
    display.save_screenshot(filename)
    print(f"  ✓ Saved: {filename}")


def compare_images(img1_path, img2_path):
    """
    Compare two images pixel by pixel
    Returns: (match, difference_percentage)
    """
    img1 = pygame.image.load(img1_path)
    img2 = pygame.image.load(img2_path)
    
    if img1.get_size() != img2.get_size():
        return False, 100.0
    
    width, height = img1.get_size()
    total_pixels = width * height
    different_pixels = 0
    
    for y in range(height):
        for x in range(width):
            if img1.get_at((x, y)) != img2.get_at((x, y)):
                different_pixels += 1
    
    difference = (different_pixels / total_pixels) * 100
    match = difference < 0.1  # Allow 0.1% difference for anti-aliasing
    
    return match, difference


def main():
    """Main test runner"""
    print("=" * 60)
    print("UI Snapshot Testing")
    print("=" * 60)
    print()
    
    # Setup
    display = setup_display()
    
    # Create screenshot directory
    screenshot_dir = "test_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    print(f"Screenshots will be saved to: {screenshot_dir}/")
    print()
    
    # Run tests
    tests = [
        test_button_rendering,
        test_list_rendering,
        test_layout_grid,
        test_text_rendering,
        test_shapes,
    ]
    
    for test_func in tests:
        try:
            test_func(display, screenshot_dir)
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print()
    print("=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print()
    print(f"View screenshots in: {screenshot_dir}/")
    print()
    print("To use for regression testing:")
    print("  1. Review screenshots and verify they look correct")
    print("  2. Copy them to 'expected_screenshots/' directory")
    print("  3. Run tests again and compare with expected")
    print()
    
    # Example comparison (if expected screenshots exist)
    expected_dir = "expected_screenshots"
    if os.path.exists(expected_dir):
        print("Comparing with expected screenshots...")
        for filename in os.listdir(screenshot_dir):
            if filename.endswith('.png'):
                actual = os.path.join(screenshot_dir, filename)
                expected = os.path.join(expected_dir, filename)
                
                if os.path.exists(expected):
                    match, diff = compare_images(actual, expected)
                    status = "✓ PASS" if match else "✗ FAIL"
                    print(f"  {status} {filename} (diff: {diff:.2f}%)")
                else:
                    print(f"  ⚠ SKIP {filename} (no expected image)")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

