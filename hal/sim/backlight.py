# Simulated backlight (no-op for simulator)

from hal.interfaces import BacklightInterface


class BacklightSim(BacklightInterface):
    """Simulated backlight (does nothing in simulator)"""
    
    def __init__(self):
        self._r = 0
        self._g = 0
        self._b = 0
        self._w = 0
    
    def set_backlight(self, r, g, b, w):
        """Set backlight RGB+W values (stored but not displayed)"""
        self._r = r
        self._g = g
        self._b = b
        self._w = w
        # In simulator, we could potentially use this to tint the display
        # or show in window title, but for now just store it
        print(f"Backlight: R={r}, G={g}, B={b}, W={w}")

