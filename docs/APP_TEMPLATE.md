# Modular Structure

## 📁 Structure

```
lcd-gfx/
├── main.py              # Original file (keep as backup)
├── main_new.py          # Modular entry point
├── core/
│   ├── __init__.py      # ✅ Exports Context, UI helpers, Input
│   ├── context.py       # ✅ Context, DataStore, ThemeManager, THEMES
│   ├── ui.py            # ✅ use_font, cls, header, rect_frame, draw_ring
│   └── input.py         # ✅ CardKB functions (read_key)
└── apps/
    ├── __init__.py      # ✅ Exports all apps
    ├── base.py          # ✅ App, AppManager, IconMenu
    ├── clock.py         # ✅ ClockApp
    ├── calculator.py    # ✅ CalculatorApp
    ├── calendar.py      # ✅ CalendarApp
    ├── contacts.py      # ✅ ContactsApp + Utils
    ├── memos.py         # ✅ MemosApp
    ├── games.py         # ✅ GamesApp, SnakeApp, MazeApp
    └── settime.py       # ✅ SetTimeApp
    ├── moonphase.py     # ✅ MoonPhaseApp
    ├── theme_chooser.py # ✅ ThemeChooserApp
    ├── w_brightness.py  # ✅ WBrightnessApp
    ├── todos.py         # ✅ TodoApp
```

## 📝 Template to Create Apps

Each app file must follow this pattern:

```python
# apps/example.py

from apps.base import App
from core.ui import cls, header, use_font
import time

class ExampleApp(App):
    title = "Example"
    tick_ms = 200
    
    def draw_icon(self, ctx, x, y, w, h):
        # Draw 16x16 icon
        pass
    
    def draw(self, ctx):
        cls(ctx)
        header(ctx, self.title)
        # Your drawing code here
    
    def handle_key(self, ctx, k):
        if k in (ord('q'), 27):
            return "pop"
        # Handle other keys
        return None
```

## 🚀 How to Use

1. **Development**: Edit `main_new.py` and the modules in `core/` and `apps/`
2. **Testing**: `python main_new.py` (on your computer) or copy to Pico
3. **Production**: Rename `main_new.py` → `main.py` on the Pico

