# SetTime App
# TODO: Copiar SetTimeApp del main.py original

import time
from apps.base import App
from core.ui import cls, header, use_font


class SetTimeApp(App):
    title = "SetTime"
    tick_ms = 100
    
    def __init__(self):
        tm = time.localtime()
        self.year = tm[0]
        self.month = tm[1]
        self.day = tm[2]
        self.hour = tm[3]
        self.minute = tm[4]
        self.second = 0
        self.field = 0  # 0=year, 1=month, 2=day, 3=hour, 4=minute, 5=second
        self.fields = ["Year", "Month", "Day", "Hour", "Min", "Sec"]
    def draw_icon(self, ctx, x, y, w, h):
        # No icon
        pass
    
    def draw(self, ctx):
        cls(ctx); header(ctx, "Set Date/Time")
        use_font(ctx, "8")
        
        # Show current values
        ctx.d.text("{:04d}-{:02d}-{:02d}".format(self.year, self.month, self.day), 10, 14, ctx.W, 1)
        ctx.d.text("{:02d}:{:02d}:{:02d}".format(self.hour, self.minute, self.second), 10, 22, ctx.W, 1)
        
        use_font(ctx, "6")
        # Show which field is selected
        ctx.d.text("Edit: {}".format(self.fields[self.field]), 2, 34, ctx.W, 1)
        vals = [self.year, self.month, self.day, self.hour, self.minute, self.second]
        ctx.d.text("Value: {}".format(vals[self.field]), 2, 42, ctx.W, 1)
        
        ctx.d.text("Up/Dn=val", 72, 12, ctx.W, 1)
        ctx.d.text("L/R=field", 72, 22, ctx.W, 1)
        ctx.d.text("Enter=save q=cancel", 2, 50, ctx.W, 1)
    def handle_key(self, ctx, k):
        if k == ord('q') or k == 27:
            return "pop"
        # Arrow keys
        if k == 0xB7:  # Right - next field
            self.field = (self.field + 1) % 6
        elif k == 0xB4:  # Left - previous field
            self.field = (self.field - 1) % 6
        elif k == 0xB5:  # Up - increment
            if self.field == 0: self.year = min(2099, self.year + 1)
            elif self.field == 1: self.month = (self.month % 12) + 1
            elif self.field == 2: self.day = min(31, self.day + 1)
            elif self.field == 3: self.hour = (self.hour + 1) % 24
            elif self.field == 4: self.minute = (self.minute + 1) % 60
            elif self.field == 5: self.second = (self.second + 1) % 60
        elif k == 0xB6:  # Down - decrement
            if self.field == 0: self.year = max(2020, self.year - 1)
            elif self.field == 1: self.month = ((self.month - 2) % 12) + 1
            elif self.field == 2: self.day = max(1, self.day - 1)
            elif self.field == 3: self.hour = (self.hour - 1) % 24
            elif self.field == 4: self.minute = (self.minute - 1) % 60
            elif self.field == 5: self.second = (self.second - 1) % 60
        elif k == 13:  # Enter - save
            # Set the RTC
            # RTC datetime format: (year, month, day, weekday, hour, minute, second, subseconds)
            # We'll calculate weekday
            wday = self.calc_weekday(self.year, self.month, self.day)
            ctx.rtc.datetime((self.year, self.month, self.day, wday, self.hour, self.minute, self.second, 0))
            return "pop"
        return None
    def calc_weekday(self, y, m, d):
        # Zeller's congruence for weekday (0=Mon, 6=Sun)
        if m < 3:
            m += 12
            y -= 1
        q = d
        k = y % 100
        j = y // 100
        h = (q + ((13 * (m + 1)) // 5) + k + (k // 4) + (j // 4) - (2 * j)) % 7
        # Convert to Monday=0 format
        return (h + 5) % 7

