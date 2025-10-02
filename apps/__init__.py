# Apps module
from .base import App, AppManager, IconMenu
from .clock import ClockApp
from .settings import SettingsApp
from .calculator import CalculatorApp
from .calendar import CalendarApp
from .contacts import ContactsApp
from .memos import MemosApp
from .games import GamesApp
from .settime import SetTimeApp
from .moonphase import MoonPhaseApp
from .theme_chooser import ThemeChooserApp
from .w_brightness import WBrightnessApp

__all__ = [
    'App', 'AppManager', 'IconMenu',
    'ClockApp', 'SettingsApp', 'CalculatorApp', 'CalendarApp',
    'ContactsApp', 'MemosApp', 'GamesApp', 'SetTimeApp', 'MoonPhaseApp',
    'ThemeChooserApp', 'WBrightnessApp'
]

