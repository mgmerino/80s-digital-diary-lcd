# Clock App

import time
import math
from apps.base import App
from core.ui import cls, header, use_font, draw_ring


def two(n):
    return "{:02d}".format(n)


class ClockApp(App):
    title = "Reloj"
    tick_ms = 200
    
    def draw_icon(self, ctx, x, y, w, h):
        icon = [
            0b0000011111100000,
            0b0001100110011000,
            0b0010000000000100,
            0b0100000000001010,
            0b0100000000010010,
            0b1000010000100001,
            0b1000001001000001,
            0b1100000110000011,
            0b1100000110000011,
            0b1000000000000001,
            0b1000000000000001,
            0b0100000000000010,
            0b0100000000000010,
            0b0010000000000100,
            0b0001100110011000,
            0b0000011111100000,
        ]
        start_x = x + (w - 16) // 2  # center horizontally
        start_y = y + (h - 12) // 2  # center vertically (usually 0 since h=16)
    
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):  # check if bit is set
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def fmt(self, ctx, tm):
        if ctx.settings.get("clock_24h", True):
            return "{}:{}:{}".format(two(tm[3]), two(tm[4]), two(tm[5]))
        h = tm[3]
        suf = "AM" if h < 12 else "PM"
        h = h % 12 or 12
        return "{}:{}:{} {}".format(two(h), two(tm[4]), two(tm[5]), suf)
    
    def month_name(self, m):
        months = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", 
                  "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
        return months[m - 1]
    
    def draw(self, ctx):
        tm = time.localtime()
        cls(ctx)
        header(ctx, "Reloj")
        
        # Date Format: DD/MONTH/YYYY
        use_font(ctx, "8")
        date_str = "{}/{}/{}".format(tm[2], self.month_name(tm[1]), tm[0])
        ctx.d.text(date_str, 2, 16, ctx.W, 1)
        
        # Time Format: HH:MM:SS
        use_font(ctx, "14")
        ctx.d.text(self.fmt(ctx, tm), 2, 24, ctx.W, 1)
        
        # Hint for shortcut
        use_font(ctx, "6")
        ctx.d.text("s=set time", 2, ctx.H - 6, ctx.W, 1)
        
        draw_ring(ctx, 96, 36, 25, 2)
        
        # agujas (clock hands)
        h, m, s = tm[3], tm[4], tm[5]
        
        def endpoint(r, ang_deg):
            rad = math.radians(ang_deg - 90)
            cx, cy = 96, 36
            return int(cx + math.cos(rad) * r), int(cy + math.sin(rad) * r)
        
        ha = (h % 12 + m / 60) * 30
        ma = m * 6 + s / 10
        sa = s * 6
        
        x, y = endpoint(14, ha)
        ctx.d.line(96, 36, x, y)
        x, y = endpoint(20, ma)
        ctx.d.line(96, 36, x, y)
        x, y = endpoint(23, sa)
        ctx.d.line(96, 36, x, y)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'), 27):
            return "pop"
        elif k == ord('s'):
            from apps.settime import SetTimeApp
            return ("push", SetTimeApp())

