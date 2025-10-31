# Simulated input using pygame keyboard

from hal.interfaces import InputInterface
import pygame


# Key mapping from PC keyboard to CardKB codes
KEY_MAP = {
    # Arrow keys
    pygame.K_UP: 0xB5,      # Up arrow
    pygame.K_DOWN: 0xB6,    # Down arrow
    pygame.K_LEFT: 0xB4,    # Left arrow
    pygame.K_RIGHT: 0xB7,   # Right arrow
    
    # Special keys
    pygame.K_RETURN: 0x0D,  # Enter/Return
    pygame.K_BACKSPACE: 0x08,  # Backspace
    pygame.K_ESCAPE: 0x1B,  # Escape
    pygame.K_TAB: 0x09,     # Tab
    pygame.K_SPACE: 0x20,   # Space
    
    # Function keys (simulate as F1-F12)
    pygame.K_F1: 0xF1,
    pygame.K_F2: 0xF2,
    pygame.K_F3: 0xF3,
    pygame.K_F4: 0xF4,
    pygame.K_F5: 0xF5,
    pygame.K_F6: 0xF6,
    
    # Letters (a-z)
    pygame.K_a: ord('a'), pygame.K_b: ord('b'), pygame.K_c: ord('c'),
    pygame.K_d: ord('d'), pygame.K_e: ord('e'), pygame.K_f: ord('f'),
    pygame.K_g: ord('g'), pygame.K_h: ord('h'), pygame.K_i: ord('i'),
    pygame.K_j: ord('j'), pygame.K_k: ord('k'), pygame.K_l: ord('l'),
    pygame.K_m: ord('m'), pygame.K_n: ord('n'), pygame.K_o: ord('o'),
    pygame.K_p: ord('p'), pygame.K_q: ord('q'), pygame.K_r: ord('r'),
    pygame.K_s: ord('s'), pygame.K_t: ord('t'), pygame.K_u: ord('u'),
    pygame.K_v: ord('v'), pygame.K_w: ord('w'), pygame.K_x: ord('x'),
    pygame.K_y: ord('y'), pygame.K_z: ord('z'),
    
    # Numbers (0-9)
    pygame.K_0: ord('0'), pygame.K_1: ord('1'), pygame.K_2: ord('2'),
    pygame.K_3: ord('3'), pygame.K_4: ord('4'), pygame.K_5: ord('5'),
    pygame.K_6: ord('6'), pygame.K_7: ord('7'), pygame.K_8: ord('8'),
    pygame.K_9: ord('9'),
    
    # Common symbols
    pygame.K_PERIOD: ord('.'),
    pygame.K_COMMA: ord(','),
    pygame.K_SLASH: ord('/'),
    pygame.K_SEMICOLON: ord(';'),
    pygame.K_QUOTE: ord("'"),
    pygame.K_LEFTBRACKET: ord('['),
    pygame.K_RIGHTBRACKET: ord(']'),
    pygame.K_BACKSLASH: ord('\\'),
    pygame.K_MINUS: ord('-'),
    pygame.K_EQUALS: ord('='),
}


class InputSim(InputInterface):
    """Simulated input using pygame keyboard"""
    
    def __init__(self):
        self._key_buffer = []
        self._last_key = None
    
    def poll(self):
        """Poll for input events"""
        events = []
        
        # Process pygame events
        for event in pygame.event.get(pygame.KEYDOWN):
            if event.key in KEY_MAP:
                key_code = KEY_MAP[event.key]
                
                # Handle shift modifier for uppercase
                if event.mod & pygame.KMOD_SHIFT:
                    if ord('a') <= key_code <= ord('z'):
                        key_code = key_code - 32  # Convert to uppercase
                
                self._key_buffer.append(key_code)
                events.append({'type': 'keydown', 'key': key_code})
        
        return events
    
    def read_key(self):
        """Read a single key (CardKB style)"""
        # Poll for new keys
        self.poll()
        
        # Return buffered key if available
        if self._key_buffer:
            key = self._key_buffer.pop(0)
            self._last_key = key
            return key
        
        return None

