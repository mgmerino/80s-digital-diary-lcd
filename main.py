# ===== main.py =====
# Modular entry point

from core import Context
from apps import (
    AppManager, IconMenu,
    ClockApp, SettingsApp, CalculatorApp, CalendarApp,
    ContactsApp, MemosApp, GamesApp, MoonPhaseApp, TodoApp
)
from secrets import secrets

SSID = secrets.get("WIFI_SSID")
PWD  = secrets.get("WIFI_PASSWORD")
if not SSID or not PWD:
    raise ValueError("Missing WIFI_SSID or WIFI_PASSWORD in secrets.py")


def make_menu(ctx):
    entries = [
        {"name": "Clock", "app": ClockApp()},
        {"name": "Cal", "app": CalendarApp()},
        {"name": "Moon", "app": MoonPhaseApp()},
        {"name": "Todos", "app": TodoApp()},
        {"name": "Calc", "app": CalculatorApp()},
        {"name": "Memos", "app": MemosApp()},
        {"name": "Tel", "app": ContactsApp()},
        {"name": "Games", "app": GamesApp()},
        {"name": "Config", "app": SettingsApp()},
    ]
    return IconMenu(entries)

def init_wifi(ctx):
    if ctx.settings.get("wifi_auto_connect", True) and ctx.wifi.is_available() and SSID:
        print("Auto-connecting to WiFi...")
        if ctx.wifi.connect(SSID, PWD):
            print("WiFi connected successfully!")
            
            if ctx.settings.get("ntp_auto_sync", True):
                print("Auto-syncing time from NTP...")
                ctx.ntp.sync_time()
        else:
            print("WiFi auto-connect failed")

def main():
    ctx = Context()
    
    init_wifi(ctx)
    
    manager = AppManager(ctx, make_menu(ctx))
    manager.run()


if __name__ == "__main__":
    main()
