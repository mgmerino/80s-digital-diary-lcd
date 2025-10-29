# Real display implementation using Pimoroni GFX Pack

from hal.interfaces import DisplayInterface


class DisplayReal(DisplayInterface):
    """Real display implementation for Pimoroni GFX Pack (ST7789)"""
    
    def __init__(self, gfx_display):
        """
        Args:
            gfx_display: The Pimoroni GFX Pack display object
        """
        self._display = gfx_display
        self._width, self._height = gfx_display.get_bounds()
        self._current_pen = 15  # Default pen color
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    def init(self):
        """Initialize display (already done by GfxPack)"""
        pass
    
    def fill(self, color):
        """Fill entire display with color"""
        self.set_pen(color)
        self._display.clear()
    
    def pixel(self, x, y, color=None):
        """Set a single pixel"""
        if color is not None:
            self._display.set_pen(color)
        self._display.pixel(x, y)
    
    def rect(self, x, y, w, h, color, fill=False):
        """Draw a rectangle"""
        self._display.set_pen(color)
        if fill:
            self._display.rectangle(x, y, w, h)
        else:
            # Draw outline
            self._display.rectangle(x, y, w, 1)  # Top
            self._display.rectangle(x, y + h - 1, w, 1)  # Bottom
            self._display.rectangle(x, y, 1, h)  # Left
            self._display.rectangle(x + w - 1, y, 1, h)  # Right
    
    def line(self, x0, y0, x1, y1, color=None):
        """Draw a line"""
        if color is not None:
            self._display.set_pen(color)
        self._display.line(x0, y0, x1, y1)
    
    def text(self, string, x, y, width=None, scale=1):
        """Draw text (GFX Pack compatible signature)"""
        # GFX Pack text() uses current pen, so just pass through
        if width is None:
            width = self._width
        self._display.text(str(string), x, y, width, scale)
    
    def blit(self, x, y, buf, w, h):
        """Blit a buffer to screen (not directly supported by GFX Pack)"""
        # This would need custom implementation for image data
        # For now, we'll skip or implement later if needed
        pass
    
    def update(self):
        """Update display - GFX Pack auto-updates, so this is a no-op"""
        self._display.update()
    
    # Compatibility methods with existing GFX Pack API
    def set_pen(self, color):
        """Set drawing color"""
        self._current_pen = color
        self._display.set_pen(color)
    
    def clear(self):
        """Clear display"""
        self._display.clear()
    
    def rectangle(self, x, y, w, h):
        """Draw filled rectangle with current pen"""
        self._display.rectangle(x, y, w, h)
    
    def circle(self, cx, cy, r):
        """Draw filled circle with current pen"""
        self._display.circle(cx, cy, r)
    
    def set_font(self, font):
        """Set font"""
        self._display.set_font(font)
    
    def get_bounds(self):
        """Get display bounds"""
        return (self._width, self._height)

