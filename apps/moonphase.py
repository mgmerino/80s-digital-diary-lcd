# Moon Phase App

import time
import math
from apps.base import App
from core.ui import cls, header, use_font


class MoonPhaseApp(App):
    title = "Moon"
    tick_ms = 1000  # update every second
    
    def __init__(self):
        # Moon phase icons as 32x32 binary arrays (4 rows of 32 bits each)
        # Each phase is represented as 32 rows of 32-bit integers
        self.moon_icons = self._create_moon_icons()
        self.phase_names = [
            "New Moon",
            "Waxing Crescent",
            "First Quarter",
            "Waxing Gibbous",
            "Full Moon",
            "Waning Gibbous",
            "Last Quarter",
            "Waning Crescent"
        ]
    
    def _create_moon_icons(self):
        """Create 32x32 moon phase icons in binary format"""
        # Each icon is a list of 32 integers (32 bits each = 32x32 pixels)
        
        # Helper to create circle mask
        def circle_pixels():
            """Generate a 32x32 circle"""
            circle = []
            for y in range(32):
                row = 0
                for x in range(32):
                    # Circle equation: (x-16)^2 + (y-16)^2 <= 15^2
                    dx, dy = x - 15.5, y - 15.5
                    if dx*dx + dy*dy <= 225:  # radius ~15
                        row |= (1 << (31 - x))
                circle.append(row)
            return circle
        
        # Helper to create half-circle (left or right)
        def half_circle(left=True):
            """Generate half of a 32x32 circle"""
            half = []
            for y in range(32):
                row = 0
                for x in range(32):
                    dx, dy = x - 15.5, y - 15.5
                    if dx*dx + dy*dy <= 225:
                        if left and x <= 16:
                            row |= (1 << (31 - x))
                        elif not left and x >= 16:
                            row |= (1 << (31 - x))
                half.append(row)
            return half
        
        # Helper for crescent/gibbous phases
        def phase_shape(phase_ratio):
            """Generate moon shape for given phase (0.0 to 1.0)"""
            shape = []
            for y in range(32):
                row = 0
                for x in range(32):
                    dx, dy = x - 15.5, y - 15.5
                    if dx*dx + dy*dy <= 225:  # in circle
                        # Calculate if pixel should be lit
                        if phase_ratio < 0.5:
                            # Waxing: show right side, curve on left
                            phase_x = 16 - (1 - 2*phase_ratio) * 16
                            if x >= phase_x:
                                row |= (1 << (31 - x))
                        else:
                            # Waning: show left side, curve on right  
                            phase_x = 16 + (2*phase_ratio - 1) * 16
                            if x <= phase_x:
                                row |= (1 << (31 - x))
                shape.append(row)
            return shape
        
        # Create 8 moon phases
        icons = []
        
        # 0: New Moon (empty circle outline)
        new_moon = []
        for y in range(32):
            row = 0
            for x in range(32):
                dx, dy = x - 15.5, y - 15.5
                dist = math.sqrt(dx*dx + dy*dy)
                if 14 <= dist <= 16:  # just the outline
                    row |= (1 << (31 - x))
            new_moon.append(row)
        icons.append(new_moon)
        
        # 1-7: Other phases using phase_shape
        for i in range(1, 8):
            icons.append(phase_shape(i / 8.0))
        
        return icons
    
    def draw_icon(self, ctx, x, y, w, h):
        """Draw 16x16 moon icon for menu"""
        # Simple moon icon for the menu (16x16)
        icon = [
            0b0000011111100000,
            0b0001111111111000,
            0b0011111111111100,
            0b0111111111111110,
            0b0111111111111110,
            0b1111111111111111,
            0b1111111111111111,
            0b1111111111111111,
            0b1111111111111111,
            0b1111111111111111,
            0b1111111111111111,
            0b0111111111111110,
            0b0111111111111110,
            0b0011111111111100,
            0b0001111111111000,
            0b0000011111100000,
        ]
        start_x = x + (w - 16) // 2
        start_y = y + (h - 12) // 2
        
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def calculate_moon_phase(self):
        """Calculate current moon phase (0.0 = new moon, 0.5 = full moon, 1.0 = new moon)"""
        # Known new moon: January 6, 2000, 18:14 UTC (JD 2451550.26)
        # Synodic month = 29.53058770576 days
        
        tm = time.localtime()
        year, month, day = tm[0], tm[1], tm[2]
        hour, minute = tm[3], tm[4]
        
        # Calculate Julian Day Number (simplified)
        if month <= 2:
            year -= 1
            month += 12
        
        A = year // 100
        B = 2 - A + A // 4
        JD = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
        JD += (hour + minute / 60.0) / 24.0
        
        # Days since known new moon
        days_since = JD - 2451550.26
        
        # Synodic month period
        synodic_month = 29.53058770576
        
        # Moon phase (0.0 to 1.0)
        phase = (days_since % synodic_month) / synodic_month
        
        return phase
    
    def get_phase_info(self, phase):
        """Get phase index (0-7) and illumination percentage"""
        # Map phase (0.0-1.0) to 8 phases
        phase_idx = int((phase * 8) + 0.5) % 8
        
        # Calculate illumination percentage
        if phase < 0.5:
            illumination = phase * 2 * 100
        else:
            illumination = (1 - phase) * 2 * 100
        
        return phase_idx, illumination
    
    def draw(self, ctx):
        cls(ctx)
        header(ctx, "Moon Phase")
        
        # Calculate current moon phase
        phase = self.calculate_moon_phase()
        phase_idx, illumination = self.get_phase_info(phase)
        
        # Draw the 32x32 moon icon centered
        moon_icon = self.moon_icons[phase_idx]
        icon_x = (ctx.W - 32) // 2
        icon_y = 16
        
        for row, bits in enumerate(moon_icon):
            for col in range(32):
                if bits & (1 << (31 - col)):
                    ctx.d.pixel(icon_x + col, icon_y + row)
        
        # Display phase name
        use_font(ctx, "8")
        phase_name = self.phase_names[phase_idx]
        text_x = (ctx.W - len(phase_name) * 8) // 2
        ctx.d.text(phase_name, text_x, icon_y + 36, ctx.W, 1)
        
        # Display illumination percentage
        use_font(ctx, "6")
        illum_text = "Illum: {:.0f}%".format(illumination)
        illum_x = (ctx.W - len(illum_text) * 6) // 2
        ctx.d.text(illum_text, illum_x, icon_y + 46, ctx.W, 1)
        
        # Display age of moon in days
        age_days = phase * 29.53
        age_text = "Age: {:.1f} days".format(age_days)
        age_x = (ctx.W - len(age_text) * 6) // 2
        ctx.d.text(age_text, age_x, icon_y + 54, ctx.W, 1)
        
        # Hint
        use_font(ctx, "6")
        ctx.d.text("q=quit", 2, ctx.H - 6, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'), 27):  # q or ESC
            return "pop"
        return None

