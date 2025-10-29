# Real clock implementation using MicroPython time module

from hal.interfaces import ClockInterface
import time


class ClockReal(ClockInterface):
    """Real clock implementation for Pico"""
    
    def sleep_ms(self, ms):
        """Sleep for milliseconds"""
        time.sleep_ms(ms)
    
    def ticks_ms(self):
        """Get millisecond timestamp"""
        return time.ticks_ms()
    
    def ticks_diff(self, ticks1, ticks2):
        """Calculate difference between two tick values"""
        return time.ticks_diff(ticks1, ticks2)

