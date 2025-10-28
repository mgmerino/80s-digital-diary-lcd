# Core Context and Configuration

from machine import I2C, Pin, RTC
from gfx_pack import GfxPack  # type: ignore
from core.wifi_manager import WiFiManager
from core.ntp_sync import NTPSync

try:
    import ujson as json
except:
    import json


# Theme definitions
THEMES = {
    "amber": dict(r=64, g=32, b=0, w=20),
    "fosforo": dict(r=0, g=64, b=0, w=20),
    "hielo": dict(r=0, g=0, b=64, w=24),
    "blanco": dict(r=0, g=0, b=0, w=64),
    "rojo": dict(r=64, g=0, b=0, w=16),
}


class DataStore:
    def __init__(self, path):
        self.path = path
    
    def load(self):
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except:
            return {"contacts": [], "memos": [], "settings": {}}
    
    def save(self, db):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(db, f)
        try:
            import os
            if self.path in os.listdir():
                os.remove(self.path)
            os.rename(tmp, self.path)
        except:
            pass
    
    def load_settings(self, defaults):
        db = self.load()
        s = db.get("settings", {})
        for k, v in defaults.items():
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


class ThemeManager:
    def __init__(self, gp, settings):
        self.gp = gp
        self.settings = settings
    
    def apply(self):
        t = (THEMES.get(self.settings.get("theme", "amber")) or THEMES["amber"]).copy()
        t["w"] = max(0, min(255, self.settings.get("w_brightness", t["w"])))
        self.gp.set_backlight(t["r"], t["g"], t["b"], t["w"])


class Context:
    def __init__(self):
        self.gp = GfxPack()
        self.d = self.gp.display
        self.W, self.H = self.d.get_bounds()
        self.d.set_font("bitmap8")
        self.INK, self.BG = 15, 0
        self.i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
        self.rtc = RTC()
        self.ds = DataStore("agenda.json")
        self.settings = self.ds.load_settings({
            "theme": "amber",
            "w_brightness": 64,
            "clock_24h": True,
            "ask_time_on_boot": True,
            "local_offset_min": 120,
            "wifi_ssid": "",
            "wifi_password": "",
            "wifi_auto_connect": True,
            "ntp_auto_sync": True
        })
        self.theme = ThemeManager(self.gp, self.settings)
        self.theme.apply()
        
        # Initialize WiFi and NTP for Raspberry Pico 2 W
        self.wifi = WiFiManager(self.settings)
        self.ntp = NTPSync(self.rtc, self.settings)

