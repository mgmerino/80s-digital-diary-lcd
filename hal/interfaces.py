# HAL Interface Definitions

class DisplayInterface:
    """Abstract display interface"""
    
    @property
    def width(self):
        """Display width in pixels"""
        raise NotImplementedError
    
    @property
    def height(self):
        """Display height in pixels"""
        raise NotImplementedError
    
    def init(self):
        """Initialize the display"""
        raise NotImplementedError
    
    def fill(self, color):
        """Fill entire display with color"""
        raise NotImplementedError
    
    def pixel(self, x, y, color=None):
        """Set a single pixel (color optional, uses current pen if not specified)"""
        raise NotImplementedError
    
    def rect(self, x, y, w, h, color, fill=False):
        """Draw a rectangle"""
        raise NotImplementedError
    
    def line(self, x0, y0, x1, y1, color=None):
        """Draw a line (color optional, uses current pen if not specified)"""
        raise NotImplementedError
    
    def text(self, string, x, y, width=None, scale=1):
        """Draw text (GFX Pack compatible: string, x, y, width, scale)"""
        raise NotImplementedError
    
    def blit(self, x, y, buf, w, h):
        """Blit a buffer to screen"""
        raise NotImplementedError
    
    def update(self):
        """Update/refresh the display (flush framebuffer)"""
        raise NotImplementedError
    
    # Additional methods for compatibility with existing code
    def set_pen(self, color):
        """Set drawing color (pen)"""
        raise NotImplementedError
    
    def clear(self):
        """Clear the display"""
        raise NotImplementedError
    
    def rectangle(self, x, y, w, h):
        """Draw filled rectangle with current pen"""
        raise NotImplementedError
    
    def circle(self, cx, cy, r):
        """Draw filled circle with current pen"""
        raise NotImplementedError
    
    def set_font(self, font):
        """Set the font for text drawing"""
        raise NotImplementedError
    
    def get_bounds(self):
        """Get display bounds (width, height)"""
        return (self.width, self.height)


class InputInterface:
    """Abstract input interface"""
    
    def poll(self):
        """Poll for input events. Returns list of events or empty list."""
        raise NotImplementedError
    
    def read_key(self):
        """Read a single key (CardKB style). Returns key code or None."""
        raise NotImplementedError


class ClockInterface:
    """Abstract clock/timing interface"""
    
    def sleep_ms(self, ms):
        """Sleep for milliseconds"""
        raise NotImplementedError
    
    def ticks_ms(self):
        """Get millisecond timestamp"""
        raise NotImplementedError
    
    def ticks_diff(self, ticks1, ticks2):
        """Calculate difference between two tick values"""
        raise NotImplementedError


class StorageInterface:
    """Abstract storage interface"""
    
    def read(self, path):
        """Read data from file"""
        raise NotImplementedError
    
    def write(self, path, data):
        """Write data to file"""
        raise NotImplementedError
    
    def exists(self, path):
        """Check if file exists"""
        raise NotImplementedError
    
    def remove(self, path):
        """Remove a file"""
        raise NotImplementedError


class BacklightInterface:
    """Abstract backlight control"""
    
    def set_backlight(self, r, g, b, w):
        """Set backlight RGB+W values (0-255)"""
        raise NotImplementedError

