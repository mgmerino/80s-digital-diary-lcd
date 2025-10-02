# Contacts App
# TODO: Copiar ContactsApp, AppHelper, Utils del main.py original

from apps.base import App
from core.ui import cls, header
from core.utils import Utils
from core.utils import AppHelper


class ContactsApp(App):
    title = "TEL"
    tick_ms = 200
    
    def draw_icon(self, ctx, x,y,w,h):
        icon =  [
            0b0011111111111110,
            0b0100000000000001,
            0b0100110000111001,
            0b0101001101000101,
            0b0101001000111001,
            0b0101001100000001,
            0b0101001001010101,
            0b0101001100000001,
            0b0101001001010101,
            0b0101001100000001,
            0b0101111001010101,
            0b0100010000000001,
            0b0100010000111001,
            0b0100010000000001,
            0b0011111111111110,
            0b0001110000000000,
        ]
        start_x = x + (w - 16) // 2  # center horizontally
        start_y = y + (h - 12) // 2  # center vertically (usually 0 since h=16)
    
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):  # check if bit is set
                    ctx.d.pixel(start_x + col, start_y + row)
    def fmt_contact(self, c):
        if isinstance(c, dict):
            return "{}  {}".format(c.get('name',''), c.get('phone',''))
        return str(c)
    def add_contact(self, ctx):
        name = Utils.prompt_input(ctx, "Nombre")
        if not name or not name.strip(): return
        phone = Utils.prompt_input(ctx, "Telefono (opcional)") or ""
        contacts = ctx.ds.load_contacts()
        contacts.append({"name": name.strip(), "phone": phone.strip()})
        ctx.ds.save_contacts(contacts)
    def draw(self, ctx):
        AppHelper.list_paginated(ctx, self, self.title, ctx.ds.load_contacts(), self.fmt_contact, self.add_contact)
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        return None

