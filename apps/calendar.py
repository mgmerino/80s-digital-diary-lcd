# Calendar App
# TODO: Copiar CalendarApp del main.py original

import time
from apps.base import App
from core.ui import cls, header, use_font


class CalendarApp(App):
    title = "Cal"
    tick_ms = 200
    
    def __init__(self):
        tm = time.localtime()
        self.y, self.m = tm[0], tm[1]
    
    def draw_icon(self, ctx, x, y, w, h):
        icon = [
            0b0111111111111110,
            0b1000000000000001,
            0b1001001001001001,
            0b1001010101101001,
            0b1001011101011001,
            0b1011010101001001,
            0b1000000000000001,
            0b1001111001111001,
            0b1001001001001001,
            0b1000001001001001,
            0b1000010001111001,
            0b1000100001001001,
            0b1001000001001001,
            0b1001111001111001,
            0b1000000000000001,
            0b0111111111111110,
            ]
        start_x = x + (w - 16) // 2  # center horizontally
        start_y = y + (h - 12) // 2  # center vertically (usually 0 since h=16)
    
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):  # check if bit is set
                    ctx.d.pixel(start_x + col, start_y + row)

    def draw(self, ctx):
        # calculate first day of month
        first_w = self.weekday(self.y, self.m, 1)
        dim = self.days_in_month(self.y, self.m)
        cls(ctx); header(ctx, "Calendar")
        
        use_font(ctx, "6")
        month_year = "{} {}".format(self.month_name(self.m), self.y)
        month_x = (ctx.W - len(month_year) * 6) // 2
        ctx.d.text(month_year, month_x, 12, ctx.W, 1)
        
        # Draw each weekday header at fixed positions
        weekdays = ["M", "T", "W", "T", "F", "S", "S"]
        cell_width = 18  # pixels per day column
        start_x = (ctx.W - 7 * cell_width) // 2
        header_y = 20
        header_offset = 3  # offset to adjust header alignment (change this value)
        
        for i, wd in enumerate(weekdays):
            x = start_x + i * cell_width + header_offset
            ctx.d.text(wd, x, header_y, ctx.W, 1)
        
        # Get today's date for highlighting
        tm_now = time.localtime()
        today_year, today_month, today_day = tm_now[0], tm_now[1], tm_now[2]
        is_current_month = (self.y == today_year and self.m == today_month)
        
        # Draw each day at fixed tile positions
        day = 1
        day_start_y = 28
        row_height = 7
        
        for week in range(6):
            for dow in range(7):
                if week == 0 and dow < first_w:
                    continue  # skip days before month starts
                if day > dim:
                    break  # month ended
                
                x = start_x + dow * cell_width
                y = day_start_y + week * row_height
                
                # Highlight today's date
                if is_current_month and day == today_day:
                    ctx.d.set_pen(ctx.INK)
                    ctx.d.rectangle(x, y, 12, 7)  # filled rectangle behind day
                    ctx.d.set_pen(ctx.BG)
                    ctx.d.text("{:2d}".format(day), x, y, ctx.W, 1)
                    ctx.d.set_pen(ctx.INK)
                else:
                    ctx.d.text("{:2d}".format(day), x, y, ctx.W, 1)
                
                day += 1
            if day > dim:
                break
        
        use_font(ctx, "8")
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        # Arrow keys
        if k == 0xB4:  # Left - previous month
            self.m -= 1
            if self.m == 0: self.m = 12; self.y -= 1
        elif k == 0xB7:  # Right - next month
            self.m += 1
            if self.m == 13: self.m = 1; self.y += 1
        elif k == 0xB5:  # Up - previous year
            self.y -= 1
        elif k == 0xB6:  # Down - next year
            self.y += 1
        elif k == ord('t'):  # Today
            tm = time.localtime(); self.y, self.m = tm[0], tm[1]
    def weekday(self, y, m, d):
        t = [0,3,2,5,0,3,5,1,4,6,2,4]
        if m < 3: y -= 1
        w = (y + y//4 - y//100 + y//400 + t[m-1] + d) % 7
        return (w - 1) % 7
    def is_leap(self, y):
        return (y%4==0 and y%100!=0) or (y%400==0)
    def days_in_month(self, y, m):
        if m==2: return 29 if self.is_leap(y) else 28
        return 31 if m in (1,3,5,7,8,10,12) else 30
    def month_name(self, m):
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", 
                  "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        return months[m - 1]
