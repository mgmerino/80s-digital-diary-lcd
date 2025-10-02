from apps.base import App
from core.ui import cls, header 
from core.utils import Utils
from core.utils import AppHelper

class MemosApp(App):
    title = "Memos"
    tick_ms = 200
    
    def draw_icon(self, ctx, x,y,w,h):
        icon = [
            0b0000001100000000,
            0b0000010010000000,
            0b0000100001000000,
            0b0001001000100000,
            0b0010010100010000,
            0b0100001000001000,
            0b1000010011000100,
            0b1000101100100010,
            0b0100001010010001,
            0b0010111111111010,
            0b0001001011001111,
            0b0000100100001111,
            0b0000010011111111,
            0b0000001000101111,
            0b0000000101000000,
            0b0000000010000000,
        ]
        start_x = x + (w - 16) // 2  # center horizontally
        start_y = y + (h - 12) // 2  # center vertically (usually 0 since h=16)
    
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):  # check if bit is set
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def fmt_memo(self, m):
        if isinstance(m, dict):
            return "{}  {}".format(m.get('title',''), m.get('text',''))
        return str(m)
    
    def add_memo(self, ctx):
        title = Utils.prompt_input(ctx, "Titulo")
        if not title or not title.strip(): return
        text = Utils.prompt_input(ctx, "Texto") or ""
        memos = ctx.ds.load_memos()
        memos.append({"title": title.strip(), "text": text.strip()})
        ctx.ds.save_memos(memos)
    
    def draw(self, ctx):
        AppHelper.list_paginated(ctx, self, self.title, ctx.ds.load_memos(), self.fmt_memo, self.add_memo)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        return None

