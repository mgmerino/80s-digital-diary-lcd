# Settings App
# TODO: Copiar SettingsApp, ThemeChooserApp, WBrightnessApp del main.py original

from apps.base import App
from core.ui import cls, header
from core.context import THEMES
from apps.theme_chooser import ThemeChooserApp
from apps.w_brightness import WBrightnessApp
from apps.settime import SetTimeApp

class SettingsApp(App):
    title = "Config"
    tick_ms = 300
    
    def __init__(self):
        self.idx = 0
        self.items = ["Theme", "W Brightness", "Set Time", "Back"]
        self.themes = list(THEMES.keys())
        self.tidx = 0
    
    def draw_icon(self, ctx, x,y,w,h):
        icon = [
            0b0000001111000000,
            0b0001101001011000,
            0b0010011001100100,
            0b0100000000000010,
            0b0100000000000010,
            0b0010000000000100,
            0b1110000110000111,
            0b1000001001000001,
            0b1000001001000001,
            0b1110000110000111,
            0b0010000000000100,
            0b0100000000000010,
            0b0100000000000010,
            0b0010011001100100,
            0b0001101001011000,
            0b0000001111000000,
        ]
        start_x = x + (w - 16) // 2  # center horizontally
        start_y = y + (h - 12) // 2  # center vertically (usually 0 since h=16)
    
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):  # check if bit is set
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def draw(self, ctx):
        cls(ctx); header(ctx,"Config")
        for i, it in enumerate(self.items):
            mark = ">" if i==self.idx else " "
            ctx.d.text("{} {}".format(mark,it), 2, 12+i*8, ctx.W, 1)
        t = ctx.settings.get("theme","amber")
        ctx.d.text("Tema: {}".format(t), 2, ctx.H-16, ctx.W, 1)
        ctx.d.text("W={}".format(ctx.settings.get("w_brightness",64)), 80, ctx.H-16, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        # Arrow key support
        if k == 0xB6:  # Down
            k = ord('j')
        elif k == 0xB5:  # Up
            k = ord('k')
        
        if k==ord('j') and self.idx< len(self.items)-1: self.idx+=1
        elif k==ord('k') and self.idx>0: self.idx-=1
        elif k==13:
            if self.idx==0: return ("push", ThemeChooserApp())
            if self.idx==1: return ("push", WBrightnessApp())
            if self.idx==2: return ("push", SetTimeApp())
            if self.idx==3: return "pop"


