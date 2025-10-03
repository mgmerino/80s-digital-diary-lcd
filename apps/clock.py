# Clock App

import time
import math
from apps.base import App
from core.ui import cls, header, use_font, draw_ring, rect_frame


def two(n):
    return "{:02d}".format(n)


class ClockApp(App):
    title = "Reloj"
    tick_ms = 200
    quotes = []
    show_quote_popup = False
    
    @classmethod
    def load_quotes(cls):
        """Load quotes from file if not already loaded"""
        if not cls.quotes:
            try:
                with open('/assets/quotes.txt', 'r') as f:
                    cls.quotes = [line.strip() for line in f if line.strip()]
            except:
                cls.quotes = ["Keep moving forward!"]
        return cls.quotes
    
    def get_daily_quote(self):
        """Get a consistent quote for the current day"""
        quotes = self.load_quotes()
        if not quotes:
            return ""
        
        # Use day of year to select quote (same quote all day)
        tm = time.localtime()
        day_of_year = tm[7]  # Julian day (1-366)
        quote_idx = day_of_year % len(quotes)
        
        full_quote = quotes[quote_idx]
        # Split quote and author if present
        if '~' in full_quote:
            quote, author = full_quote.split('~', 1)
            return quote.strip(), author.strip()
        return full_quote, ""
    
    def wrap_text(self, text, max_width, font_size=3):
        """Wrap text to fit within max_width pixels"""
        max_chars = max_width // font_size
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, break it
                    lines.append(word[:max_chars])
                    current_line = word[max_chars:]
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def draw_quote_popup(self, ctx):
        """Draw a beautiful popup window with the daily quote"""
        quote, author = self.get_daily_quote()
        if not quote:
            return
        
        # Popup dimensions - larger popup with smaller margins
        margin = 4
        padding = 4
        popup_x = margin
        popup_y = margin
        popup_w = ctx.W - (2 * margin)
        popup_h = ctx.H - (2 * margin)
        
        # Fill background
        ctx.d.set_pen(ctx.BG)
        ctx.d.rectangle(popup_x, popup_y, popup_w, popup_h)
        ctx.d.set_pen(ctx.INK)
        
        # Draw outer decorative border (double frame)
        rect_frame(ctx, popup_x, popup_y, popup_w, popup_h, 1)
        rect_frame(ctx, popup_x + 2, popup_y + 2, popup_w - 4, popup_h - 4, 1)
        
        # Draw corner decorations
        corner_size = 4
        for cx, cy in [(popup_x, popup_y), 
                       (popup_x + popup_w - corner_size, popup_y),
                       (popup_x, popup_y + popup_h - corner_size),
                       (popup_x + popup_w - corner_size, popup_y + popup_h - corner_size)]:
            ctx.d.rectangle(cx, cy, corner_size, corner_size)
        
        # Title bar
        use_font(ctx, "8")
        title_text = "Daily Quote"
        title_y = popup_y + padding
        # Center the title (font 8 is ~4-5px per char)
        ctx.d.text(title_text, popup_x + (popup_w - len(title_text) * 4) // 2, 
                   title_y, ctx.W, 1)
        
        # Draw line under title
        line_y = title_y + 10
        ctx.d.line(popup_x + padding, line_y, 
                   popup_x + popup_w - padding, line_y)
        
        # Wrap and display quote text with larger font
        use_font(ctx, "8")
        text_area_width = popup_w - (2 * padding) - 4
        quote_lines = self.wrap_text(quote, text_area_width, font_size=5)
        
        # Start quote text closer to the line
        y_pos = line_y + 4
        line_spacing = 10
        max_quote_lines = 3  # Show up to 3 lines of quote
        
        # Draw the quote lines
        for i, line in enumerate(quote_lines):
            if i >= max_quote_lines:
                break
            if y_pos > popup_y + popup_h - 22:  # Leave room for author
                break
            ctx.d.text(line, popup_x + padding + 2, y_pos, ctx.W, 1)
            y_pos += line_spacing
        
        # Display author
        if author:
            use_font(ctx, "8")
            author_text = "- " + author
            # Position author below last quote line or at bottom
            author_y = min(y_pos + 2, popup_y + popup_h - padding - 12)
            # Wrap author if too long
            max_author_chars = (text_area_width // 5) + 2
            if len(author_text) > max_author_chars:
                author_text = author_text[:max_author_chars - 2] + ".."
            # Right-align the author
            ctx.d.text(author_text, popup_x + popup_w - len(author_text) * 5 - padding - 2, 
                       author_y, ctx.W, 1)
        
        # Close instruction at bottom
        # use_font(ctx, "6")
        # close_text = "[k] Close"
        # close_y = popup_y + popup_h - padding - 5
        # ctx.d.text(close_text, popup_x + padding + 2, close_y, ctx.W, 1)
    
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
        def endpoint(r, ang_deg):
            rad = math.radians(ang_deg - 90)
            cx, cy = x_center, y_center
            return int(cx + math.cos(rad) * r), int(cy + math.sin(rad) * r)
        
        
        # Time Format: HH:MM:SS
        use_font(ctx, "6")
        ctx.d.text(self.fmt(ctx, tm), 0, 0, ctx.W, 2)

        # Date Format: DD/MONTH/YYYY
        use_font(ctx, "8")
        date_str = "{}/{}/{}".format(tm[2], self.month_name(tm[1]), tm[0])
        ctx.d.text(date_str, 2, 16, ctx.W, 1)
        
        # Hints at bottom
        use_font(ctx, "6")
        ctx.d.text("k=quote  s=set time", 2, ctx.H - 6, ctx.W, 1)
        # clock hands
        h, m, s = tm[3], tm[4], tm[5]
        ha = (h % 12 + m / 60) * 30
        ma = m * 6 + s / 10
        sa = s * 6

        # clock face
        x_center, y_center = 98, 30
        radius = 28
        draw_ring(ctx, x_center, y_center, radius, 2)
        
        # Draw hour markers
        for i in range(12):
            angle = (i * 30) + 30
            # Cardinal hours (12, 3, 6, 9) get 3px markers, others get 2px
            # i=11→12, i=2→3, i=5→6, i=8→9
            marker_length = 4 if i in (11, 2, 5, 8) else 0
            x1, y1 = endpoint(radius, angle)
            x2, y2 = endpoint(radius - marker_length, angle)
            ctx.d.line(x1, y1, x2, y2)
        
        for i in range(12):
            x, y = endpoint(radius - 8, (i * 30) + 30)
            num_str = str(i+1)
            # Center the text: offset by ~half character width and height
            # Font "6" is about 3-4px wide per digit, 6px tall
            text_w = len(num_str) * 3  # approximate width
            text_h = 6
            ctx.d.text(num_str, x - text_w // 2, y - text_h // 2, ctx.W, 1)

        x, y = endpoint(14, ha)
        ctx.d.line(x, y, x_center, y_center)
        x, y = endpoint(20, ma)
        ctx.d.line(x, y, x_center, y_center)
        x, y = endpoint(23, sa)
        ctx.d.line(x, y, x_center, y_center)
        
        # Draw quote popup on top if active
        if self.show_quote_popup:
            self.draw_quote_popup(ctx)
    
    def handle_key(self, ctx, k):
        if k == ord('q'):
            return "pop"
        elif k == 27:  # ESC
            return "pop"
        elif k == ord('k'):
            # Toggle quote popup
            self.show_quote_popup = not self.show_quote_popup
        elif k == ord('s'):
            from apps.settime import SetTimeApp
            return ("push", SetTimeApp())

