# Calculator App

from apps.base import App
from core.ui import cls, header, use_font


class CalculatorApp(App):
    title = "Calc"
    tick_ms = 100
    
    def __init__(self):
        self.expr = ""
        self.result = ""
        self.allowed = set("0123456789+-*/(). ")
    
    def draw_icon(self, ctx, x, y, w, h):
        icon = [
            0b0000000000000000,
            0b0000111111110000,
            0b0001000000001000,
            0b0001001111001000,
            0b0001010000101000,
            0b0001010000101000,
            0b0001001111001000,
            0b0001000000001000,
            0b0001010101001000,
            0b0001000000001000,
            0b0001010101001000,
            0b0001000000001000,
            0b0001010101101000,
            0b0001000000001000,
            0b0000111111110000,
            0b0000000000000000,
        ]
        start_x = x + (w - 16) // 2  # center horizontally
        start_y = y + (h - 12) // 2  # center vertically (usually 0 since h=16)
    
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):  # check if bit is set
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def draw(self, ctx):
        cls(ctx)
        header(ctx, "Calc")
        use_font(ctx, "6")
        ctx.d.text("Expr:", 2, 12, ctx.W, 1)
        ctx.d.text(self.expr[-20:], 2, 18, ctx.W, 1)
        ctx.d.text("Res: {}".format(self.result[:20]), 2, 28, ctx.W, 1)
        use_font(ctx, "8")
        ctx.d.text("Enter=eval c=clear q=salir", 2, ctx.H - 8, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'), 27):
            return "pop"
        if k in (8, 127):
            self.expr = self.expr[:-1] if self.expr else ""
            return None
        if k == ord('c'):
            self.expr, self.result = "", ""
            return None
        if k == 13:
            try:
                if self.expr.strip():
                    self.result = str(self.safe_eval(self.expr.strip()))
                else:
                    self.result = ""
            except:
                self.result = "Error"
            return None
        try:
            ch = bytes([k]).decode()
        except:
            ch = ""
        if ch in self.allowed:
            self.expr += ch
    
    def safe_eval(self, expr):
        if not all(ch in self.allowed for ch in expr):
            raise ValueError("bad char")
        return eval(expr, {"__builtins__": None}, {})

