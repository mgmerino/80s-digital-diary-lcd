# Settings App
# TODO: Copiar SettingsApp, ThemeChooserApp, WBrightnessApp del main.py original

from apps.base import App
from core.ui import cls, header


class SettingsApp(App):
    title = "Config"
    tick_ms = 300
    
    def __init__(self):
        self.idx = 0
        self.items = ["Tema", "Brillo W", "Set Time", "Volver"]
    
    def draw_icon(self, ctx, x, y, w, h):
        # TODO: Copiar icon del main.py original
        pass
    
    def draw(self, ctx):
        cls(ctx)
        header(ctx, "Config")
        ctx.d.text("TODO: Migrar desde main.py", 2, 20, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'), 27):
            return "pop"
        return None

