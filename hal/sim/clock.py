# Simulated clock using standard Python time module

from hal.interfaces import ClockInterface
import time


class ClockSim(ClockInterface):
    """Simulated clock for PC"""
    
    def __init__(self):
        self._start_time = time.time() * 1000  # Convert to ms
    
    def sleep_ms(self, ms):
        """Sleep for milliseconds"""
        time.sleep(ms / 1000.0)
    
    def ticks_ms(self):
        """Get millisecond timestamp"""
        # Return milliseconds since start
        return int(time.time() * 1000 - self._start_time)
    
    def ticks_diff(self, ticks1, ticks2):
        """Calculate difference between two tick values"""
        return ticks1 - ticks2

