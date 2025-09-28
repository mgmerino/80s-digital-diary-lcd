# main.py — Agenda 80s+ con Configuración, Hora y Temas
# Hardware: Raspberry Pi Pico + Pimoroni GFX Pack + M5Stack CardKB (I2C 0x5F)
# Requiere MicroPython de Pimoroni (gfx_pack / PicoGraphics)

from machine import I2C, Pin, RTC
from gfx_pack import GfxPack
import time, math
import os, time
try:
    import ujson as json
except:
    import json
try:
    import urandom as random
except:
    import random

# ---------- CardKB / Entrada ----------
CARDKB_ADDR = 0x5F
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)

def read_key():
    try:
        b = i2c.readfrom(CARDKB_ADDR, 1)
        if not b: return None
        v = b[0]
        return None if v == 0 else v
    except OSError:
        return None

def read_char():
    k = read_key()
    if k is None: return None
    try:
        return bytes([k]).decode()
    except:
        return None

# ---------- Pantalla ----------
gp = GfxPack()
d = gp.display
W, H = d.get_bounds()        # 128 x 64
d.set_font("bitmap8")        # 8x8
INK, BG = 15, 0              # monocromo
# ---------- Mapa -----------
MAP_W, MAP_H = 96, 28        # mapa pequeño
MAP_X = (W - MAP_W) // 2
MAP_Y = 12
ROW_H = 6                     # texto 6x6
LIST_Y = MAP_Y + MAP_H + 2
COLS = 2

# Mapa: 24 franjas (husos) en la parte superior
WORLD_CITIES = [
    {"name":"UTC",        "offset":   0},
    {"name":"Madrid",     "offset":  60},
    {"name":"Londres",    "offset":   0},
    {"name":"New York",   "offset": -300},
    {"name":"Mexico",     "offset": -360},
    {"name":"Sao Paulo",  "offset": -180},
    {"name":"Cairo",      "offset":  120},
    {"name":"Nairobi",    "offset":  180},
    {"name":"Dubai",      "offset":  240},
    {"name":"Kolkata",    "offset":  330}, # +5:30
    {"name":"Bangkok",    "offset":  420},
    {"name":"Beijing",    "offset":  480},
    {"name":"Tokyo",      "offset":  540},
    {"name":"Sydney",     "offset":  600},
    {"name":"Auckland",   "offset":  720},
]


# ---------- Menú principal ----------
# --- Layout del grid ---
TILE_W, TILE_H = 40, 28
GAP_X, GAP_Y = 2, 2
GRID_COLS, GRID_ROWS = 3, 2
GRID_W = GRID_COLS*TILE_W + (GRID_COLS-1)*GAP_X
GRID_H = GRID_ROWS*TILE_H + (GRID_ROWS-1)*GAP_Y
GRID_X = (W - GRID_W)//2
GRID_Y = (H - GRID_H)//2


# ---------- Temas / Backlight ----------
THEMES = {
    "amber":       {"r":64, "g":32, "b":0,  "w":20},
    "fosforo":     {"r":0,  "g":64, "b":0,  "w":20},
    "hielo":       {"r":0,  "g":0,  "b":64, "w":24},
    "blanco":      {"r":0,  "g":0,  "b":0,  "w":64},
    "rojo":        {"r":64, "g":0,  "b":0,  "w":16},
}

# Iconos en bytes
# 16x16 = 2 bytes por fila → 32 bytes
ICON_GEAR_16 = bytes([
    0x3C,0x00,
    0x42,0x00,
    0x99,0x00,
    0xA5,0x00,
    0xA5,0x00,
    0x99,0x00,
    0x42,0x00,
    0x3C,0x00,
    0x3C,0x00,
    0x42,0x00,
    0x99,0x00,
    0xA5,0x00,
    0xA5,0x00,
    0x99,0x00,
    0x42,0x00,
    0x3C,0x00,
])

# --- Definición de entradas del menú ---
MENU_ITEMS = [
    {"name": "Contact", "icon": icon_contacts, "fn": lambda: contacts_app()},
    # En el menú:
    {"name": "Memos",   "icon": icon_memos,    "fn": lambda: memos_app()},
    {"name": "Reloj",   "icon": icon_clock,    "fn": lambda: clock_view()},
    {"name": "Cal",     "icon": icon_calendar, "fn": lambda: calendar_view()},
    {"name": "Calc",    "icon": icon_calc,     "fn": lambda: calculator_app()},
    {"name": "World",   "icon": icon_world,    "fn": lambda: world_clock_view()},
    {"name": "Snake",   "icon": icon_snake,    "fn": lambda: snake_game()},
    {"name":"Config", "icon_bytes":("gear",16,16,ICON_GEAR_16), "fn": lambda: settings_app()}
]

def cls():
    d.set_pen(BG); d.clear(); d.set_pen(INK)

def header(title):
    d.set_pen(INK); d.rectangle(0, 0, W, 10)
    d.set_pen(BG); d.text(title[:16], 2, 1, W, 1)
    d.set_pen(INK)

def text_lines(lines, y0=12):
    y = y0
    for s in lines:
        d.text(s, 0, y, W, 1); y += 8

# ---------- RTC / Tiempo ----------
rtc = RTC()

def weekday(y, m, d):
    # 0=Lunes..6=Domingo
    t = [0,3,2,5,0,3,5,1,4,6,2,4]
    if m < 3: y -= 1
    w = (y + y//4 - y//100 + y//400 + t[m-1] + d) % 7  # 0=Domingo..6=Sab
    return (w - 1) % 7

def is_leap(y):
    return (y%4==0 and y%100!=0) or (y%400==0)

def days_in_month(y, m):
    if m==2: return 29 if is_leap(y) else 28
    return 31 if m in (1,3,5,7,8,10,12) else 30

# ---------- Persistencia (datos + ajustes) ----------
DB_FILE = "agenda.json"
db = {
    "contacts": [],
    "memos": [],
    "settings": {
        "theme": "amber",
        "backlight": {"r":64, "g":32, "b":0, "w":20},
        "local_offset_min": 120,
        "w_brightness": 64,           # valor W base (0..255), usado por temas
        "clock_24h": True,
        "ask_time_on_boot": True
    }
}

def load_db():
    global db
    try:
        with open(DB_FILE, "r") as f:
            loaded = json.load(f)
        # saneo claves
        loaded.setdefault("contacts", [])
        loaded.setdefault("memos", [])
        loaded.setdefault("settings", {})
        s = loaded["settings"]
        s.setdefault("theme", "amber")
        s.setdefault("backlight", {"r":64,"g":32,"b":0,"w":20})
        s.setdefault("w_brightness", 64)
        s.setdefault("clock_24h", True)
        s.setdefault("ask_time_on_boot", True)
        s.setdefault("local_offset_min", 120)
        db = loaded
    except Exception:
        pass

def backup_db_daily():
    try:
        tm = time.localtime()
        stamp = "{:04d}{:02d}{:02d}".format(tm[0], tm[1], tm[2])
        src = "agenda.json"
        dst = "agenda-" + stamp + ".json"
        if src in os.listdir() and dst not in os.listdir():
            # copia sencilla
            with open(src, "r") as f: data = f.read()
            with open(dst, "w") as f: f.write(data)
    except Exception:
        pass


def save_db():
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(db, f)
    try:
        import os
        if DB_FILE in os.listdir():
            os.remove(DB_FILE)
        os.rename(tmp, DB_FILE)
    except:
        pass

# ---------- Temas / Backlight ----------
def apply_backlight():
    s = db["settings"]
    t = s.get("backlight", THEMES["amber"]).copy()
    # Aplica brillo W adicional (no toca R,G,B para mantener tono)
    t["w"] = max(0, min(255, s.get("w_brightness", t.get("w", 32))))
    gp.set_backlight(t["r"], t["g"], t["b"], t["w"])

def choose_theme():
    names = list(THEMES.keys())
    idx = max(0, names.index(db["settings"].get("theme", "amber")) if db["settings"].get("theme") in names else 0)
    while True:
        cls(); header("Tema")
        for i, name in enumerate(names):
            mark = ">" if i==idx else " "
            d.text("{} {}".format(mark, name), 2, 12 + i*8, W, 1)
        d.text("Enter=aplicar  j/k=mov  q=salir", 2, H-8, W, 1)
        d.update()
        k = read_key()
        if k is None: time.sleep_ms(30); continue
        if k in (ord('q'), 27): return
        if k == ord('j') and idx < len(names)-1: idx += 1
        if k == ord('k') and idx > 0: idx -= 1
        if k == 13:  # Enter
            name = names[idx]
            db["settings"]["theme"] = name
            db["settings"]["backlight"] = THEMES[name].copy()
            apply_backlight()
            save_db()

def adjust_brightness_w():
    while True:
        cls(); header("Brillo W")
        val = db["settings"].get("w_brightness", 64)
        d.text("W = {}".format(val), 2, 16, W, 1)
        d.text("h/l = -/+  q=salir", 2, 24, W, 1)
        d.update()
        k = read_key()
        if k is None: time.sleep_ms(30); continue
        if k in (ord('q'), 27): return
        if k == ord('h'): val = max(0, val-8)
        if k == ord('l'): val = min(255, val+8)
        db["settings"]["w_brightness"] = val
        apply_backlight()
        save_db()

def toggle_24h():
    db["settings"]["clock_24h"] = not db["settings"].get("clock_24h", True)
    save_db()

def toggle_ask_on_boot():
    s = db["settings"]
    s["ask_time_on_boot"] = not s.get("ask_time_on_boot", True)
    save_db()

# ---------- Input helpers ----------
def rect_frame(x, y, w, h, th=1):
    # “marco” (borde) usando fill + vaciado interior
    d.rectangle(x, y, w, h)
    d.set_pen(BG); d.rectangle(x+th, y+th, max(0, w-2*th), max(0, h-2*th))
    d.set_pen(INK)

def draw_ring(cx, cy, r, thickness=2):
    d.circle(cx, cy, r)
    inner = r - max(1, thickness)
    if inner > 0:
        d.set_pen(BG); d.circle(cx, cy, inner)
    d.set_pen(INK)

def format_utc_offset(mins):
    sign = '+' if mins >= 0 else '-'
    m = abs(mins)
    return "UTC{}{:02d}:{:02d}".format(sign, m//60, m%60)

def two(n):  # ya lo tienes, por si acaso
    return "{:02d}".format(n)

def prompt_input(label, maxlen=24):
    buf = []
    while True:
        cls(); header(label)
        d.text("".join(buf), 0, 16, W, 1)
        d.update()
        k = read_key()
        if k is None: time.sleep_ms(10); continue
        if k == 13: return "".join(buf)
        if k in (8,127):
            if buf: buf.pop()
            continue
        if k == 27: return None
        try: ch = bytes([k]).decode()
        except: ch = ""
        if ch and len(buf) < maxlen:
            buf.append(ch)

def prompt_yes_no(question, default=None):
    while True:
        cls(); header("Confirmar")
        d.text(question, 2, 16, W, 1)
        d.text("(y/n)", 2, 24, W, 1)
        d.update()
        ch = read_char()
        if ch in ('y','Y'): return True
        if ch in ('n','N'): return False
        if default is not None: return default
        time.sleep_ms(20)
# x,y = esquina sup-izq de la celda; w,h = tamaño de celda
def icon_contacts(x,y,w,h):
    # cabeza + torso
    r = min(w,h)//6
    cx = x + w//2
    cy = y + h//3
    d.circle(cx, cy, r)                  # cabeza (rellena)
    rect_frame(cx - 2*r, cy + r, 4*r, 2*r, 1)  # torso

def icon_memos(x,y,w,h):
    # hoja con “dog-ear” + líneas
    rect_frame(x+6, y+3, w-12, h-10, 1)
    d.line(x+w-12, y+3, x+w-6, y+9)      # esquina doblada
    d.line(x+8, y+h-12, x+w-8, y+h-12)
    d.line(x+8, y+h-8,  x+w-14, y+h-8)

def icon_clock(x,y,w,h):
    r = min(w,h)//3 + 2
    cx = x + w//2; cy = y + h//2 - 2
    draw_ring(cx, cy, r, 2)
    # agujas
    d.line(cx, cy, cx, cy - r + 6)       # min
    d.line(cx, cy, cx + (r-8), cy)       # hora
    # marcas 12/3/6/9
    d.line(cx, cy - r, cx, cy - r + 2)
    d.line(cx + r, cy, cx + r - 2, cy)
    d.line(cx, cy + r, cx, cy + r - 2)
    d.line(cx - r, cy, cx - r + 2, cy)

def icon_calendar(x,y,w,h):
    rect_frame(x+4, y+4, w-8, h-10, 1)
    # anillas
    d.line(x+8, y+4, x+8, y+1)
    d.line(x+w-8, y+4, x+w-8, y+1)
    # cuadricula 3x2
    gx1, gx2 = x+8, x+w-8
    gy = y+ h//2
    d.line(x+6, gy, x+w-6, gy)
    d.line((x+gx1+gx2)//2, y+6, (x+gx1+gx2)//2, y+h-6)

def icon_calc(x,y,w,h):
    rect_frame(x+6, y+3, w-12, h-10, 1)
    # display
    rect_frame(x+8, y+5, w-16, 6, 1)
    # botones 3x3
    bx = [x+10, x+ w//2 - 2, x+w-14]
    by = [y+14, y+19, y+24]
    for yy in by:
        for xx in bx:
            d.rectangle(xx, yy, 3, 3)

def icon_world(x,y,w,h):
    r = min(w,h)//3 + 2
    cx = x + w//2; cy = y + h//2 - 2
    draw_ring(cx, cy, r, 2)
    # meridianos / paralelos
    d.line(cx - r//2, cy - r+2, cx - r//2, cy + r-2)
    d.line(cx + r//2, cy - r+2, cx + r//2, cy + r-2)
    d.line(cx - r + 2, cy, cx + r - 2, cy)

def icon_snake(x,y,w,h):
    # camino en S
    px = x+6; py = y+6
    step = (w-12)//3
    for i in range(1,6):
        nx = x+6 + (i%3)*step if (i//3)%2==0 else x+w-6 - (i%3)*step
        ny = py + (i//3)*((h-12)//2)
        d.line(px, py, nx, ny); px, py = nx, ny
    # cabeza
    d.rectangle(px-1, py-1, 3, 3)

def icon_settings(x,y,w,h):
    # engranaje simplificado
    r = min(w,h)//4
    cx = x + w//2; cy = y + h//2 - 2
    draw_ring(cx, cy, r+4, 2)
    for a in range(0, 360, 60):
        rad = math.radians(a)
        x1 = int(cx + math.cos(rad)*(r+4))
        y1 = int(cy + math.sin(rad)*(r+4))
        x2 = int(cx + math.cos(rad)*(r+8))
        y2 = int(cy + math.sin(rad)*(r+8))
        d.line(x1,y1,x2,y2)
    draw_ring(cx, cy, r-2, 2)

# ---------- Ajuste de hora ----------
def set_rtc_datetime(y, m, d, hh, mm, ss):
    wd = weekday(y,m,d)  # 0=Lun..6=Dom
    rtc.datetime((y, m, d, wd, hh, mm, ss, 0))

def parse_int(s, lo, hi):
    try:
        n = int(s)
        if lo <= n <= hi:
            return n
    except:
        pass
    return None


def adjust_local_offset():
    step = 30  # saltos de 30 min para soportar medias horas (India, etc.)
    while True:
        cls(); header("UTC local")
        cur = db["settings"].get("local_offset_min", 0)
        d.text(format_utc_offset(cur), 2, 16, W, 1)
        d.text("h/l=-/+30m  0=UTC  q=salir", 2, 24, W, 1)
        d.update()
        k = read_key()
        if k is None: time.sleep_ms(20); continue
        if k in (ord('q'), 27): return
        if k == ord('h'): cur -= step
        if k == ord('l'): cur += step
        if k == ord('0'): cur = 0
        # limita a rangos razonables (-12:00 .. +14:00)
        cur = max(-12*60, min(14*60, cur))
        db["settings"]["local_offset_min"] = cur
        save_db()

def set_time_flow():
    # Pide "AAAA-MM-DD" y "HH:MM:SS" y aplica al RTC
    while True:
        date_s = prompt_input("Fecha AAAA-MM-DD", 10)
        if date_s is None: return
        try:
            y_s, m_s, d_s = date_s.strip().split("-")
        except:
            continue
        y = parse_int(y_s, 2000, 2099)
        m = parse_int(m_s, 1, 12)
        if y is None or m is None: continue
        dmax = days_in_month(y, m)
        d = parse_int(d_s, 1, dmax)
        if d is None: continue
        break
    while True:
        time_s = prompt_input("Hora HH:MM:SS", 8)
        if time_s is None: return
        try:
            hh_s, mm_s, ss_s = time_s.strip().split(":")
        except:
            continue
        hh = parse_int(hh_s, 0, 23)
        mm = parse_int(mm_s, 0, 59)
        ss = parse_int(ss_s, 0, 59)
        if None in (hh,mm,ss): continue
        break
    set_rtc_datetime(y, m, d, hh, mm, ss)

# ---------- Listas / CRUD simple ----------
def list_paginated(items, title, fmt_fn, add_fn):
    page, size = 0, 6
    while True:
        cls(); header(title)
        if not items:
            d.text("(vacio) a=añadir, q=salir", 0, 16, W, 1)
        else:
            start = page*size
            chunk = items[start:start+size]
            y = 12
            for i, it in enumerate(chunk, start=1):
                d.text(f"{i+start:02d}. {fmt_fn(it)}", 0, y, W, 1); y += 8
            d.text("j/k=nav  a=añadir  q=salir", 0, H-8, W, 1)
        d.update()
        k = read_key()
        if k is None: time.sleep_ms(20); continue
        if k in (ord('q'),27): return
        if k == ord('a'):
            add_fn(); save_db()
            if items: page = max(0, (len(items)-1)//size)
            continue
        if k == ord('j') and (page+1)*size < len(items): page += 1
        if k == ord('k') and page>0: page -= 1

# ---------- Contactos / Memos ----------
def fmt_contact(c): return f"{c.get('name','')}  {c.get('phone','')}"
def add_contact():
    name = prompt_input("Nombre")
    if not name or not name.strip(): return
    phone = prompt_input("Telefono (opcional)") or ""
    db["contacts"].append({"name": name.strip(), "phone": phone.strip()})
def contacts_app(): return list_paginated(db["contacts"], "Contactos", fmt_contact, add_contact)

def fmt_memo(m): return m
def add_memo():
    memo = prompt_input("Nuevo memo")
    if not memo or not memo.strip(): return
    db["memos"].append(memo.strip())
def memos_app(): return list_paginated(db["memos"], "Memos", fmt_memo, add_memo)

# ---------- Reloj ----------
def two(n): return "{:02d}".format(n)

def draw_ring(cx, cy, r, thickness=2):
    d.set_pen(INK); d.circle(cx, cy, r)
    inner = r - max(1, thickness)
    if inner > 0:
        d.set_pen(BG); d.circle(cx, cy, inner)
    d.set_pen(INK)

def draw_analog(cx, cy, r, tm):
    h, m, s = tm[3], tm[4], tm[5]
    draw_ring(cx, cy, r, thickness=2)
    for i in range(12):
        ang = (i/12.0)*2*math.pi
        x1 = int(cx + math.cos(ang)*(r-3))
        y1 = int(cy + math.sin(ang)*(r-3))
        x2 = int(cx + math.cos(ang)*r)
        y2 = int(cy + math.sin(ang)*r)
        d.line(x1, y1, x2, y2)
    def endpoint(len_factor, angle_deg):
        rad = math.radians(angle_deg - 90.0)
        return int(cx + math.cos(rad)*len_factor), int(cy + math.sin(rad)*len_factor)
    h_angle = (h%12 + m/60.0)*30.0
    m_angle = m*6.0 + s/10.0
    s_angle = s*6.0
    xh, yh = endpoint(r*0.50, h_angle); d.line(cx, cy, xh, yh)
    xm, ym = endpoint(r*0.75, m_angle); d.line(cx, cy, xm, ym)
    xs, ys = endpoint(r*0.85, s_angle); d.line(cx, cy, xs, ys)

def format_time(tm):
    h, m, s = tm[3], tm[4], tm[5]
    if db["settings"].get("clock_24h", True):
        return "{}:{}:{}".format(two(h), two(m), two(s))
    else:
        suf = "AM" if h<12 else "PM"
        h12 = h%12; h12 = 12 if h12==0 else h12
        return "{}:{}:{} {}".format(two(h12), two(m), two(s), suf)

def month_name_es(m):
    return ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][m-1]

def clock_view():
    while True:
        tm = time.localtime()
        cls(); header("Reloj")
        d.text(format_time(tm), 2, 16, W, 1)
        d.text("{:04d}-{:02d}-{:02d}".format(tm[0], tm[1], tm[2]), 2, 24, W, 1)
        draw_analog(96, 36, 27, tm)
        d.text("q=salir", 2, H-8, W, 1)
        d.update()
        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < 200:
            k = read_key()
            if k in (ord('q'),27): return
            time.sleep_ms(5)

# ---------- Calendario ----------
def calendar_view():
    use_font_small()          # 👈 texto 6x6
    tm = time.localtime()
    y, m = tm[0], tm[1]

    while True:
        first_w = weekday(y, m, 1)     # 0=Lun..6=Dom
        dim = days_in_month(y, m)

        cls(); header("Calendario")
        d.text("{} {}".format(month_name_es(m), y), 2, 12, W, 1)
        d.text("Lu Ma Mi Ju Vi Sa Do", 2, 18, W, 1)

        # 6 semanas * 6 px = 36 px, cabe justo sin tapar nada
        day = 1; ypix = 24
        for week in range(6):
            line = ""
            for dow in range(7):
                if week==0 and dow<first_w:
                    line += "   "
                elif day<=dim:
                    line += "{:2d} ".format(day); day += 1
                else:
                    line += "   "
            d.text(line.rstrip(), 2, ypix, W, 1); ypix += 6

        d.update()

        # Teclas (sin dibujar barra inferior)
        while True:
            k = read_key()
            if k is None: time.sleep_ms(20); continue
            if k in (ord('q'),27): 
                use_font_normal(); 
                return
            if k == ord('h'): m -= 1;  m = 12 if m==0 else m;  y -= 1 if m==12 else 0; break
            if k == ord('l'): m += 1;  y += 1 if m==13 else 0; m = 1 if m==13 else m; break
            if k == ord('k'): y -= 1; break
            if k == ord('j'): y += 1; break
            if k == ord('t'): tm = time.localtime(); y, m = tm[0], tm[1]; break

# ---------- Calculadora ----------
ALLOWED = set("0123456789+-*/(). ")
def safe_eval(expr):
    if not all(ch in ALLOWED for ch in expr): raise ValueError("bad char")
    return eval(expr, {"__builtins__": None}, {})
# ---------- Hora mundial (mapa de husos + lista de ciudades) ----------

def minutes_of_day(tm):
    return tm[3]*60 + tm[4]  # hh:mm (ignoramos segundos para la tabla)

def world_time_for_offset(tm_local, local_off_min, city_off_min):
    # Convierte hora local (RTC) a hora de ciudad: (Local -> UTC -> Ciudad)
    m_local = tm_local[3]*60 + tm_local[4]
    m_utc_raw = m_local - local_off_min
    m_city_raw = m_utc_raw + city_off_min
    # delta de día respecto a la fecha local
    day_delta = -1 if m_city_raw < 0 else (1 if m_city_raw >= 1440 else 0)
    m_city = m_city_raw % 1440
    hh, mm = m_city // 60, m_city % 60
    return hh, mm, day_delta

# ----- Fuentes: normal/pequeña -----
def use_font_normal():
    d.set_font("bitmap8")  # 8x8

def use_font_small():
    d.set_font("bitmap6")  # 6x6  ✅ más líneas en 128x64
# ----- PBM ASCII "P1" en pantalla monocromo -----
def draw_pbm(x, y, filename, invert=False, max_w=None, max_h=None):
    # Devuelve (width,height) si OK, None si el fichero no existe/rompe
    try:
        with open(filename, "r") as f:
            data = f.read().split()
    except OSError:
        return None

    if not data or data[0] != "P1":
        return None

    # Saltar comentarios '# ...'
    idx = 1
    while data[idx].startswith("#"):
        idx += 1

    w = int(data[idx]); h = int(data[idx+1]); idx += 2
    # Resto: w*h bits (como '0'/'1') separados por espacios/CR
    # Escalado simple opcional
    sx = sy = 1
    if max_w and w > 0:
        sx = max(1, min(4, max_w // w))
    if max_h and h > 0:
        sy = max(1, min(4, max_h // h))

    # Dibujo
    pos = 0
    for j in range(h):
        for i in range(w):
            if idx + pos >= len(data): break
            bit = int(data[idx + pos])
            pos += 1
            on = (bit == 1)
            if invert: on = not on
            if on:
                # píxel "escalado"
                d.rectangle(x + i*sx, y + j*sy, sx, sy)
    return (w*sx, h*sy)
    
def draw_world_map(local_off_min, cities):
    # Intentar PBM (centra y escala a área MAP_W x MAP_H)
    drawn = draw_pbm(MAP_X, MAP_Y, "world_96x32.pbm", invert=False, max_w=MAP_W, max_h=MAP_H)
    if not drawn:
        # Fallback: franjas de huso
        stripe_w = MAP_W // 24
        for i in range(25):
            x = MAP_X + i*stripe_w
            d.line(x, MAP_Y, x, MAP_Y + MAP_H - 1)

    # Meridiano local (línea de puntos)
    x_local = MAP_X + int((local_off_min + 12*60) * (MAP_W-1) / (24*60))
    for yy in range(MAP_Y, MAP_Y + MAP_H):
        if (yy - MAP_Y) % 2 == 0:
            d.pixel(x_local, yy)

def world_clock_view():
    use_font_small()
    page = 0
    while True:
        tm = time.localtime()
        cls(); header("Hora mundial")
        local_off = db["settings"].get("local_offset_min", 0)

        # Mapa
        draw_world_map(local_off, WORLD_CITIES)
        d.text("Local: {}".format(format_utc_offset(local_off)), 2, MAP_Y + MAP_H + 1, W, 1)

        # Lista en dos columnas
        # Cálculo de filas visibles según espacio
        rows_vis = max(1, (H - LIST_Y - 2) // ROW_H)   # deja 2 px de margen
        page_size = rows_vis * COLS
        start = page * page_size
        chunk = WORLD_CITIES[start:start + page_size]

        for idx, c in enumerate(chunk):
            col = idx // rows_vis
            row = idx % rows_vis
            x = 0 if col == 0 else W//2
            y = LIST_Y + row*ROW_H
            hh, mm, dd = world_time_for_offset(tm, local_off, c["offset"])
            suf = "" if dd==0 else ("-1d" if dd<0 else "+1d")
            label = "{} {:02d}:{:02d} {}".format(c["name"][:9], hh, mm, suf)
            d.text(label.rstrip(), x, y, W//2, 1)

        d.update()

        # Entrada / paginado
        k = read_key()
        if k in (ord('q'), 27):
            use_font_normal()
            return
        if k == ord('h') and page > 0:
            page -= 1
        elif k == ord('l') and (page+1)*page_size < len(WORLD_CITIES):
            page += 1
        time.sleep_ms(20)

def calculator_app():
    expr, result = "", ""
    while True:
        cls(); header("Calculadora")
        d.text("Expr:", 2, 12, W, 1); d.text(expr, 2, 20, W, 1)
        d.text("Res: {}".format(result), 2, 36, W, 1)
        d.text("Enter=eval  c=clear  q=salir", 2, H-8, W, 1)
        d.update()
        k = read_key()
        if k is None: time.sleep_ms(10); continue
        if k in (ord('q'),27): return
        if k in (8,127): expr = expr[:-1] if expr else ""; continue
        if k == ord('c'): expr, result = "", ""; continue
        if k == 13:
            try: result = str(safe_eval(expr.strip())) if expr.strip() else ""
            except: result = "Error"
            continue
        try: ch = bytes([k]).decode()
        except: ch = ""
        if ch in ALLOWED: expr += ch

# ---------- Snake ----------
def randrange(a, b):
    try: return random.randrange(a, b)
    except: return a + (random.getrandbits(8) % (b - a))
def snake_game():
    cell = 4
    cols = W // cell
    rows = (H - 8) // cell
    offy = 8
    def draw_cell(x,y): d.rectangle(x*cell, offy + y*cell, cell, cell)
    def place_food(snake):
        while True:
            fx, fy = randrange(0, cols), randrange(0, rows)
            if (fx,fy) not in snake: return (fx,fy)
    score = 0
    snake = [(cols//2, rows//2)]
    direction = (1,0)
    food = place_food(snake)
    alive = True
    speed_ms = 120
    last = time.ticks_ms()
    while True:
        ch = read_char()
        if ch in ('q','\x1b'): return
        if alive and ch in ('w','a','s','d','W','A','S','D'):
            if ch in ('w','W') and direction!=(0,1): direction=(0,-1)
            if ch in ('s','S') and direction!=(0,-1): direction=(0,1)
            if ch in ('a','A') and direction!=(1,0): direction=(-1,0)
            if ch in ('d','D') and direction!=(-1,0): direction=(1,0)
        if not alive and ch in ('r','R'): return snake_game()
        if time.ticks_diff(time.ticks_ms(), last) >= speed_ms:
            last = time.ticks_ms()
            if alive:
                hx, hy = snake[0]
                nx, ny = hx+direction[0], hy+direction[1]
                if nx<0 or nx>=cols or ny<0 or ny>=rows or (nx,ny) in snake:
                    alive = False
                else:
                    snake.insert(0,(nx,ny))
                    if (nx,ny)==food:
                        score += 1
                        if score%5==0 and speed_ms>60: speed_ms -= 5
                        food = place_food(snake)
                    else:
                        snake.pop()
            cls(); header("Snake  q=salir")
            d.text("Puntos: {}".format(score), 2, 12, W, 1)
            d.rectangle(food[0]*cell, offy + food[1]*cell, cell, cell)
            for (x,y) in snake: draw_cell(x,y)
            if not alive: d.text("GAME OVER  r=reiniciar", 2, H-8, W, 1)
            d.update()
        time.sleep_ms(5)

# ---------- Configuración ----------
def settings_app():
    idx = 0
    items = [
        "Tema (Enter)",
        "Brillo W (Enter)",
        "Formato 24h (toggle)",
        "Ajustar hora ahora",
        "Preguntar hora al iniciar (toggle)",
        "UTC local (Enter)",
        "Volver"
    ]
    while True:
        cls(); header("Config")
        for i, it in enumerate(items):
            mark = ">" if i==idx else " "
            d.text("{} {}".format(mark, it), 2, 12 + i*8, W, 1)
        # estado actual
        d.text("24h: {}".format("SI" if db["settings"].get("clock_24h",True) else "NO"), 2, H-16, W, 1)
        d.text("AskBoot: {}".format("SI" if db["settings"].get("ask_time_on_boot",True) else "NO"), 70, H-16, W, 1)
        d.update()
        k = read_key()
        if k is None: time.sleep_ms(20); continue
        if k in (ord('q'),27): return
        if k == ord('j') and idx < len(items)-1: idx += 1
        if k == ord('k') and idx > 0: idx -= 1
        if k == 13:  # Enter
            if idx == 0: choose_theme()
            elif idx == 1: adjust_brightness_w()
            elif idx == 2: toggle_24h()
            elif idx == 3: set_time_flow()
            elif idx == 4: toggle_ask_on_boot()
            elif idx == 5: adjust_local_offset()
            elif idx == 6: return

def draw_bitmap(x, y, w, h, data, scale=1, invert=False):
    bpr = (w + 7) // 8
    idx = 0
    for row in range(h):
        for col in range(w):
            byte = data[idx + (col >> 3)]
            bit  = 7 - (col & 7)
            on = ((byte >> bit) & 1) ^ (1 if invert else 0)
            if on:
                d.rectangle(x + col*scale, y + row*scale, scale, scale)
        idx += bpr

def draw_bitmap_centered(cell_x, cell_y, cell_w, cell_h, w, h, data, scale=1, invert=False):
    x = cell_x + (cell_w - w*scale)//2
    y = cell_y + (cell_h - h*scale)//2
    draw_bitmap(x, y, w, h, data, scale=scale, invert=invert)

def draw_menu_grid(page, sel_idx):
    use_font_small()
    cls()
    # página y selección relativas a la página
    per_page = GRID_COLS * GRID_ROWS
    start = page*per_page
    items = MENU_ITEMS[start:start+per_page]

    # dibuja tiles
    for i, item in enumerate(items):
        r = i // GRID_COLS
        c = i % GRID_COLS
        x = GRID_X + c*(TILE_W + GAP_X)
        y = GRID_Y + r*(TILE_H + GAP_Y)
        
        # Y en draw_menu_grid(...):
        if "icon_bytes" in item:
            _, iw, ih, data = item["icon_bytes"]
            draw_bitmap_centered(x, y, TILE_W, TILE_H-8, iw, ih, data, scale=1)
        # tile base
        rect_frame(x, y, TILE_W, TILE_H, 1)
        # icono (zona superior, centrado)
        try:
            item["icon"](x, y, TILE_W, TILE_H-8)
        except:
            pass
        # etiqueta (abajo)
        label = item["name"][:8]
        tx = x + (TILE_W - len(label)*6)//2
        d.text(label, tx, y + TILE_H - 7, TILE_W, 1)

        # selección (borde más grueso)
        if i == sel_idx:
            rect_frame(x-1, y-1, TILE_W+2, TILE_H+2, 1)

    # indicador de página
    pages = (len(MENU_ITEMS) + per_page - 1)//per_page
    if pages > 1:
        txt = "Pag {}/{}".format(page+1, pages)
        d.text(txt, W - (len(txt)*6) - 2, 1, W, 1)

    d.update()
    use_font_normal()


def main_menu_icons():
    per_page = GRID_COLS * GRID_ROWS
    pages = (len(MENU_ITEMS) + per_page - 1)//per_page
    page = 0
    sel = 0  # índice relativo dentro de la página (0..per_page-1)

    while True:
        draw_menu_grid(page, sel)
        k = read_key()
        if k is None:
            time.sleep_ms(20); continue

        # salir
        if k in (ord('q'), 27):
            return

        # selección directa por número 1..9
        if ord('1') <= k <= ord('9'):
            idx = k - ord('1')
            if idx < per_page:
                sel = idx
                draw_menu_grid(page, sel)
                time.sleep_ms(50)
                # abrir si existe
                abs_idx = page*per_page + sel
                if abs_idx < len(MENU_ITEMS):
                    MENU_ITEMS[abs_idx]["fn"]()
            continue

        # movimiento estilo vi (h/j/k/l)
        if k == ord('h') and sel % GRID_COLS > 0:
            sel -= 1
        elif k == ord('l') and sel % GRID_COLS < GRID_COLS-1:
            # no sobrepasar último elemento real de la página
            if page*per_page + sel + 1 < len(MENU_ITEMS):
                sel += 1
        elif k == ord('k') and sel - GRID_COLS >= 0:
            sel -= GRID_COLS
        elif k == ord('j') and sel + GRID_COLS < per_page and page*per_page + sel + GRID_COLS < len(MENU_ITEMS):
            sel += GRID_COLS
        # paginado con , .  o H L (mayúsculas)
        elif k in (ord(','), ord('H')) and page > 0:
            page -= 1; sel = 0
        elif k in (ord('.'), ord('L')) and page < pages-1:
            page += 1; sel = 0
        # abrir
        elif k == 13:
            abs_idx = page*per_page + sel
            if abs_idx < len(MENU_ITEMS):
                MENU_ITEMS[abs_idx]["fn"]()
        time.sleep_ms(20)

def main_menu():
    while True:
        cls(); header("Agenda 80s+")
        text_lines([
            "1 Contactos",
            "2 Memos",
            "3 Reloj",
            "4 Calendario",
            "5 Calculadora",
            "6 Hora mundial",
            "7 Snake",
            "8 Configuracion",
            "",
            "q Salir"
        ])
        d.update()
        k = read_key()
        if k is None: time.sleep_ms(20); continue
        if k in (ord('q'),27): return
        if k == ord('1'): contacts_app()
        if k == ord('2'): memos_app()
        if k == ord('3'): clock_view()
        if k == ord('4'): calendar_view()
        if k == ord('5'): calculator_app()
        if k == ord('6'): world_clock_view()
        if k == ord('7'): snake_game()
        if k == ord('8'): settings_app()

# ---------- Arranque ----------
load_db()
apply_backlight()
backup_db_daily()

# Preguntar hora al iniciar si el RTC parece no inicializado
tm = time.localtime()
if db["settings"].get("ask_time_on_boot", True) and tm[0] < 2024:
    if prompt_yes_no("Configurar hora ahora?", default=True):
        set_time_flow()

main_menu()
cls(); d.text("Hasta pronto", 0, 16, W, 1); d.update()
