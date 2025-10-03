# Memos App

import time
from apps.base import App
from core.ui import cls, header, use_font
from core.input import read_key


class MemosApp(App):
    title = "Memos"
    tick_ms = 200
    
    def __init__(self):
        self.mode = 'list'  # 'list', 'view', 'edit', 'new'
        self.selected_index = 0
        self.selected_memo = None
        self.edit_buffer = []
        self.scroll_offset = 0
        
        # Memo bullet icon (16x16)
        self.memo_bullet = [
            0b0000000000000000,
            0b0000101010100000,
            0b0011111111111100,
            0b0010101010101100,
            0b0010000000001100,
            0b0010000000001100,
            0b0010000000001100,
            0b0010111111001100,
            0b0010000000001100,
            0b0010111100001100,
            0b0010000000001100,
            0b0010111111101100,
            0b0010000000001100,
            0b0010000000001100,
            0b0011111111111000,
            0b0000000000000000,
        ]
    
    def draw_icon(self, ctx, x, y, w, h):
        icon = [
            0b0000001100000000,
            0b0000010010000000,
            0b0000100001000000,
            0b0001001000100000,
            0b0010010100010000,
            0b0100001000001000,
            0b1000010011000100,
            0b1000101100100010,
            0b0100001010010001,
            0b0010111111111010,
            0b0001001011001111,
            0b0000100100001111,
            0b0000010011111111,
            0b0000001000101111,
            0b0000000101000000,
            0b0000000010000000,
        ]
        start_x = x + (w - 16) // 2
        start_y = y + (h - 12) // 2
        
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def get_sorted_memos(self, ctx):
        """Get memos sorted by creation date (newest first)"""
        memos = ctx.ds.load_memos()
        
        # Migrate old format to new format
        migrated = []
        for m in memos:
            # Handle old formats
            if isinstance(m, str):
                # Old format: just a string
                migrated.append({
                    'text': m,
                    'timestamp': 0  # Unknown date
                })
            elif isinstance(m, dict):
                if 'text' not in m and 'title' in m:
                    # Old format: title + text
                    migrated.append({
                        'text': m.get('title', '') + ': ' + m.get('text', ''),
                        'timestamp': 0
                    })
                elif 'timestamp' not in m:
                    # Old format: dict without timestamp
                    migrated.append({
                        'text': m.get('text', str(m)),
                        'timestamp': 0
                    })
                else:
                    # New format: already has timestamp
                    migrated.append(m)
            else:
                # Unknown format, convert to string
                migrated.append({
                    'text': str(m),
                    'timestamp': 0
                })
        
        # Sort by timestamp, newest first (0 timestamp goes to end)
        migrated.sort(key=lambda m: m.get('timestamp', 0) if m.get('timestamp', 0) != 0 else -float('inf'), reverse=True)
        
        return migrated
    
    def format_date(self, timestamp):
        """Format timestamp to readable date"""
        if not timestamp:
            return "Unknown"
        t = time.localtime(timestamp)
        return "{:02d}/{:02d}/{} {:02d}:{:02d}".format(
            t[2], t[1], t[0], t[3], t[4]
        )
    
    def draw_memo_bullet(self, ctx, x, y):
        """Draw the memo bullet icon at given position"""
        for row, bits in enumerate(self.memo_bullet):
            for col in range(16):
                if bits & (1 << (15 - col)):
                    ctx.d.pixel(x + col, y + row)
    
    def draw_list(self, ctx):
        """Draw memos list view"""
        cls(ctx)
        # No header to save space
        
        memos = self.get_sorted_memos(ctx)
        
        use_font(ctx, "6")
        if not memos:
            ctx.d.text("No memos yet", 2, 8, ctx.W, 1)
            ctx.d.text("Press 'n' to create one", 2, 16, ctx.W, 1)
        else:
            # Ensure valid selection
            if self.selected_index >= len(memos):
                self.selected_index = max(0, len(memos) - 1)
            
            # Display memos (3 visible at a time)
            # Limit rendering area to prevent overlap with help text
            max_visible = 3
            start_idx = max(0, self.selected_index - 1)
            visible_memos = memos[start_idx:start_idx + max_visible]
            
            y = 2
            max_y = 55  # Limit rendering to leave space for help text
            
            for i, memo in enumerate(visible_memos):
                actual_idx = start_idx + i
                
                # Stop rendering if we would exceed the safe area
                if y + 14 > max_y:
                    break
                
                text = memo.get('text', '')
                date = self.format_date(memo.get('timestamp', 0))
                
                # Preview: first 16 chars (reduced to make room for icon)
                preview = text[:16] + "..." if len(text) > 16 else text
                
                # Highlight selected
                if actual_idx == self.selected_index:
                    ctx.d.set_pen(ctx.INK)
                    ctx.d.rectangle(0, y - 1, ctx.W, 15)
                    ctx.d.set_pen(ctx.BG)
                    # Draw bullet icon (inverted colors for selected)
                    self.draw_memo_bullet(ctx, 2, y - 1)
                    ctx.d.text(preview, 20, y, ctx.W, 1)
                    ctx.d.text(date, 20, y + 7, ctx.W, 1)
                    ctx.d.set_pen(ctx.INK)
                else:
                    # Draw bullet icon
                    self.draw_memo_bullet(ctx, 2, y - 1)
                    ctx.d.text(preview, 20, y, ctx.W, 1)
                    ctx.d.text(date, 20, y + 7, ctx.W, 1)
                
                y += 16
        
        # Help text - positioned safely at bottom
        use_font(ctx, "6")
        ctx.d.text("n=new  Enter=view  q=quit", 2, 57, ctx.W, 1)
    
    def draw_view(self, ctx):
        """Draw memo view mode"""
        if not self.selected_memo:
            return
        
        cls(ctx)
        header(ctx, "View Memo")
        
        text = self.selected_memo.get('text', '')
        date = self.format_date(self.selected_memo.get('timestamp', 0))
        
        use_font(ctx, "6")
        # Show date
        ctx.d.text(date, 2, 12, ctx.W, 1)
        
        # Show text with scrolling
        y = 20
        line_height = 7
        chars_per_line = 20
        max_lines = 4
        
        # Word wrap text
        words = text.split(' ')
        lines = []
        current_line = ''
        
        for word in words:
            if len(current_line) + len(word) + 1 <= chars_per_line:
                current_line += (' ' if current_line else '') + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Display visible lines with scroll
        visible_lines = lines[self.scroll_offset:self.scroll_offset + max_lines]
        for line in visible_lines:
            ctx.d.text(line, 2, y, ctx.W, 1)
            y += line_height
        
        # Scroll indicator
        if len(lines) > max_lines:
            total_pages = (len(lines) + max_lines - 1) // max_lines
            current_page = (self.scroll_offset // max_lines) + 1
            ctx.d.text("[{}/{}]".format(current_page, total_pages), ctx.W - 30, y + 2, ctx.W, 1)
        
        # Character count
        char_info = "{}/256 chars".format(len(text))
        ctx.d.text(char_info, 2, ctx.H - 14, ctx.W, 1)
        
        # Help
        ctx.d.text("e=edit  d=delete  j/k=scroll", 2, ctx.H - 6, ctx.W, 1)
    
    def draw_edit(self, ctx):
        """Draw memo edit mode"""
        cls(ctx)
        header(ctx, "Edit Memo")
        
        text = "".join(self.edit_buffer)
        
        use_font(ctx, "6")
        
        # Show text with word wrap
        y = 14
        line_height = 7
        chars_per_line = 20
        max_lines = 5
        
        # Word wrap
        words = text.split(' ')
        lines = []
        current_line = ''
        
        for word in words:
            if len(current_line) + len(word) + 1 <= chars_per_line:
                current_line += (' ' if current_line else '') + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        if not lines:
            lines = ['']
        
        # Display visible lines with scroll
        visible_lines = lines[self.scroll_offset:self.scroll_offset + max_lines]
        for line in visible_lines:
            ctx.d.text(line, 2, y, ctx.W, 1)
            y += line_height
        
        # Show cursor on last visible line
        if len(visible_lines) > 0:
            last_line_y = 14 + (len(visible_lines) - 1) * line_height
            cursor_x = 2 + (len(visible_lines[-1]) * 6) % (ctx.W - 4)
            ctx.d.text("_", cursor_x, last_line_y, ctx.W, 1)
        
        # Character count with limit indicator
        char_count = len(text)
        if char_count >= 256:
            ctx.d.set_pen(ctx.INK)
            ctx.d.rectangle(0, ctx.H - 15, ctx.W, 8)
            ctx.d.set_pen(ctx.BG)
        
        char_info = "{}/256 chars".format(char_count)
        ctx.d.text(char_info, 2, ctx.H - 14, ctx.W, 1)
        ctx.d.set_pen(ctx.INK)
        
        # Help
        ctx.d.text("Enter=save  Esc=cancel", 2, ctx.H - 6, ctx.W, 1)
    
    def draw_new(self, ctx):
        """Draw new memo creation mode"""
        cls(ctx)
        header(ctx, "New Memo")
        
        text = "".join(self.edit_buffer)
        
        use_font(ctx, "6")
        ctx.d.text("Type your memo:", 2, 14, ctx.W, 1)
        
        # Show text with word wrap
        y = 24
        line_height = 7
        chars_per_line = 20
        max_lines = 4
        
        # Word wrap
        words = text.split(' ')
        lines = []
        current_line = ''
        
        for word in words:
            if len(current_line) + len(word) + 1 <= chars_per_line:
                current_line += (' ' if current_line else '') + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        if not lines:
            lines = ['']
        
        # Display visible lines
        visible_lines = lines[self.scroll_offset:self.scroll_offset + max_lines]
        for line in visible_lines:
            ctx.d.text(line, 2, y, ctx.W, 1)
            y += line_height
        
        # Show cursor on last visible line
        if len(visible_lines) > 0:
            last_line_y = 24 + (len(visible_lines) - 1) * line_height
            cursor_x = 2 + (len(visible_lines[-1]) * 6) % (ctx.W - 4)
            ctx.d.text("_", cursor_x, last_line_y, ctx.W, 1)
        
        # Character count
        char_count = len(text)
        if char_count >= 256:
            ctx.d.set_pen(ctx.INK)
            ctx.d.rectangle(0, ctx.H - 15, ctx.W, 8)
            ctx.d.set_pen(ctx.BG)
        
        char_info = "{}/256 chars".format(char_count)
        ctx.d.text(char_info, 2, ctx.H - 14, ctx.W, 1)
        ctx.d.set_pen(ctx.INK)
        
        # Help
        ctx.d.text("Enter=save  Esc=cancel", 2, ctx.H - 6, ctx.W, 1)
    
    def draw(self, ctx):
        if self.mode == 'list':
            self.draw_list(ctx)
        elif self.mode == 'view':
            self.draw_view(ctx)
        elif self.mode == 'edit':
            self.draw_edit(ctx)
        elif self.mode == 'new':
            self.draw_new(ctx)
    
    def handle_key(self, ctx, k):
        if self.mode == 'list':
            return self.handle_list_key(ctx, k)
        elif self.mode == 'view':
            return self.handle_view_key(ctx, k)
        elif self.mode == 'edit':
            return self.handle_edit_key(ctx, k)
        elif self.mode == 'new':
            return self.handle_new_key(ctx, k)
    
    def handle_list_key(self, ctx, k):
        """Handle keys in list mode"""
        if k in (ord('q'), 27):
            return "pop"
        
        memos = self.get_sorted_memos(ctx)
        
        # Up/Down: Navigate memos
        if k in (0xB5, ord('k')):  # Up
            if memos:
                self.selected_index = max(0, self.selected_index - 1)
        
        elif k in (0xB6, ord('j')):  # Down
            if memos:
                self.selected_index = min(len(memos) - 1, self.selected_index + 1)
        
        # Enter: View memo
        elif k == 13:
            if memos and self.selected_index < len(memos):
                self.selected_memo = memos[self.selected_index]
                self.mode = 'view'
                self.scroll_offset = 0
        
        # N: New memo
        elif k in (ord('n'), ord('N')):
            self.mode = 'new'
            self.edit_buffer = []
            self.scroll_offset = 0
        
        return None
    
    def handle_view_key(self, ctx, k):
        """Handle keys in view mode"""
        if k in (ord('q'), 27):  # Back to list
            self.mode = 'list'
            self.selected_memo = None
            self.scroll_offset = 0
        
        elif k in (ord('e'), ord('E')) and self.selected_memo:  # Edit
            self.mode = 'edit'
            self.edit_buffer = list(self.selected_memo.get('text', ''))
            self.scroll_offset = 0
        
        elif k in (ord('d'), ord('D')) and self.selected_memo:  # Delete
            memos = ctx.ds.load_memos()
            # Find and remove the memo
            for i, m in enumerate(memos):
                if (m.get('text') == self.selected_memo.get('text') and 
                    m.get('timestamp') == self.selected_memo.get('timestamp')):
                    memos.pop(i)
                    break
            ctx.ds.save_memos(memos)
            self.mode = 'list'
            self.selected_memo = None
            self.scroll_offset = 0
        
        # Scroll
        elif k in (0xB6, ord('j')) and self.selected_memo:  # Down
            text = self.selected_memo.get('text', '')
            chars_per_line = 20
            max_lines = 4
            words = text.split(' ')
            lines = []
            current_line = ''
            for word in words:
                if len(current_line) + len(word) + 1 <= chars_per_line:
                    current_line += (' ' if current_line else '') + word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            max_scroll = max(0, len(lines) - max_lines)
            self.scroll_offset = min(self.scroll_offset + 1, max_scroll)
        
        elif k in (0xB5, ord('k')):  # Up
            self.scroll_offset = max(0, self.scroll_offset - 1)
        
        return None
    
    def handle_edit_key(self, ctx, k):
        """Handle keys in edit mode"""
        if k == 13:  # Enter - save
            new_text = "".join(self.edit_buffer).strip()
            if new_text and self.selected_memo:
                self.selected_memo['text'] = new_text
                # Don't update timestamp on edit, keep original
                
                # Save to storage
                memos = ctx.ds.load_memos()
                for i, m in enumerate(memos):
                    if id(m) == id(self.selected_memo):
                        memos[i] = self.selected_memo
                        break
                ctx.ds.save_memos(memos)
            
            self.mode = 'view'
            self.edit_buffer = []
            self.scroll_offset = 0
        
        elif k == 27:  # Esc - cancel
            self.mode = 'view'
            self.edit_buffer = []
            self.scroll_offset = 0
        
        elif k in (8, 127):  # Backspace
            if self.edit_buffer:
                self.edit_buffer.pop()
                # Auto-scroll up if needed
                text = "".join(self.edit_buffer)
                chars_per_line = 20
                total_lines = (len(text) + chars_per_line - 1) // chars_per_line
                if total_lines < self.scroll_offset + 5:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
        
        else:
            # Add character (limit to 256)
            if len(self.edit_buffer) < 256:
                try:
                    ch = chr(k)
                    if ch:
                        self.edit_buffer.append(ch)
                        # Auto-scroll down if needed
                        text = "".join(self.edit_buffer)
                        chars_per_line = 20
                        max_visible_lines = 5
                        total_lines = (len(text) + chars_per_line - 1) // chars_per_line
                        if total_lines > self.scroll_offset + max_visible_lines:
                            self.scroll_offset += 1
                except:
                    pass
        
        return None
    
    def handle_new_key(self, ctx, k):
        """Handle keys in new memo mode"""
        if k == 13:  # Enter - save
            new_text = "".join(self.edit_buffer).strip()
            if new_text:
                memos = ctx.ds.load_memos()
                memos.append({
                    "text": new_text,
                    "timestamp": time.time()
                })
                ctx.ds.save_memos(memos)
            
            self.mode = 'list'
            self.edit_buffer = []
            self.scroll_offset = 0
            self.selected_index = 0  # Jump to top (newest)
        
        elif k == 27:  # Esc - cancel
            self.mode = 'list'
            self.edit_buffer = []
            self.scroll_offset = 0
        
        elif k in (8, 127):  # Backspace
            if self.edit_buffer:
                self.edit_buffer.pop()
                # Auto-scroll up if needed
                text = "".join(self.edit_buffer)
                chars_per_line = 20
                total_lines = (len(text) + chars_per_line - 1) // chars_per_line
                if total_lines < self.scroll_offset + 4:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
        
        else:
            # Add character (limit to 256)
            if len(self.edit_buffer) < 256:
                try:
                    ch = chr(k)
                    if ch:
                        self.edit_buffer.append(ch)
                        # Auto-scroll down if needed
                        text = "".join(self.edit_buffer)
                        chars_per_line = 20
                        max_visible_lines = 4
                        total_lines = (len(text) + chars_per_line - 1) // chars_per_line
                        if total_lines > self.scroll_offset + max_visible_lines:
                            self.scroll_offset += 1
                except:
                    pass
        
        return None
