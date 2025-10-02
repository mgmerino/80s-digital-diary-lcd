# Moon Phase App

import time
from apps.base import App
from core.ui import cls, header, use_font


class MoonPhaseApp(App):
    title = "Moon"
    tick_ms = 1000  # update every second
    
    def __init__(self):
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
        
        # Custom 32x32 pixel art moon phase icons
        self.new_moon_icon = [
            0b00000000000000000000000000000000,
            0b00000000000000000000000000000000,
            0b00000000001111111111110000000000,
            0b00000000001111111111110000000000,
            0b00000000110000000000001100000000,
            0b00000000110000000000001100000000,
            0b00000011000000000000000011000000,
            0b00000011000100000000000011000000,
            0b00001100000000000000000000110000,
            0b00001100000000000000000000110000,
            0b00110000000000000000000000001100,
            0b00110000000000000000100000001100,
            0b00110000000000000000000000001100,
            0b00110000000000000000000000001100,
            0b00110000000000000000001000001100,
            0b00110000000010000000000000001100,
            0b00110000000000000000000000001100,
            0b00110000000000000000000000001100,
            0b00110000001000000000000000001100,
            0b00110000000000000000000000001100,
            0b00110000000000000010000000001100,
            0b00110000000000000000000000001100,
            0b00001100000000000000000000110000,
            0b00001100000000000000000000110000,
            0b00000011000000000000000011000000,
            0b00000011000000000000000011000000,
            0b00000000110000000000001100000000,
            0b00000000110000000000001100000000,
            0b00000000001111111111110000000000,
            0b00000000001111111111110000000000,
            0b00000000000000000000000000000000,
            0b00000000000000000000000000000000,
        ]
        self.waxing_crescent_icon = [
            0b00000000000000000000000000000000,
            0b00000000000000000000000000000000,
            0b00000000001111111111110000000000,
            0b00000000001111111111110000000000,
            0b00000000111111110000001100000000,
            0b00000000111111110000001100000000,
            0b00000011111100000000000011000000,
            0b00000011111100000000000011000000,
            0b00001111111100000000000000110000,
            0b00001111111100000000000000110000,
            0b00111111110000000000000000001100,
            0b00111111110000000000000000001100,
            0b00111110110000000000000000001100,
            0b00111111110000000000000000001100,
            0b00111111110000000000000000001100,
            0b00111111110000000000000000001100,
            0b00110111110000000000000000001100,
            0b00111111110000000000000000001100,
            0b00111111110000000000000000001100,
            0b00111111110000000000000000001100,
            0b00111110110000000000000000001100,
            0b00111111110000000000000000001100,
            0b00001111111100000000000000110000,
            0b00001111111100000000000000110000,
            0b00000011111100000000000011000000,
            0b00000011111100000000000011000000,
            0b00000000111111110000001100000000,
            0b00000000111111110000001100000000,
            0b00000000001111111111110000000000,
            0b00000000001111111111110000000000,
            0b00000000000000000000000000000000,
            0b00000000000000000000000000000000,
        ]
        
        # Placeholder icons (reuse existing ones until you create them)
        # TODO: Create custom icons for these phases
        self.first_quarter_icon = self.waxing_crescent_icon  # Placeholder
        self.waxing_gibbous_icon = self.waxing_crescent_icon  # Placeholder
        self.full_moon_icon = self.waxing_crescent_icon  # Placeholder
        self.waning_gibbous_icon = self.waxing_crescent_icon  # Placeholder
        self.last_quarter_icon = self.waxing_crescent_icon  # Placeholder
        self.waning_crescent_icon = self.waxing_crescent_icon  # Placeholder
        
        # All 8 moon phase icons in order
        self.moon_icons = [
            self.new_moon_icon,           # 0: New Moon
            self.waxing_crescent_icon,     # 1: Waxing Crescent
            self.first_quarter_icon,       # 2: First Quarter (placeholder)
            self.waxing_gibbous_icon,      # 3: Waxing Gibbous (placeholder)
            self.full_moon_icon,           # 4: Full Moon (placeholder)
            self.waning_gibbous_icon,      # 5: Waning Gibbous (placeholder)
            self.last_quarter_icon,        # 6: Last Quarter (placeholder)
            self.waning_crescent_icon,     # 7: Waning Crescent (placeholder)
        ]
    
    def draw_icon(self, ctx, x, y, w, h):
        icon = [
            0b0000000000000000,
            0b0000011111100000,
            0b0000111100010000,
            0b0001111110001000,
            0b0011111111000100,
            0b0111111111000010,
            0b0111101111100010,
            0b0111111111100010,
            0b0111011011100010,
            0b0111111111100010,
            0b0111101111100010,
            0b0011111111000100,
            0b0011111111001000,
            0b0001111110010000,
            0b0000111111100000,
            0b0000000000000000,
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

