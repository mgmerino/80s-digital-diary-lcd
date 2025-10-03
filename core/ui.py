# UI Helper Functions

def use_font(ctx, size="8"):
    if size == "6":
        ctx.d.set_font("bitmap6")
    elif size == "8":
        ctx.d.set_font("bitmap8")
    elif size == "14":
        ctx.d.set_font("bitmap14_outline")
    elif size == "sans":
        ctx.d.set_font("sans")
    elif size == "cursive":
        ctx.d.set_font("cursive")


def cls(ctx):
    d = ctx.d
    d.set_pen(ctx.BG)
    d.clear()
    d.set_pen(ctx.INK)


def header(ctx, title):
    d = ctx.d
    W = ctx.W
    d.set_pen(ctx.INK)
    d.rectangle(0, 0, W, 10)
    d.set_pen(ctx.BG)
    d.text(title[:16], 2, 1, W, 1)
    d.set_pen(ctx.INK)


def rect_frame(ctx, x, y, w, h, th=1):
    d = ctx.d
    d.rectangle(x, y, w, h)
    d.set_pen(ctx.BG)
    d.rectangle(x + th, y + th, max(0, w - 2 * th), max(0, h - 2 * th))
    d.set_pen(ctx.INK)


def draw_ring(ctx, cx, cy, r, th=2):
    d = ctx.d
    d.circle(cx, cy, r)
    inner = r - max(1, th)
    if inner > 0:
        d.set_pen(ctx.BG)
        d.circle(cx, cy, inner)
    d.set_pen(ctx.INK)

