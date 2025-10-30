# Timezone Selector App

from apps.base import App
from core.ui import cls, header
from core.timezone_manager import get_timezone_info, TIMEZONE_LIST


class TimezoneSelectorApp(App):
    """App for selecting timezone"""
    
    title = "Timezone"
    tick_ms = 300
    
    def __init__(self):
        self.idx = 0
        self.scroll_offset = 0
        self.max_visible = 20  # Number of timezones visible at once
        
        # Get current timezone from context (will be set in draw)
        self.current_tz_key = None
    
    def draw(self, ctx):
        cls(ctx)
        header(ctx, "Select Timezone")
        
        # Get current timezone
        if self.current_tz_key is None:
            self.current_tz_key = ctx.settings.get("timezone", "CET")
            # Find index of current timezone
            try:
                self.idx = TIMEZONE_LIST.index(self.current_tz_key)
            except ValueError:
                self.idx = 0
        
        # Calculate scroll offset to keep selected item visible
        if self.idx < self.scroll_offset:
            self.scroll_offset = self.idx
        elif self.idx >= self.scroll_offset + self.max_visible:
            self.scroll_offset = self.idx - self.max_visible + 1
        
        # Display timezone list
        y = 12
        for i in range(self.scroll_offset, min(len(TIMEZONE_LIST), self.scroll_offset + self.max_visible)):
            tz_key = TIMEZONE_LIST[i]
            tz_info = get_timezone_info(tz_key)
            
            if tz_info is None:
                continue
            
            # Create display text
            mark = ">" if i == self.idx else " "
            
            # Format timezone info
            offset = tz_info["std_offset"]
            hours = abs(offset) // 60
            minutes = abs(offset) % 60
            sign = "+" if offset >= 0 else "-"
            
            if minutes > 0:
                offset_str = f"{sign}{hours}:{minutes:02d}"
            else:
                offset_str = f"{sign}{hours}"
            
            # Show DST indicator
            dst_indicator = "*" if tz_info["has_dst"] else " "
            
            # Truncate name if too long
            display_name = tz_info["name"][:15]
            
            text = f"{mark}{dst_indicator}{display_name}"
            ctx.d.text(text, 2, y, ctx.W, 1)
            
            # Display relative line on the screen
            display_line = i - self.scroll_offset
            
            # Only break if we've filled the screen
            if display_line >= self.max_visible - 1:
                break
            
            y += 8
        
        # Footer with instructions
        footer_y = ctx.H - 16
        ctx.d.text("j/k:move Enter:sel", 2, footer_y, ctx.W, 1)
        
        # Get current selection info
        current_tz_info = get_timezone_info(TIMEZONE_LIST[self.idx])
        has_dst = current_tz_info["has_dst"] if current_tz_info else False
        ctx.d.text(f"DST:{('Y' if has_dst else 'N')}", 2, footer_y + 8, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'), 27):  # q or ESC
            return "pop"
        
        # Arrow key support
        if k == 0xB6:  # Down
            k = ord('j')
        elif k == 0xB5:  # Up
            k = ord('k')
        
        if k == ord('j') and self.idx < len(TIMEZONE_LIST) - 1:
            self.idx += 1
        elif k == ord('k') and self.idx > 0:
            self.idx -= 1
        elif k == 13:  # Enter
            # Save selected timezone
            selected_tz_key = TIMEZONE_LIST[self.idx]
            selected_tz_info = get_timezone_info(selected_tz_key)
            
            if selected_tz_info:
                # Update settings
                ctx.ds.update_settings({
                    "timezone": selected_tz_key,
                    "local_offset_min": selected_tz_info["std_offset"]  # Update fallback offset
                })
                ctx.settings["timezone"] = selected_tz_key
                ctx.settings["local_offset_min"] = selected_tz_info["std_offset"]
                
                # Update timezone manager
                if hasattr(ctx, 'timezone_mgr'):
                    ctx.timezone_mgr.load_timezone()
                
                print(f"Timezone set to: {selected_tz_info['name']}")
            return "pop"

