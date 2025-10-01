# ===== main.py =====
from machine import I2C, Pin, RTC
from gfx_pack import GfxPack  # type: ignore
import time, math
try:
    import ujson as json
except:
    import json

# ---------- core: Contexto ----------
class Context:
    def __init__(self):
        self.gp = GfxPack()
        self.d  = self.gp.display
        self.W, self.H = self.d.get_bounds()
        self.d.set_font("bitmap8")
        self.INK, self.BG = 15, 0
        self.i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
        self.rtc = RTC()
        self.ds  = DataStore("agenda.json")
        self.settings = self.ds.load_settings({
            "theme":"amber", "w_brightness":64, "clock_24h":True,
            "ask_time_on_boot":True, "local_offset_min":120
        })
        self.theme = ThemeManager(self.gp, self.settings)
        self.theme.apply()

# ---------- core: UI helpers ----------
def use_font(ctx, size="8"):
    ctx.d.set_font("bitmap6" if size=="6" else "bitmap8")

def cls(ctx):
    d=ctx.d; d.set_pen(ctx.BG); d.clear(); d.set_pen(ctx.INK)

def header(ctx, title):
    d=ctx.d; W=ctx.W
    d.set_pen(ctx.INK); d.rectangle(0,0,W,10)
    d.set_pen(ctx.BG); d.text(title[:16], 2, 1, W, 1)
    d.set_pen(ctx.INK)

def rect_frame(ctx, x,y,w,h,th=1):
    d=ctx.d
    d.rectangle(x,y,w,h)
    d.set_pen(ctx.BG); d.rectangle(x+th,y+th,max(0,w-2*th),max(0,h-2*th))
    d.set_pen(ctx.INK)

def draw_ring(ctx, cx,cy,r,th=2):
    d=ctx.d
    d.circle(cx,cy,r)
    inner = r - max(1, th)
    if inner>0:
        d.set_pen(ctx.BG); d.circle(cx,cy,inner)
    d.set_pen(ctx.INK)

# ---------- core: Input (CardKB) ----------
CARDKB_ADDR = 0x5F
def read_key(ctx):
    try:
        b = ctx.i2c.readfrom(CARDKB_ADDR, 1)
        if not b: return None
        v = b[0]
        return None if v==0 else v
    except OSError:
        return None

# ---------- core: Storage ----------
class DataStore:
    def __init__(self, path):
        self.path = path
    def load(self):
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except:
            return {"contacts":[], "memos":[], "settings":{}}
    def save(self, db):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f: json.dump(db, f)
        try:
            import os
            if self.path in os.listdir(): os.remove(self.path)
            os.rename(tmp, self.path)
        except: pass
    def load_settings(self, defaults):
        db = self.load()
        s = db.get("settings", {})
        for k,v in defaults.items():
            s.setdefault(k, v)
        db["settings"] = s
        self.save(db)
        return s
    def update_settings(self, patch):
        db = self.load()
        db.setdefault("settings", {}).update(patch)
        self.save(db)
    def load_contacts(self):
        return self.load().get("contacts", [])
    def load_memos(self):
        return self.load().get("memos", [])
    def save_db(self):
        self.save(self.load())
    def save_contacts(self, contacts):
        db = self.load()
        db["contacts"] = contacts
        self.save(db)
    def save_memos(self, memos):
        db = self.load()
        db["memos"] = memos
        self.save(db)
        

# ---------- core: Tema ----------
THEMES = {
    "amber":  dict(r=64,g=32,b=0,w=20),
    "fosforo":dict(r=0,g=64,b=0,w=20),
    "hielo":  dict(r=0,g=0,b=64,w=24),
    "blanco": dict(r=0,g=0,b=0,w=64),
    "rojo":   dict(r=64,g=0,b=0,w=16),
}
class ThemeManager:
    def __init__(self, gp, settings):
        self.gp=gp; self.settings=settings
    def apply(self):
        t = (THEMES.get(self.settings.get("theme","amber")) or THEMES["amber"]).copy()
        t["w"] = max(0, min(255, self.settings.get("w_brightness", t["w"])))
        self.gp.set_backlight(t["r"], t["g"], t["b"], t["w"])

# ---------- core: App base y Manager ----------
class App:
    title = "App"
    tick_ms = 200  # refresco recomendado
    def draw(self, ctx): pass
    def handle_key(self, ctx, k): return None  # devolver "pop", ("push", nuevaApp), None

class AppManager:
    def __init__(self, ctx, home_app):
        self.ctx = ctx
        self.stack = [home_app]
        self._last = time.ticks_ms()
    def push(self, app): self.stack.append(app)
    def pop(self): 
        if len(self.stack)>1: self.stack.pop()
    def run(self):
        ctx=self.ctx
        while True:
            app = self.stack[-1]
            now=time.ticks_ms()
            if time.ticks_diff(now,self._last) >= app.tick_ms:
                app.draw(ctx); ctx.d.update()
                # allow draw() to request closing
                if getattr(app, "_should_pop", False):
                    try: delattr(app, "_should_pop")
                    except: pass
                    self.pop()
                    continue
                self._last = now
            k = read_key(ctx)
            if k is not None:
                act = app.handle_key(ctx, k)
                if act=="pop": self.pop()
                elif isinstance(act, tuple) and act[0]=="push":
                    self.push(act[1])
            time.sleep_ms(5)

# ---------- apps: Menú de iconos ----------
class IconMenu(App):
    title="Menu"
    def __init__(self, entries):
        self.entries = entries
        self.cols, self.rows = 3, 2
        # The display has a resolution of 128x64
        # so we need to calculate the size of the tiles
        # for 3 columns and 2 rows, the total width is 128
        self.tilew, self.tileh = 40, 28
        self.gx, self.gy = 2,2
        self.per = self.cols*self.rows
        self.page = 0
        self.sel = 0
    def pages(self): 
        return (len(self.entries)+self.per-1)//self.per
    def current_items(self):
        s=self.page*self.per
        return self.entries[s:s+self.per]
    def draw(self, ctx):
        cls(ctx);
        items = self.current_items()
        # grid centrado
        gridw = self.cols*self.tilew + (self.cols-1)*self.gx
        gridh = self.rows*self.tileh + (self.rows-1)*self.gy
        base_x = (ctx.W - gridw)//2
        base_y = (ctx.H - gridh)//2
        # pintar celdas
        for i, ent in enumerate(items):
            r=i//self.cols; c=i%self.cols
            x=base_x + c*(self.tilew+self.gx)
            y=base_y + r*(self.tileh+self.gy)
            rect_frame(ctx, x,y,self.tilew,self.tileh,1)
            # icono (vector simple por defecto)
            if hasattr(ent["app"], "draw_icon"):
                ent["app"].draw_icon(ctx, x, y, self.tilew-2, self.tileh-12)
            # etiqueta
            label = ent["name"][:8]
            use_font(ctx,"6"); 
            ctx.d.text(label, x+(self.tilew-len(label)*6)//2, y+self.tileh-8, ctx.W, 1)
            #
            # invert pixels on the label text
            #
            if i == self.sel:
                ctx.d.set_pen(ctx.INK); ctx.d.rectangle(x, y+self.tileh-8, self.tilew, 10)
                ctx.d.set_pen(ctx.BG); ctx.d.text(label, x+(self.tilew-len(label)*6)//2, y+self.tileh-7, ctx.W, 1)
                ctx.d.set_pen(ctx.INK)
        # paginador
        #ptxt = "Pag {}/{}".format(self.page+1, self.pages())
        #use_font(ctx,"6"); ctx.d.text(ptxt, ctx.W-len(ptxt)*6-2, 1, ctx.W, 1); use_font(ctx,"8")
    def handle_key(self, ctx, k):
        per=self.per
        # CardKB arrow keys: 0xB4=Left, 0xB5=Up, 0xB6=Down, 0xB7=Right
        arrow_key = None
        if k == 0xB5:    # Up arrow
            arrow_key = 'UP'
        elif k == 0xB6:  # Down arrow
            arrow_key = 'DOWN'
        elif k == 0xB7:  # Right arrow
            arrow_key = 'RIGHT'
        elif k == 0xB4:  # Left arrow
            arrow_key = 'LEFT'
        elif k == 27:    # ESC to quit
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
        # paginar
        elif k in (ord('.'), ord('L')) and self.page < self.pages()-1: self.page+=1; self.sel=0
        elif k in (ord(','), ord('H')) and self.page>0: self.page-=1; self.sel=0
        elif k==13:  # Enter
            idx = self.page*self.per + self.sel
            if idx < len(self.entries):
                return ("push", self.entries[idx]["app"])
        return None

# ---------- apps: Reloj ----------
def two(n): return "{:02d}".format(n)
class ClockApp(App):
    title="Reloj"; tick_ms=200
    def draw_icon(self, ctx, x,y,w,h):
        r=min(w,h)//3+2; cx=x+w//2; cy=y+h//2
        draw_ring(ctx,cx,cy,r,2)
        ctx.d.line(cx, cy, cx, cy-r+6)
        ctx.d.line(cx, cy, cx+r-8, cy)
    def fmt(self, ctx, tm):
        if ctx.settings.get("clock_24h", True):
            return "{}:{}:{}".format(two(tm[3]),two(tm[4]),two(tm[5]))
        h=tm[3]; suf="AM" if h<12 else "PM"; h=h%12 or 12
        return "{}:{}:{} {}".format(two(h),two(tm[4]),two(tm[5]),suf)
    def draw(self, ctx):
        tm=time.localtime()
        cls(ctx); header(ctx, "Reloj")
        ctx.d.text(self.fmt(ctx, tm), 2, 16, ctx.W, 1)
        ctx.d.text("{:04d}-{:02d}-{:02d}".format(tm[0],tm[1],tm[2]), 2, 24, ctx.W, 1)
        draw_ring(ctx, 96, 36, 27, 2)
        # agujas
        h,m,s = tm[3],tm[4],tm[5]
        def endpoint(r, ang_deg):
            rad=math.radians(ang_deg-90); cx,cy=96,36
            return int(cx+math.cos(rad)*r), int(cy+math.sin(rad)*r)
        ha=(h%12 + m/60)*30; ma=m*6+s/10; sa=s*6
        x,y=endpoint(14,ha); ctx.d.line(96,36,x,y)
        x,y=endpoint(20,ma); ctx.d.line(96,36,x,y)
        x,y=endpoint(23,sa); ctx.d.line(96,36,x,y)
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"

# ---------- apps: Ajustes (solo tema/brillo demo) ----------
class SettingsApp(App):
    title="Config"; tick_ms=300
    def __init__(self):
        self.idx=0
        self.items=["Tema", "Brillo W", "Volver"]
        self.themes=list(THEMES.keys())
        self.tidx=0
    def draw_icon(self, ctx, x,y,w,h):
        r=min(w,h)//4; cx=x+w//2; cy=y+h//2
        draw_ring(ctx,cx,cy,r+4,2)
        draw_ring(ctx,cx,cy,r-2,2)
    def draw(self, ctx):
        cls(ctx); header(ctx,"Config")
        for i, it in enumerate(self.items):
            mark = ">" if i==self.idx else " "
            ctx.d.text("{} {}".format(mark,it), 2, 12+i*8, ctx.W, 1)
        t = ctx.settings.get("theme","amber")
        ctx.d.text("Tema: {}".format(t), 2, ctx.H-16, ctx.W, 1)
        ctx.d.text("W={}".format(ctx.settings.get("w_brightness",64)), 80, ctx.H-16, ctx.W, 1)
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        if k==ord('j') and self.idx< len(self.items)-1: self.idx+=1
        elif k==ord('k') and self.idx>0: self.idx-=1
        elif k==13:
            if self.idx==0: return ("push", ThemeChooserApp())
            if self.idx==1: return ("push", WBrightnessApp())
            if self.idx==2: return "pop"

class ThemeChooserApp(App):
    title="Tema"; tick_ms=200
    def __init__(self):
        self.names=list(THEMES.keys()); self.idx=0
    def draw(self, ctx):
        cls(ctx); header(ctx,"Tema")
        for i,n in enumerate(self.names):
            mark=">" if i==self.idx else " "
            ctx.d.text("{} {}".format(mark,n), 2, 12+i*8, ctx.W, 1)
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        if k==ord('j') and self.idx< len(self.names)-1: self.idx+=1
        elif k==ord('k') and self.idx>0: self.idx-=1
        elif k==13:
            ctx.settings["theme"]=self.names[self.idx]
            ctx.ds.update_settings({"theme":ctx.settings["theme"]})
            ctx.theme.apply()
            return "pop"

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

class ContactsApp(App):
    title="TEL"; tick_ms=200
    def draw_icon(self, ctx, x,y,w,h):
        r=min(w,h)//4; cx=x+w//2; cy=y+h//2
        draw_ring(ctx,cx,cy,r+4,2)
        draw_ring(ctx,cx,cy,r-2,2)
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

class MemosApp(App):
    title="Memos"; tick_ms=200
    def draw_icon(self, ctx, x,y,w,h):
        r=min(w,h)//4; cx=x+w//2; cy=y+h//2
        draw_ring(ctx,cx,cy,r+4,2)
        draw_ring(ctx,cx,cy,r-2,2)
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

# ---------- apps: Calendar ----------
class CalendarApp(App):
    title="Cal"; tick_ms=200
    def __init__(self):
        tm = time.localtime()
        self.y, self.m = tm[0], tm[1]
    def draw_icon(self, ctx, x,y,w,h):
        rect_frame(ctx, x+4, y+4, w-8, h-10, 1)
        ctx.d.line(x+8, y+4, x+8, y+1)
        ctx.d.line(x+w-8, y+4, x+w-8, y+1)
        gy = y+ h//2
        ctx.d.line(x+6, gy, x+w-6, gy)
    def draw(self, ctx):
        # calculate first day of month
        first_w = self.weekday(self.y, self.m, 1)
        dim = self.days_in_month(self.y, self.m)
        cls(ctx); header(ctx, "Calendario")
        
        use_font(ctx, "6")
        month_year = "{} {}".format(self.month_name(self.m), self.y)
        month_x = (ctx.W - len(month_year) * 6) // 2
        ctx.d.text(month_year, month_x, 12, ctx.W, 1)
        
        # Draw each weekday header at fixed positions
        weekdays = ["M", "T", "W", "T", "F", "S", "S"]
        cell_width = 18  # pixels per day column
        start_x = (ctx.W - 7 * cell_width) // 2
        header_y = 20
        
        for i, wd in enumerate(weekdays):
            x = start_x + i * cell_width
            ctx.d.text(wd, x, header_y, ctx.W, 1)
        
        # Get today's date for highlighting
        tm_now = time.localtime()
        today_year, today_month, today_day = tm_now[0], tm_now[1], tm_now[2]
        is_current_month = (self.y == today_year and self.m == today_month)
        
        # Draw each day at fixed tile positions
        day = 1
        day_start_y = 28
        row_height = 7
        
        for week in range(6):
            for dow in range(7):
                if week == 0 and dow < first_w:
                    continue  # skip days before month starts
                if day > dim:
                    break  # month ended
                
                x = start_x + dow * cell_width
                y = day_start_y + week * row_height
                
                # Highlight today's date
                if is_current_month and day == today_day:
                    ctx.d.set_pen(ctx.INK)
                    ctx.d.rectangle(x, y, 12, 7)  # filled rectangle behind day
                    ctx.d.set_pen(ctx.BG)
                    ctx.d.text("{:2d}".format(day), x, y, ctx.W, 1)
                    ctx.d.set_pen(ctx.INK)
                else:
                    ctx.d.text("{:2d}".format(day), x, y, ctx.W, 1)
                
                day += 1
            if day > dim:
                break
        
        use_font(ctx, "8")
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        # Arrow keys
        if k == 0xB4:  # Left - previous month
            self.m -= 1
            if self.m == 0: self.m = 12; self.y -= 1
        elif k == 0xB7:  # Right - next month
            self.m += 1
            if self.m == 13: self.m = 1; self.y += 1
        elif k == 0xB5:  # Up - previous year
            self.y -= 1
        elif k == 0xB6:  # Down - next year
            self.y += 1
        elif k == ord('t'):  # Today
            tm = time.localtime(); self.y, self.m = tm[0], tm[1]
    def weekday(self, y, m, d):
        t = [0,3,2,5,0,3,5,1,4,6,2,4]
        if m < 3: y -= 1
        w = (y + y//4 - y//100 + y//400 + t[m-1] + d) % 7
        return (w - 1) % 7
    def is_leap(self, y):
        return (y%4==0 and y%100!=0) or (y%400==0)
    def days_in_month(self, y, m):
        if m==2: return 29 if self.is_leap(y) else 28
        return 31 if m in (1,3,5,7,8,10,12) else 30
    def month_name(self, m):
        return ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"][m-1]

# ---------- apps: Calculator ----------
class CalculatorApp(App):
    title="Calc"; tick_ms=100
    def __init__(self):
        self.expr = ""
        self.result = ""
        self.allowed = set("0123456789+-*/(). ")
    def draw_icon(self, ctx, x,y,w,h):
        rect_frame(ctx, x+6, y+3, w-12, h-10, 1)
        rect_frame(ctx, x+8, y+5, w-16, 6, 1)
        bx = [x+10, x+ w//2 - 2, x+w-14]
        by = [y+14, y+19]
        for yy in by:
            for xx in bx:
                ctx.d.rectangle(xx, yy, 3, 3)
    def draw(self, ctx):
        cls(ctx); header(ctx, "Calc")
        use_font(ctx,"6")
        ctx.d.text("Expr:", 2, 12, ctx.W, 1)
        ctx.d.text(self.expr[-20:], 2, 18, ctx.W, 1)
        ctx.d.text("Res: {}".format(self.result[:20]), 2, 28, ctx.W, 1)
        use_font(ctx,"8")
        ctx.d.text("Enter=eval c=clear q=salir", 2, ctx.H-8, ctx.W, 1)
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
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

# ---------- apps: Snake ----------
class SnakeApp(App):
    title="Snake"; tick_ms=5
    def __init__(self):
        try:
            import urandom as random
            self.random = random
        except:
            import random
            self.random = random
        self.cell = 4
        self.cols = 128 // self.cell
        self.rows = (64 - 8) // self.cell
        self.offy = 8
        self.reset_game()
    def reset_game(self):
        self.score = 0
        self.snake = [(self.cols//2, self.rows//2)]
        self.direction = (1,0)
        self.food = self.place_food()
        self.alive = True
        self.speed_ms = 120
        self.last = time.ticks_ms()
    def draw_icon(self, ctx, x,y,w,h):
        px = x+6; py = y+6
        step = (w-12)//3
        for i in range(1,6):
            nx = x+6 + (i%3)*step if (i//3)%2==0 else x+w-6 - (i%3)*step
            ny = py + (i//3)*((h-12)//2)
            ctx.d.line(px, py, nx, ny); px, py = nx, ny
        ctx.d.rectangle(px-1, py-1, 3, 3)
    def place_food(self):
        while True:
            fx = self.randrange(0, self.cols)
            fy = self.randrange(0, self.rows)
            if (fx,fy) not in self.snake:
                return (fx,fy)
    def randrange(self, a, b):
        try:
            return self.random.randrange(a, b)
        except:
            return a + (self.random.getrandbits(8) % (b - a))
    def draw_cell(self, ctx, x, y):
        ctx.d.rectangle(x*self.cell, self.offy + y*self.cell, self.cell, self.cell)
    def draw(self, ctx):
        cls(ctx); header(ctx, "Snake")
        ctx.d.text("Pts: {}".format(self.score), 2, 12, ctx.W, 1)
        ctx.d.rectangle(self.food[0]*self.cell, self.offy + self.food[1]*self.cell, self.cell, self.cell)
        for (x,y) in self.snake:
            self.draw_cell(ctx, x, y)
        if not self.alive:
            ctx.d.text("GAME OVER  r=reinicio", 2, ctx.H-8, ctx.W, 1)
    def handle_key(self, ctx, k):
        if k in (ord('q'),27): return "pop"
        # Arrow keys for snake
        if self.alive:
            if k == 0xB5 and self.direction!=(0,1): self.direction=(0,-1)  # Up
            elif k == 0xB6 and self.direction!=(0,-1): self.direction=(0,1)  # Down
            elif k == 0xB4 and self.direction!=(1,0): self.direction=(-1,0)  # Left
            elif k == 0xB7 and self.direction!=(-1,0): self.direction=(1,0)  # Right
        if not self.alive and k == ord('r'):
            self.reset_game()
            return None
        # Game update logic
        if time.ticks_diff(time.ticks_ms(), self.last) >= self.speed_ms:
            self.last = time.ticks_ms()
            if self.alive:
                hx, hy = self.snake[0]
                nx, ny = hx+self.direction[0], hy+self.direction[1]
                if nx<0 or nx>=self.cols or ny<0 or ny>=self.rows or (nx,ny) in self.snake:
                    self.alive = False
                else:
                    self.snake.insert(0,(nx,ny))
                    if (nx,ny)==self.food:
                        self.score += 1
                        if self.score%5==0 and self.speed_ms>60:
                            self.speed_ms -= 5
                        self.food = self.place_food()
                    else:
                        self.snake.pop()
        return None

# ---------- apps: Set Time ----------
class SetTimeApp(App):
    title="SetTime"; tick_ms=100
    def __init__(self):
        tm = time.localtime()
        self.year = tm[0]
        self.month = tm[1]
        self.day = tm[2]
        self.hour = tm[3]
        self.minute = tm[4]
        self.second = 0
        self.field = 0  # 0=year, 1=month, 2=day, 3=hour, 4=minute, 5=second
        self.fields = ["Year", "Month", "Day", "Hour", "Min", "Sec"]
    def draw_icon(self, ctx, x,y,w,h):
        rect_frame(ctx, x+6, y+4, w-12, h-10, 1)
        cx = x + w//2; cy = y + h//2
        ctx.d.text("T", cx-3, cy-3, ctx.W, 1)
    def draw(self, ctx):
        cls(ctx); header(ctx, "Set Date/Time")
        use_font(ctx, "6")
        
        # Show current values
        ctx.d.text("{:04d}-{:02d}-{:02d}".format(self.year, self.month, self.day), 10, 14, ctx.W, 1)
        ctx.d.text("{:02d}:{:02d}:{:02d}".format(self.hour, self.minute, self.second), 10, 22, ctx.W, 1)
        
        use_font(ctx, "8")
        # Show which field is selected
        ctx.d.text("Edit: {}".format(self.fields[self.field]), 2, 34, ctx.W, 1)
        vals = [self.year, self.month, self.day, self.hour, self.minute, self.second]
        ctx.d.text("Value: {}".format(vals[self.field]), 2, 42, ctx.W, 1)
        
        ctx.d.text("Up/Dn=val L/R=field", 2, 52, ctx.W, 1)
        ctx.d.text("Enter=save q=cancel", 2, 60, ctx.W, 1)
    def handle_key(self, ctx, k):
        if k == ord('q') or k == 27:
            return "pop"
        # Arrow keys
        if k == 0xB7:  # Right - next field
            self.field = (self.field + 1) % 6
        elif k == 0xB4:  # Left - previous field
            self.field = (self.field - 1) % 6
        elif k == 0xB5:  # Up - increment
            if self.field == 0: self.year = min(2099, self.year + 1)
            elif self.field == 1: self.month = (self.month % 12) + 1
            elif self.field == 2: self.day = min(31, self.day + 1)
            elif self.field == 3: self.hour = (self.hour + 1) % 24
            elif self.field == 4: self.minute = (self.minute + 1) % 60
            elif self.field == 5: self.second = (self.second + 1) % 60
        elif k == 0xB6:  # Down - decrement
            if self.field == 0: self.year = max(2020, self.year - 1)
            elif self.field == 1: self.month = ((self.month - 2) % 12) + 1
            elif self.field == 2: self.day = max(1, self.day - 1)
            elif self.field == 3: self.hour = (self.hour - 1) % 24
            elif self.field == 4: self.minute = (self.minute - 1) % 60
            elif self.field == 5: self.second = (self.second - 1) % 60
        elif k == 13:  # Enter - save
            # Set the RTC
            # RTC datetime format: (year, month, day, weekday, hour, minute, second, subseconds)
            # We'll calculate weekday
            wday = self.calc_weekday(self.year, self.month, self.day)
            ctx.rtc.datetime((self.year, self.month, self.day, wday, self.hour, self.minute, self.second, 0))
            return "pop"
        return None
    def calc_weekday(self, y, m, d):
        # Zeller's congruence for weekday (0=Mon, 6=Sun)
        if m < 3:
            m += 12
            y -= 1
        q = d
        k = y % 100
        j = y // 100
        h = (q + ((13 * (m + 1)) // 5) + k + (k // 4) + (j // 4) - (2 * j)) % 7
        # Convert to Monday=0 format
        return (h + 5) % 7

# ---------- Arranque ----------
def make_menu(ctx):
    entries = [
        {"name":"Clock",  "app": ClockApp()},
        {"name":"Config", "app": SettingsApp()},
        {"name":"SetTime", "app": SetTimeApp()},
        {"name":"Calc", "app": CalculatorApp()},
        {"name":"Cal", "app": CalendarApp()},
        {"name":"Memos", "app": MemosApp()},
        {"name":"Tel","app": ContactsApp()},
        {"name":"Snake", "app": SnakeApp()},
    ]
    return IconMenu(entries)

def main():
    ctx = Context()
    # opción: preguntar hora en frío
    tm = time.localtime()
    if ctx.settings.get("ask_time_on_boot",True) and tm[0] < 2024:
        # aquí podrías empujar una App de “SetTimeApp” para pedir AAAA-MM-DD y HH:MM:SS
        pass
    manager = AppManager(ctx, make_menu(ctx))
    manager.run()

main()
