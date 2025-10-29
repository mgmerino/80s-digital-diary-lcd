# Simulated display using pygame

from hal.interfaces import DisplayInterface
from hal.color import rgb565_to_rgb888
import pygame
import sys


# Font data for bitmap fonts (simple 8x8 monospace)
class FontRenderer:
    """Simple font renderer for simulator"""
    
    def __init__(self, size=8):
        self.size = size
        # Try to load a monospace font
        try:
            self.font = pygame.font.SysFont('courier', size)
        except:
            self.font = pygame.font.Font(None, size)
    
    def get_size(self, text):
        """Get text size"""
        return self.font.size(text)
    
    def render(self, text, color):
        """Render text to surface"""
        return self.font.render(text, True, color)


class DisplaySim(DisplayInterface):
    """Simulated display using pygame"""
    
    def __init__(self, width=240, height=240, scale=3):
        """
        Args:
            width: Display width in pixels
            height: Display height in pixels
            scale: Scaling factor for display window
        """
        self._width = width
        self._height = height
        self._scale = scale
        self._current_pen = 15
        self._current_font = "bitmap8"
        
        # Initialize pygame
        pygame.init()
        self._window = pygame.display.set_mode((width * scale, height * scale))
        pygame.display.set_caption("LCD-GFX Simulator")
        
        # Create framebuffer (RGB888)
        self._framebuffer = pygame.Surface((width, height))
        self._framebuffer.fill((0, 0, 0))
        
        # Font renderers for different sizes
        self._fonts = {
            "bitmap6": FontRenderer(6),
            "bitmap8": FontRenderer(8),
            "bitmap14_outline": FontRenderer(14),
            "sans": FontRenderer(12),
            "cursive": FontRenderer(12),
        }
        self._current_font_renderer = self._fonts["bitmap8"]
        
        # Color palette (16 colors, similar to GFX Pack)
        self._palette = self._create_palette()
    
    def _create_palette(self):
        """Create a 16-color palette"""
        # Simple grayscale palette for now
        palette = []
        for i in range(16):
            val = (i * 255) // 15
            palette.append((val, val, val))
        return palette
    
    def _pen_to_rgb(self, pen):
        """Convert pen index to RGB"""
        if isinstance(pen, int):
            return self._palette[pen % 16]
        return pen
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    def init(self):
        """Initialize display"""
        self._framebuffer.fill((0, 0, 0))
        self.update()
    
    def fill(self, color):
        """Fill entire display with color"""
        rgb = self._pen_to_rgb(color)
        self._framebuffer.fill(rgb)
    
    def pixel(self, x, y, color=None):
        """Set a single pixel"""
        if color is None:
            color = self._current_pen
        if 0 <= x < self._width and 0 <= y < self._height:
            rgb = self._pen_to_rgb(color)
            self._framebuffer.set_at((x, y), rgb)
    
    def rect(self, x, y, w, h, color, fill=False):
        """Draw a rectangle"""
        rgb = self._pen_to_rgb(color)
        if fill:
            pygame.draw.rect(self._framebuffer, rgb, (x, y, w, h))
        else:
            pygame.draw.rect(self._framebuffer, rgb, (x, y, w, h), 1)
    
    def line(self, x0, y0, x1, y1, color=None):
        """Draw a line"""
        if color is None:
            color = self._current_pen
        rgb = self._pen_to_rgb(color)
        pygame.draw.line(self._framebuffer, rgb, (x0, y0), (x1, y1))
    
    def text(self, string, x, y, width=None, scale=1):
        """Draw text (GFX Pack compatible signature)"""
        # Use current pen color
        rgb = self._pen_to_rgb(self._current_pen)
        text_surface = self._current_font_renderer.render(str(string), rgb)
        self._framebuffer.blit(text_surface, (x, y))
    
    def blit(self, x, y, buf, w, h):
        """Blit a buffer to screen"""
        # buf should be a bytes object or list of RGB values
        if isinstance(buf, (bytes, bytearray)):
            # Create surface from buffer
            surface = pygame.Surface((w, h))
            for py in range(h):
                for px in range(w):
                    idx = (py * w + px) * 3
                    if idx + 2 < len(buf):
                        color = (buf[idx], buf[idx+1], buf[idx+2])
                        surface.set_at((px, py), color)
            self._framebuffer.blit(surface, (x, y))
    
    def update(self):
        """Update display window"""
        # Scale framebuffer to window
        scaled = pygame.transform.scale(self._framebuffer, 
                                       (self._width * self._scale, 
                                        self._height * self._scale))
        self._window.blit(scaled, (0, 0))
        pygame.display.flip()
        
        # Process pygame events to keep window responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
    
    # Compatibility methods
    def set_pen(self, color):
        """Set drawing color"""
        self._current_pen = color
    
    def clear(self):
        """Clear display"""
        rgb = self._pen_to_rgb(self._current_pen)
        self._framebuffer.fill(rgb)
    
    def rectangle(self, x, y, w, h):
        """Draw filled rectangle with current pen"""
        rgb = self._pen_to_rgb(self._current_pen)
        pygame.draw.rect(self._framebuffer, rgb, (x, y, w, h))
    
    def circle(self, cx, cy, r):
        """Draw filled circle with current pen"""
        rgb = self._pen_to_rgb(self._current_pen)
        pygame.draw.circle(self._framebuffer, rgb, (cx, cy), r)
    
    def set_font(self, font):
        """Set font"""
        self._current_font = font
        if font in self._fonts:
            self._current_font_renderer = self._fonts[font]
    
    def get_bounds(self):
        """Get display bounds"""
        return (self._width, self._height)
    
    def save_screenshot(self, filename):
        """Save current framebuffer to PNG"""
        pygame.image.save(self._framebuffer, filename)

