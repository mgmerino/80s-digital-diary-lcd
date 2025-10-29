# Hardware Abstraction Layer (HAL)
# This module provides platform-independent interfaces for hardware access

from .platform import get_platform, is_simulator
from .color import rgb565_to_rgb888, rgb888_to_rgb565

__all__ = [
    'get_platform',
    'is_simulator',
    'rgb565_to_rgb888',
    'rgb888_to_rgb565',
]

