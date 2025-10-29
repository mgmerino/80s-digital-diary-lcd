# Color conversion helpers

def rgb565_to_rgb888(color565):
    """Convert RGB565 to RGB888 tuple (r, g, b)"""
    r = ((color565 >> 11) & 0x1F) << 3
    g = ((color565 >> 5) & 0x3F) << 2
    b = (color565 & 0x1F) << 3
    # Expand to full range by copying MSB to LSB
    r |= r >> 5
    g |= g >> 6
    b |= b >> 5
    return (r, g, b)


def rgb888_to_rgb565(r, g, b):
    """Convert RGB888 (r, g, b) to RGB565"""
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def rgb_to_rgb565(rgb_tuple):
    """Convert RGB tuple to RGB565"""
    return rgb888_to_rgb565(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])

