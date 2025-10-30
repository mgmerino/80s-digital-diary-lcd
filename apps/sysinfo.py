# System Info App - Display RAM usage and system information

from apps.base import App
from core.ui import cls, header

try:
    import gc
    GC_AVAILABLE = True
except ImportError:
    GC_AVAILABLE = False

try:
    import os
    OS_AVAILABLE = True
except ImportError:
    OS_AVAILABLE = False


class SystemInfoApp(App):
    """Display system information including RAM usage"""
    
    title = "Sys Info"
    tick_ms = 1000  # Update every second
    
    def __init__(self):
        self.auto_collect = True  # Enable by default to prevent saw-tooth pattern
        # Pre-format strings to reduce allocations
        self._str_buffer = None
    
    def draw_icon(self, ctx, x, y, w, h):
        """Draw a chip/processor icon"""
        icon = [
            0b0000111111110000,
            0b0001000000001000,
            0b1101000000001011,
            0b0101111111101010,
            0b0101000000101010,
            0b0101011110101010,
            0b0101010010101010,
            0b0101011110101010,
            0b0101000000101010,
            0b0101111111101010,
            0b1101000000001011,
            0b0001000000001000,
            0b0000111111110000,
            0b0000000000000000,
            0b0000000000000000,
            0b0000000000000000,
        ]
        start_x = x + (w - 16) // 2
        start_y = y + (h - 16) // 2
        
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def draw(self, ctx):
        # ALWAYS collect at start of draw for accurate readings
        # This prevents the saw-tooth memory pattern
        if GC_AVAILABLE:
            gc.collect()
        
        cls(ctx)
        header(ctx, "System Info")
        
        y = 12
        
        if GC_AVAILABLE:
            # Get memory info (after GC for accurate numbers)
            mem_free = gc.mem_free()
            mem_alloc = gc.mem_alloc()
            mem_total = mem_free + mem_alloc
            
            # Display memory info
            ctx.d.text("=== MEMORY ===", 2, y, ctx.W, 1)
            y += 10
            
            # Total memory
            if mem_total >= 1024:
                total_kb = mem_total / 1024
                ctx.d.text(f"Total: {total_kb:.1f} KB", 2, y, ctx.W, 1)
            else:
                ctx.d.text(f"Total: {mem_total} B", 2, y, ctx.W, 1)
            y += 8
            
            # Used memory
            if mem_alloc >= 1024:
                alloc_kb = mem_alloc / 1024
                ctx.d.text(f"Used:  {alloc_kb:.1f} KB", 2, y, ctx.W, 1)
            else:
                ctx.d.text(f"Used:  {mem_alloc} B", 2, y, ctx.W, 1)
            y += 8
            
            # Free memory
            if mem_free >= 1024:
                free_kb = mem_free / 1024
                ctx.d.text(f"Free:  {free_kb:.1f} KB", 2, y, ctx.W, 1)
            else:
                ctx.d.text(f"Free:  {mem_free} B", 2, y, ctx.W, 1)
            y += 8
            
            # Usage percentage
            usage_pct = (mem_alloc / mem_total) * 100
            ctx.d.text(f"Usage: {usage_pct:.1f}%", 2, y, ctx.W, 1)
            y += 10
            
            # Memory bar graph
            bar_width = ctx.W - 4
            bar_height = 8
            bar_x = 2
            bar_y = y
            
            # Draw border
            ctx.d.rectangle(bar_x, bar_y, bar_width, bar_height)
            
            # Draw filled portion
            fill_width = int((mem_alloc / mem_total) * (bar_width - 2))
            if fill_width > 0:
                for i in range(fill_width):
                    ctx.d.line(bar_x + 1 + i, bar_y + 1, bar_x + 1 + i, bar_y + bar_height - 2)
            
            y += bar_height + 4
        else:
            ctx.d.text("GC not available", 2, y, ctx.W, 1)
            y += 10
        
        # Storage info (if available)
        if OS_AVAILABLE and hasattr(os, 'statvfs'):
            try:
                ctx.d.text("=== STORAGE ===", 2, y, ctx.W, 1)
                y += 10
                
                stat = os.statvfs('/')
                block_size = stat[0]
                total_blocks = stat[2]
                free_blocks = stat[3]
                
                total_kb = (total_blocks * block_size) / 1024
                free_kb = (free_blocks * block_size) / 1024
                used_kb = total_kb - free_kb
                
                if total_kb >= 1024:
                    ctx.d.text(f"Total: {total_kb/1024:.1f} MB", 2, y, ctx.W, 1)
                else:
                    ctx.d.text(f"Total: {total_kb:.0f} KB", 2, y, ctx.W, 1)
                y += 8
                
                if used_kb >= 1024:
                    ctx.d.text(f"Used:  {used_kb/1024:.1f} MB", 2, y, ctx.W, 1)
                else:
                    ctx.d.text(f"Used:  {used_kb:.0f} KB", 2, y, ctx.W, 1)
                y += 8
                
                if free_kb >= 1024:
                    ctx.d.text(f"Free:  {free_kb/1024:.1f} MB", 2, y, ctx.W, 1)
                else:
                    ctx.d.text(f"Free:  {free_kb:.0f} KB", 2, y, ctx.W, 1)
                y += 8
            except:
                pass  # Storage info not available
        
        # Footer
        footer_y = ctx.H - 16
        ctx.d.text("g:GC q:back", 2, footer_y, ctx.W, 1)
        ctx.d.text("GC runs on draw", 2, footer_y + 8, ctx.W, 1)
    
    def handle_key(self, ctx, k):
        if k in (ord('q'), 27):  # q or ESC
            return "pop"
        
        if k == ord('g'):
            # Manual garbage collection (already runs on draw, but allow manual trigger)
            if GC_AVAILABLE:
                before = gc.mem_free()
                gc.collect()
                after = gc.mem_free()
                freed = after - before
                print(f"GC: freed {freed} bytes ({freed/1024:.2f} KB)")

