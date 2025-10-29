# Real backlight implementation using GFX Pack

from hal.interfaces import BacklightInterface


class BacklightReal(BacklightInterface):
    """Real backlight implementation for GFX Pack"""
    
    def __init__(self, gfx_pack):
        """
        Args:
            gfx_pack: The GfxPack object
        """
        self._gfx_pack = gfx_pack
    
    def set_backlight(self, r, g, b, w):
        """Set backlight RGB+W values"""
        self._gfx_pack.set_backlight(r, g, b, w)

