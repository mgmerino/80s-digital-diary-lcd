# Games App
# TODO: Copiar GamesApp, SnakeApp, MazeApp del main.py original

from apps.base import App
from core.ui import cls, header


class GamesApp(App):
    title = "Games"
    tick_ms = 300
    
    def draw_icon(self, ctx, x, y, w, h):
        icon = [
            0b0000000000100000,
            0b0000000001000000,
            0b0000000010000000,
            0b0000000100000000,
            0b0000000100000000,
            0b0111111111111110,
            0b1000000000000001,
            0b1001000000001001,
            0b1011101010010001,
            0b1001000000100001,
            0b1000000000000001,
            0b0111111111111110,
            0b0000000000000000,
            0b0000000000000000,
            0b0000000000000000,
            0b0000000000000000,
        ]

        start_x = x + (w - 16) // 2
        start_y = y + (h - 12) // 2
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def draw(self, ctx):
        cls(ctx)
        header(ctx, "Games")
        ctx.d.text("TODO: Migrar desde main.py", 2, 20, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'), 27):
            return "pop"
        return None

