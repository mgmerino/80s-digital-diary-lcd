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
        self.mode = 'calendar'  # 'calendar' or 'day_view'
        self.selected_day = tm[2]  # Currently selected day
        self.scroll_offset = 0
    
    def draw_icon(self, ctx, x, y, w, h):
        icon = [
            0b0111111111111110,
            0b1111111111111111,
            0b1111011011011011,
            0b1111010101001011,
            0b1111010001010011,
            0b1100010101011011,
            0b1111111111111111,
            0b1000000000000001,
            0b1001111001111001,
            0b1001001001001001,
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

    def get_todos_for_date(self, ctx, year, month, day):
        """Get todos due on a specific date"""
        db = ctx.ds.load()
        todos = db.get('todos', [])
        
        matching_todos = []
        for todo in todos:
            due_date = todo.get('due_date')
            if due_date:
                due_time = time.localtime(due_date)
                if due_time[0] == year and due_time[1] == month and due_time[2] == day:
                    matching_todos.append(todo)
        
        return matching_todos
    
    def has_todos_on_date(self, ctx, year, month, day):
        """Check if a date has any todos"""
        return len(self.get_todos_for_date(ctx, year, month, day)) > 0
    
    def draw_calendar(self, ctx):
        """Draw calendar view with todo indicators"""
        # calculate first day of month
        first_w = self.weekday(self.y, self.m, 1)
        dim = self.days_in_month(self.y, self.m)
        cls(ctx)
        # No header to save space
        
        use_font(ctx, "6")
        # Month/year at top
        month_year = "{} {}".format(self.month_name(self.m), self.y)
        month_x = (ctx.W - len(month_year) * 6) // 2
        ctx.d.text(month_year, month_x, 2, ctx.W, 1)
        
        # Draw each weekday header at fixed positions
        weekdays = ["M", "T", "W", "T", "F", "S", "S"]
        cell_width = 18  # pixels per day column
        start_x = (ctx.W - 7 * cell_width) // 2
        header_y = 10
        header_offset = 3  # offset to adjust header alignment
        
        for i, wd in enumerate(weekdays):
            x = start_x + i * cell_width + header_offset
            ctx.d.text(wd, x, header_y, ctx.W, 1)
        
        # Get today's date for highlighting
        tm_now = time.localtime()
        today_year, today_month, today_day = tm_now[0], tm_now[1], tm_now[2]
        is_current_month = (self.y == today_year and self.m == today_month)
        
        # Draw each day at fixed tile positions
        day = 1
        day_start_y = 18  # Start higher since no header
        row_height = 7
        
        for week in range(6):
            for dow in range(7):
                if week == 0 and dow < first_w:
                    continue  # skip days before month starts
                if day > dim:
                    break  # month ended
                
                x = start_x + dow * cell_width
                y = day_start_y + week * row_height
                
                # Check if this date has todos
                has_todos = self.has_todos_on_date(ctx, self.y, self.m, day)
                
                # Highlight today's date
                if is_current_month and day == today_day:
                    ctx.d.set_pen(ctx.INK)
                    ctx.d.rectangle(x, y, 12, 7)  # filled rectangle behind day
                    ctx.d.set_pen(ctx.BG)
                    ctx.d.text("{:2d}".format(day), x, y, ctx.W, 1)
                    ctx.d.set_pen(ctx.INK)
                # Highlight selected day (for navigation)
                elif day == self.selected_day:
                    ctx.d.rectangle(x - 1, y - 1, 13, 8)  # frame around selected
                    ctx.d.text("{:2d}".format(day), x, y, ctx.W, 1)
                else:
                    ctx.d.text("{:2d}".format(day), x, y, ctx.W, 1)
                
                # Draw dot indicator if date has todos
                if has_todos:
                    dot_x = x + 11
                    dot_y = y + 5
                    # Draw a small dot (2x2 pixels)
                    ctx.d.pixel(dot_x, dot_y)
                    ctx.d.pixel(dot_x + 1, dot_y)
                
                day += 1
            if day > dim:
                break
        
        # Help text - positioned safely at bottom
        use_font(ctx, "6")
        ctx.d.text("Enter=view  t=today  q=quit", 2, 57, ctx.W, 1)
    
    def draw_day_view(self, ctx):
        """Draw todos for selected day"""
        cls(ctx)
        # No header, just show date at top
        
        use_font(ctx, "6")
        date_str = "{} {} {}".format(self.selected_day, self.month_name(self.m)[:3], self.y)
        date_x = (ctx.W - len(date_str) * 6) // 2
        ctx.d.text(date_str, date_x, 2, ctx.W, 1)
        
        todos = self.get_todos_for_date(ctx, self.y, self.m, self.selected_day)
        
        if not todos:
            ctx.d.text("No todos for this day", 2, 14, ctx.W, 1)
        else:
            # Display todos (up to 4 visible)
            y = 14
            max_y = 55
            
            for i, todo in enumerate(todos):
                if y + 10 > max_y:
                    break
                
                text = todo.get('text', '')
                completed = todo.get('completed', False)
                has_alarm = todo.get('alarm', False)
                
                # Status indicator
                status = "[X]" if completed else "[ ]"
                
                # Preview text (adjust for status and alarm)
                max_chars = 14 if has_alarm else 17
                preview = text[:max_chars] + "..." if len(text) > max_chars else text
                
                # Draw todo
                todo_str = "{} {}".format(status, preview)
                ctx.d.text(todo_str, 2, y, ctx.W, 1)
                
                # Draw alarm icon if present
                if has_alarm:
                    ctx.d.text("!", ctx.W - 8, y, ctx.W, 1)  # Simple alarm indicator
                
                y += 10
        
        # Help text - positioned safely at bottom
        use_font(ctx, "6")
        ctx.d.text("q=back", 2, 57, ctx.W, 1)
    
    def draw(self, ctx):
        if self.mode == 'calendar':
            self.draw_calendar(ctx)
        elif self.mode == 'day_view':
            self.draw_day_view(ctx)
    
    def handle_key(self, ctx, k):
        if self.mode == 'day_view':
            # Day view mode
            if k in (ord('q'), 27):
                self.mode = 'calendar'
                return None
        else:
            # Calendar mode
            if k in (ord('q'), 27):
                return "pop"
            
            # Arrow keys
            if k == 0xB4:  # Left - previous month
                self.m -= 1
                if self.m == 0:
                    self.m = 12
                    self.y -= 1
                # Adjust selected day if it's out of range
                dim = self.days_in_month(self.y, self.m)
                if self.selected_day > dim:
                    self.selected_day = dim
            elif k == 0xB7:  # Right - next month
                self.m += 1
                if self.m == 13:
                    self.m = 1
                    self.y += 1
                # Adjust selected day if it's out of range
                dim = self.days_in_month(self.y, self.m)
                if self.selected_day > dim:
                    self.selected_day = dim
            elif k == 0xB5:  # Up - previous day
                self.selected_day -= 1
                if self.selected_day < 1:
                    # Go to previous month
                    self.m -= 1
                    if self.m == 0:
                        self.m = 12
                        self.y -= 1
                    self.selected_day = self.days_in_month(self.y, self.m)
            elif k == 0xB6:  # Down - next day
                dim = self.days_in_month(self.y, self.m)
                self.selected_day += 1
                if self.selected_day > dim:
                    # Go to next month
                    self.m += 1
                    if self.m == 13:
                        self.m = 1
                        self.y += 1
                    self.selected_day = 1
            elif k == ord('t'):  # Today
                tm = time.localtime()
                self.y, self.m, self.selected_day = tm[0], tm[1], tm[2]
            elif k == 13:  # Enter - view todos for selected day
                self.mode = 'day_view'
        
        return None
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
