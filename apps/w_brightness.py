from apps.base import App
from core.ui import cls, header


class WBrightnessApp(App):
    title="Brillo W"; tick_ms=200
    def draw(self, ctx):
        cls(ctx); header(ctx,"Brillo W")
        val = ctx.settings.get("w_brightness",64)
        ctx.d.text("W = {}".format(val), 2, 16, ctx.W, 1)
        ctx.d.text("h/l -/+8  q=salir", 2, 24, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        val = ctx.settings.get("w_brightness",64)
        if k==ord('h'): val=max(0,val-8)
        if k==ord('l'): val=min(255,val+8)
        if val!=ctx.settings.get("w_brightness"):
            ctx.settings["w_brightness"]=val
            ctx.ds.update_settings({"w_brightness":val})
            ctx.theme.apply()