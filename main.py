# ===== main.py =====
# Modular entry point

import time
from core import Context
from apps import (
    AppManager, IconMenu,
    ClockApp, SettingsApp, CalculatorApp, CalendarApp,
    ContactsApp, MemosApp, GamesApp
)


def make_menu(ctx):
    entries = [
        {"name": "Clock", "app": ClockApp()},
        {"name": "Calc", "app": CalculatorApp()},
        {"name": "Cal", "app": CalendarApp()},
        {"name": "Memos", "app": MemosApp()},
        {"name": "Tel", "app": ContactsApp()},
        {"name": "Games", "app": GamesApp()},
        {"name": "Config", "app": SettingsApp()},
    ]
    return IconMenu(entries)


def main():
    ctx = Context()
    # opción: preguntar hora en frío
    tm = time.localtime()
    if ctx.settings.get("ask_time_on_boot", True) and tm[0] < 2024:
        # aquí podrías empujar una App de "SetTimeApp" para pedir AAAA-MM-DD y HH:MM:SS
        pass
    manager = AppManager(ctx, make_menu(ctx))
    manager.run()


if __name__ == "__main__":
    main()

