# Real input implementation using CardKB over I2C

from hal.interfaces import InputInterface

CARDKB_ADDR = 0x5F


class InputReal(InputInterface):
    """Real input implementation for CardKB"""
    
    def __init__(self, i2c):
        """
        Args:
            i2c: I2C object configured for CardKB
        """
        self._i2c = i2c
        self._last_key = None
    
    def poll(self):
        """Poll for input events"""
        key = self.read_key()
        if key is not None:
            return [{'type': 'keydown', 'key': key}]
        return []
    
    def read_key(self):
        """Read a single key from CardKB"""
        try:
            b = self._i2c.readfrom(CARDKB_ADDR, 1)
            if not b:
                return None
            v = b[0]
            return None if v == 0 else v
        except OSError:
            return None

