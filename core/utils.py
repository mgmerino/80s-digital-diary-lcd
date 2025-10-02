import time
from core.ui import cls, header
from core.input import read_key

class Utils:
    @staticmethod
    def prompt_input(ctx, label, maxlen=24):
        buf = []
        while True:
            cls(ctx); header(ctx, label)
            ctx.d.text("".join(buf), 0, 16, ctx.W, 1)
            ctx.d.update()
            k = read_key(ctx)
            if k is None:
                time.sleep_ms(10); continue
            if k == 13:  # Enter
                return "".join(buf)
            if k in (8, 127):  # Backspace/Delete
                if buf: buf.pop()
                continue
            if k == 27:  # Esc
                return None
            try:
                ch = bytes([k]).decode()
            except:
                ch = ""
            if ch and len(buf) < maxlen:
                buf.append(ch)
class AppHelper:
    @staticmethod
    def list_paginated(ctx, app, title, items, fmt_fn, add_fn):
        page, size = 0, 6
        while True:
            cls(ctx); header(ctx, title)
            if not items:
                ctx.d.text("(vacio) a=añadir, q=salir", 0, 16, ctx.W, 1)
            else:
                start = page*size
                chunk = items[start:start+size]
                y = 12
                for i, it in enumerate(chunk, start=1):
                    ctx.d.text("{:02d}. {}".format(i+start, fmt_fn(it)), 0, y, ctx.W, 1); y += 8
                ctx.d.text("j/k=nav  a=añadir  q=salir", 0, ctx.H-8, ctx.W, 1)
            ctx.d.update()
            k = read_key(ctx)
            # Arrow keys ESC [ A/B/C/D
            if k == 27:
                k2 = read_key(ctx)
                if k2 == ord('['):
                    k3 = read_key(ctx)
                    if k3 == ord('A'): k = ord('k')  # Up
                    elif k3 == ord('B'): k = ord('j')  # Down
                    elif k3 == ord('C'): k = ord('l')  # Right
                    elif k3 == ord('D'): k = ord('h')  # Left
            if k is None: time.sleep_ms(20); continue
            if k in (ord('q'),27):
                try: setattr(app, "_should_pop", True)
                except: pass
                return
            if k == ord('a'):
                add_fn(ctx)
                # refresh and move to last page
                items = ctx.ds.load_contacts() if title=="TEL" else ctx.ds.load_memos()
                if items: page = max(0, (len(items)-1)//size)
                continue
            if k == ord('j') and (page+1)*size < len(items): page += 1
            if k == ord('k') and page>0: page -= 1
