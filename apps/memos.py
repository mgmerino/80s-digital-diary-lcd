# Memos App
# TODO: Copiar MemosApp del main.py original

from apps.base import App
from core.ui import cls, header


class MemosApp(App):
    title = "Memos"
    tick_ms = 200
    
    def draw_icon(self, ctx, x, y, w, h):
        # TODO: Copiar icon del main.py original
        pass
    
    def draw(self, ctx):
        cls(ctx)
        header(ctx, "Memos")
        ctx.d.text("TODO: Migrar desde main.py", 2, 20, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'), 27):
            return "pop"
        return None

