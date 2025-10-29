# Base App Classes

from core.ui import cls, rect_frame, use_font
from core.input import read_key


class App:
    title = "App"
    tick_ms = 200  # refresco recomendado
    
    def draw(self, ctx):
        pass
    
    def handle_key(self, ctx, k):
        return None  # devolver "pop", ("push", nuevaApp), None


class AppManager:
    def __init__(self, ctx, home_app):
        self.ctx = ctx
        self.stack = [home_app]
        self._last = ctx.hal_clock.ticks_ms()
    
    def push(self, app):
        self.stack.append(app)
    
    def pop(self):
        if len(self.stack) > 1:
            self.stack.pop()
    
    def run(self):
        ctx = self.ctx
        while True:
            app = self.stack[-1]
            now = ctx.hal_clock.ticks_ms()
            if ctx.hal_clock.ticks_diff(now, self._last) >= app.tick_ms:
                app.draw(ctx)
                ctx.d.update()
                # allow draw() to request closing
                if getattr(app, "_should_pop", False):
                    try:
                        delattr(app, "_should_pop")
                    except:
                        pass
                    self.pop()
                    continue
                self._last = now
            k = read_key(ctx)
            if k is not None:
                act = app.handle_key(ctx, k)
                if act == "pop":
                    self.pop()
                elif isinstance(act, tuple) and act[0] == "push":
                    self.push(act[1])
            ctx.hal_clock.sleep_ms(5)


class IconMenu(App):
    title = "Menu"
    
    def __init__(self, entries):
        self.entries = entries
        self.cols, self.rows = 3, 2
        self.tilew, self.tileh = 40, 28
        self.gx, self.gy = 2, 2
        self.per = self.cols * self.rows
        self.page = 0
        self.sel = 0
    
    def pages(self):
        return (len(self.entries) + self.per - 1) // self.per
    
    def current_items(self):
        s = self.page * self.per
        return self.entries[s:s + self.per]
    
    def draw(self, ctx):
        cls(ctx)
        items = self.current_items()
        # calculate grid size and position
        gridw = self.cols * self.tilew + (self.cols - 1) * self.gx
        gridh = self.rows * self.tileh + (self.rows - 1) * self.gy
        base_x = (ctx.W - gridw) // 2
        base_y = (ctx.H - gridh) // 2

        for i, ent in enumerate(items):
            r = i // self.cols
            c = i % self.cols
            x = base_x + c * (self.tilew + self.gx)
            y = base_y + r * (self.tileh + self.gy)
            rect_frame(ctx, x, y, self.tilew, self.tileh, 1)
            
            # every app can have a draw_icon method
            if hasattr(ent["app"], "draw_icon"):
                ent["app"].draw_icon(ctx, x, y, self.tilew - 2, self.tileh - 12)
            # label
            label = ent["name"][:8]
            use_font(ctx, "6")
            ctx.d.text(label, x + (self.tilew - len(label) * 6) // 2, y + self.tileh - 8, ctx.W, 1)
            
            # invert pixels on the label text for selected item
            if i == self.sel:
                ctx.d.set_pen(ctx.INK)
                ctx.d.rectangle(x, y + self.tileh - 8, self.tilew, 8)
                ctx.d.set_pen(ctx.BG)
                ctx.d.text(label, x + (self.tilew - len(label) * 6) // 2, y + self.tileh - 7, ctx.W, 1)
                ctx.d.set_pen(ctx.INK)
    
    def handle_key(self, ctx, k):
        per = self.per
        # CardKB arrow keys: 0xB4=Left, 0xB5=Up, 0xB6=Down, 0xB7=Right
        arrow_key = None
        if k == 0xB5:  # Up arrow
            arrow_key = 'UP'
        elif k == 0xB6:  # Down arrow
            arrow_key = 'DOWN'
        elif k == 0xB7:  # Right arrow
            arrow_key = 'RIGHT'
        elif k == 0xB4:  # Left arrow
            arrow_key = 'LEFT'
        elif k == 27:  # ESC to quit
            return "pop"
        elif k == ord('q'):
            return "pop"
        
        # Navigation with arrow keys
        abs_sel = self.page * self.per + self.sel
        
        if arrow_key == 'LEFT':
            # Move left, stay in same row
            if self.sel > 0:
                self.sel -= 1
        elif arrow_key == 'RIGHT':
            # Move right, wrap to next row
            if abs_sel + 1 < len(self.entries):
                self.sel += 1
        elif arrow_key == 'UP':
            # Move up one row
            if self.sel >= self.cols:
                self.sel -= self.cols
        elif arrow_key == 'DOWN':
            # Move down one row
            new_sel = self.sel + self.cols
            new_abs = self.page * self.per + new_sel
            if new_abs < len(self.entries):
                self.sel = new_sel
        # paginate
        elif k in (ord('.'), ord('L')) and self.page < self.pages() - 1:
            self.page += 1
            self.sel = 0
        elif k in (ord(','), ord('H')) and self.page > 0:
            self.page -= 1
            self.sel = 0
        elif k == 13:  # Enter
            idx = self.page * self.per + self.sel
            if idx < len(self.entries):
                return ("push", self.entries[idx]["app"])
        return None

