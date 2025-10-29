# Platform detection and HAL factory

import os
import sys


def is_simulator():
    """Check if running in simulator mode"""
    # Check for SIM environment variable
    return os.environ.get('SIM', '0') == '1'


def is_micropython():
    """Check if running on MicroPython"""
    return sys.implementation.name == 'micropython'


class Platform:
    """Platform abstraction - provides hardware interfaces"""
    
    def __init__(self):
        self._sim_mode = is_simulator()
        self._display = None
        self._input = None
        self._clock = None
        self._storage = None
        self._backlight = None
        self._gfx_pack = None
        self._i2c = None
        self._rtc = None
    
    def init_display(self, width=240, height=240, scale=3, gfx_pack=None):
        """Initialize display interface"""
        if self._sim_mode:
            from hal.sim import DisplaySim
            self._display = DisplaySim(width, height, scale)
        else:
            from hal.real import DisplayReal
            if gfx_pack is None:
                raise ValueError("gfx_pack required for real hardware")
            self._display = DisplayReal(gfx_pack.display)
        
        self._display.init()
        return self._display
    
    def init_input(self, i2c=None):
        """Initialize input interface"""
        if self._sim_mode:
            from hal.sim import InputSim
            self._input = InputSim()
        else:
            from hal.real import InputReal
            if i2c is None:
                raise ValueError("i2c required for real hardware")
            self._input = InputReal(i2c)
        
        return self._input
    
    def init_clock(self):
        """Initialize clock interface"""
        if self._sim_mode:
            from hal.sim import ClockSim
            self._clock = ClockSim()
        else:
            from hal.real import ClockReal
            self._clock = ClockReal()
        
        return self._clock
    
    def init_storage(self):
        """Initialize storage interface"""
        if self._sim_mode:
            from hal.sim import StorageSim
            self._storage = StorageSim()
        else:
            from hal.real import StorageReal
            self._storage = StorageReal()
        
        return self._storage
    
    def init_backlight(self, gfx_pack=None):
        """Initialize backlight interface"""
        if self._sim_mode:
            from hal.sim import BacklightSim
            self._backlight = BacklightSim()
        else:
            from hal.real import BacklightReal
            if gfx_pack is None:
                raise ValueError("gfx_pack required for real hardware")
            self._backlight = BacklightReal(gfx_pack)
        
        return self._backlight
    
    @property
    def display(self):
        return self._display
    
    @property
    def input(self):
        return self._input
    
    @property
    def clock(self):
        return self._clock
    
    @property
    def storage(self):
        return self._storage
    
    @property
    def backlight(self):
        return self._backlight
    
    def is_simulator(self):
        return self._sim_mode


def get_platform():
    """Get platform instance (singleton)"""
    if not hasattr(get_platform, '_instance'):
        get_platform._instance = Platform()
    return get_platform._instance

