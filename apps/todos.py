# Todo App

import time
from apps.base import App
from core.ui import cls, header, use_font
from core.input import read_key


class TodoApp(App):
    title = "Todos"
    tick_ms = 200
    
    def __init__(self):
        self.mode = 'list'  # 'list', 'view', 'edit', 'new', 'set_date'
        self.selected_index = 0
        self.selected_todo = None
        self.edit_buffer = []
        self.scroll_offset = 0
        self.date_field = 0  # 0=year, 1=month, 2=day, 3=hour, 4=minute, 5=alarm
        self.date_values = [2024, 1, 1, 12, 0]  # temp values for date entry
        self.alarm_enabled = False  # temp value for alarm setting
        
        # Todo checkbox icons (16x16)
        self.checkbox_empty = [
            0b0000000000000000,
            0b0000000000000000,
            0b0011111111111100,
            0b0010000000000100,
            0b0010000000000100,
            0b0010000000000100,
            0b0010000000000100,
            0b0010000000000100,
            0b0010000000000100,
            0b0010000000000100,
            0b0010000000000100,
            0b0010000000000100,
            0b0010000000000100,
            0b0011111111111100,
            0b0000000000000000,
            0b0000000000000000,
        ]
        
        self.checkbox_checked = [
            0b0000000000000000,
            0b0000000000000000,
            0b0011111111111100,
            0b0010000000000100,
            0b0010000000001100,
            0b0010000000011100,
            0b0010000000111100,
            0b0010100001111100,
            0b0011110011111100,
            0b0011111111110100,
            0b0010111111100100,
            0b0010011111000100,
            0b0010001110000100,
            0b0011111111111100,
            0b0000000000000000,
            0b0000000000000000,
        ]
        
        self.alarm_icon = [
            0b0000000000000000,
            0b0000000110000000,
            0b0000000110000000,
            0b0000001001000000,
            0b0000110000110000,
            0b0000100000010000,
            0b0000100000010000,
            0b0000100000010000,
            0b0000100000010000,
            0b0001100000011000,
            0b0010000000000100,
            0b0001111111111000,
            0b0000000110000000,
            0b0000000110000000,
            0b0000000000000000,
            0b0000000000000000,
        ]
    
    def draw_icon(self, ctx, x, y, w, h):
        """Draw app icon for menu"""
        icon = [
            0b0000000000000000,
            0b0011111000000000,
            0b0011010000000000,
            0b0010110011111110,
            0b0011110000000000,
            0b0000000000000000,
            0b0011111000000000,
            0b0011010000000000,
            0b0010110011111110,
            0b0011110000000000,
            0b0000000000000000,
            0b0011110000000000,
            0b0010010000000000,
            0b0010010011111110,
            0b0011110000000000,
            0b0000000000000000,
        ]
        start_x = x + (w - 16) // 2
        start_y = y + (h - 12) // 2
        
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def draw_checkbox(self, ctx, x, y, checked):
        """Draw checkbox icon"""
        icon = self.checkbox_checked if checked else self.checkbox_empty
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):
                    ctx.d.pixel(x + col, y + row)
    
    def draw_alarm_icon(self, ctx, x, y):
        """Draw alarm icon"""
        for row, bits in enumerate(self.alarm_icon):
            for col in range(16):
                if bits & (1 << (15 - col)):
                    ctx.d.pixel(x + col, y + row)
    
    def get_sorted_todos(self, ctx):
        """Get todos sorted by due date and completion status"""
        todos = ctx.ds.load().get('todos', [])
        
        # Migrate old format if needed
        migrated = []
        for t in todos:
            if isinstance(t, str):
                migrated.append({
                    'text': t,
                    'completed': False,
                    'due_date': None,
                    'alarm': False,
                    'timestamp': 0
                })
            elif isinstance(t, dict):
                if 'completed' not in t:
                    t['completed'] = False
                if 'due_date' not in t:
                    t['due_date'] = None
                if 'alarm' not in t:
                    t['alarm'] = False
                if 'timestamp' not in t:
                    t['timestamp'] = 0
                migrated.append(t)
        
        # Sort: incomplete first, then by due date (soonest first), then by creation
        def sort_key(t):
            if t.get('completed'):
                return (1, float('inf'), 0)  # Completed items at end
            due = t.get('due_date', 0) or 0
            if due == 0:
                return (0, float('inf'), -t.get('timestamp', 0))  # No due date
            return (0, due, -t.get('timestamp', 0))  # Has due date
        
        migrated.sort(key=sort_key)
        return migrated
    
    def save_todos(self, ctx, todos):
        """Save todos to storage"""
        db = ctx.ds.load()
        db['todos'] = todos
        ctx.ds.save(db)
    
    def format_date(self, timestamp):
        """Format timestamp to readable date"""
        if not timestamp:
            return "No due date"
        t = time.localtime(timestamp)
        return "{:02d}/{:02d}/{} {:02d}:{:02d}".format(
            t[2], t[1], t[0], t[3], t[4]
        )
    
    def format_date_short(self, timestamp):
        """Format timestamp to short date (for list view)"""
        if not timestamp:
            return ""
        t = time.localtime(timestamp)
        return "{:02d}/{:02d} {:02d}:{:02d}".format(t[2], t[1], t[3], t[4])
    
    def is_overdue(self, due_date):
        """Check if todo is overdue"""
        if not due_date:
            return False
        return due_date < time.time()
    
    def is_today(self, due_date):
        """Check if todo is due today"""
        if not due_date:
            return False
        now = time.localtime()
        due = time.localtime(due_date)
        return now[0] == due[0] and now[1] == due[1] and now[2] == due[2]
    
    def draw_list(self, ctx):
        """Draw todos list view"""
        cls(ctx)
        # No header to save space
        
        todos = self.get_sorted_todos(ctx)
        
        use_font(ctx, "6")
        if not todos:
            ctx.d.text("No todos yet", 2, 8, ctx.W, 1)
            ctx.d.text("Press 'n' to create one", 2, 16, ctx.W, 1)
        else:
            # Ensure valid selection
            if self.selected_index >= len(todos):
                self.selected_index = max(0, len(todos) - 1)
            
            # Display todos (3 visible to avoid overlap with help text)
            # Maximum rendering area: 55px to leave space for help text
            max_visible = 3
            start_idx = max(0, self.selected_index - 1)
            visible_todos = todos[start_idx:start_idx + max_visible]
            
            y = 2
            max_y = 55  # Limit rendering to this y-coordinate
            
            for i, todo in enumerate(visible_todos):
                actual_idx = start_idx + i
                
                # Stop rendering if we would exceed the safe area
                if y + 14 > max_y:
                    break
                
                text = todo.get('text', '')
                completed = todo.get('completed', False)
                due_date = todo.get('due_date')
                has_alarm = todo.get('alarm', False)
                
                # Preview: adjust length based on alarm
                max_chars = 13 if has_alarm else 16
                preview = text[:max_chars] + "..." if len(text) > max_chars else text
                
                # Highlight selected
                if actual_idx == self.selected_index:
                    ctx.d.set_pen(ctx.INK)
                    ctx.d.rectangle(0, y - 1, ctx.W, 15)
                    ctx.d.set_pen(ctx.BG)
                    self.draw_checkbox(ctx, 2, y - 1, completed)
                    ctx.d.text(preview, 20, y, ctx.W, 1)
                    # Show date/alarm on second line
                    date_str = self.format_date_short(due_date)
                    ctx.d.text(date_str, 20, y + 7, ctx.W, 1)
                    if has_alarm:
                        self.draw_alarm_icon(ctx, ctx.W - 18, y - 1)
                    ctx.d.set_pen(ctx.INK)
                else:
                    self.draw_checkbox(ctx, 2, y - 1, completed)
                    ctx.d.text(preview, 20, y, ctx.W, 1)
                    # Show date/alarm on second line
                    date_str = self.format_date_short(due_date)
                    # Color code by status
                    if not completed and self.is_overdue(due_date):
                        # Overdue - show with emphasis (would be red in color)
                        pass  # In monochrome, just show normally
                    ctx.d.text(date_str, 20, y + 7, ctx.W, 1)
                    if has_alarm:
                        self.draw_alarm_icon(ctx, ctx.W - 18, y - 1)
                
                y += 16
        
        # Help text - positioned safely at bottom
        use_font(ctx, "6")
        ctx.d.text("n=new  Space=check  q=quit", 2, 57, ctx.W, 1)
    
    def draw_view(self, ctx):
        """Draw todo view mode"""
        if not self.selected_todo:
            return
        
        cls(ctx)
        header(ctx, "Todo Detail")
        
        text = self.selected_todo.get('text', '')
        completed = self.selected_todo.get('completed', False)
        due_date = self.selected_todo.get('due_date')
        has_alarm = self.selected_todo.get('alarm', False)
        
        use_font(ctx, "6")
        
        # Status
        status = "[X] Completed" if completed else "[ ] Pending"
        ctx.d.text(status, 2, 12, ctx.W, 1)
        
        # Text with word wrap
        y = 22
        line_height = 7
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
        
        # Display visible lines with scroll
        visible_lines = lines[self.scroll_offset:self.scroll_offset + max_lines]
        for line in visible_lines:
            ctx.d.text(line, 2, y, ctx.W, 1)
            y += line_height
        
        # Due date
        y += 2
        use_font(ctx, "8")
        ctx.d.text("Due:", 2, y, ctx.W, 1)
        use_font(ctx, "6")
        date_str = self.format_date(due_date)
        ctx.d.text(date_str, 2, y + 8, ctx.W, 1)
        
        # Alarm status
        y += 18
        alarm_str = "[X] Alarm ON" if has_alarm else "[ ] Alarm OFF"
        ctx.d.text(alarm_str, 2, y, ctx.W, 1)
        
        # Help
        ctx.d.text("e=edit  d=del  Space=done", 2, ctx.H - 6, ctx.W, 1)
    
    def draw_edit(self, ctx):
        """Draw todo edit mode"""
        if not self.selected_todo:
            return
        
        cls(ctx)
        header(ctx, "Edit Todo")
        
        text = "".join(self.edit_buffer)
        
        use_font(ctx, "6")
        
        # Show text with word wrap
        y = 14
        line_height = 7
        chars_per_line = 20
        max_lines = 5
        
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
        
        visible_lines = lines[:max_lines]
        for line in visible_lines:
            ctx.d.text(line, 2, y, ctx.W, 1)
            y += line_height
        
        # Cursor
        if len(visible_lines) > 0:
            last_line_y = 14 + (len(visible_lines) - 1) * line_height
            cursor_x = 2 + (len(visible_lines[-1]) * 6) % (ctx.W - 4)
            ctx.d.text("_", cursor_x, last_line_y, ctx.W, 1)
        
        # Character count
        char_count = len(text)
        char_info = "{}/128 chars".format(char_count)
        ctx.d.text(char_info, 2, ctx.H - 14, ctx.W, 1)
        
        # Help
        ctx.d.text("Enter=save  Esc=cancel", 2, ctx.H - 6, ctx.W, 1)
    
    def draw_new(self, ctx):
        """Draw new todo mode"""
        cls(ctx)
        header(ctx, "New Todo")
        
        text = "".join(self.edit_buffer)
        
        use_font(ctx, "6")
        ctx.d.text("Type your todo:", 2, 14, ctx.W, 1)
        
        y = 24
        line_height = 7
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
        
        if not lines:
            lines = ['']
        
        visible_lines = lines[:max_lines]
        for line in visible_lines:
            ctx.d.text(line, 2, y, ctx.W, 1)
            y += line_height
        
        # Cursor
        if len(visible_lines) > 0:
            last_line_y = 24 + (len(visible_lines) - 1) * line_height
            cursor_x = 2 + (len(visible_lines[-1]) * 6) % (ctx.W - 4)
            ctx.d.text("_", cursor_x, last_line_y, ctx.W, 1)
        
        # Character count
        char_count = len(text)
        char_info = "{}/128 chars".format(char_count)
        ctx.d.text(char_info, 2, ctx.H - 14, ctx.W, 1)
        
        # Help
        ctx.d.text("Enter=next  Esc=cancel", 2, ctx.H - 6, ctx.W, 1)
    
    def draw_set_date(self, ctx):
        """Draw date/time setting mode"""
        cls(ctx)
        # No header to save space
        
        use_font(ctx, "6")
        
        # Show current values - 6 fields on left side
        y = 2
        fields = ["Year", "Mon", "Day", "Hour", "Min", "Alarm"]
        
        for i, field in enumerate(fields):
            if i == self.date_field:
                ctx.d.set_pen(ctx.INK)
                ctx.d.rectangle(0, y - 1, 60, 8)  # Limit highlight to left side
                ctx.d.set_pen(ctx.BG)
            
            if i < 5:
                # Date/time fields
                value_str = "{}: {:04d}".format(field, self.date_values[i]) if i == 0 else "{}: {:02d}".format(field, self.date_values[i])
            else:
                # Alarm field
                value_str = "Alarm: {}".format("ON" if self.alarm_enabled else "OFF")
            
            ctx.d.text(value_str, 2, y, 60, 1)  # Left side only
            
            if i == self.date_field:
                ctx.d.set_pen(ctx.INK)
            
            y += 8
        
        # Help text on right side (vertical layout)
        help_x = 66  # Start at x=66 (leaving 2px margin from x=64)
        ctx.d.text("j/k", help_x, 2, ctx.W, 1)
        ctx.d.text("chg", help_x, 9, ctx.W, 1)
        ctx.d.text("", help_x, 16, ctx.W, 1)
        ctx.d.text("Tab", help_x, 23, ctx.W, 1)
        ctx.d.text("next", help_x, 30, ctx.W, 1)
        ctx.d.text("", help_x, 37, ctx.W, 1)
        ctx.d.text("Ent", help_x, 44, ctx.W, 1)
        ctx.d.text("save", help_x, 51, ctx.W, 1)
        ctx.d.text("Esc", help_x, 58, ctx.W, 1)
    
    def draw(self, ctx):
        if self.mode == 'list':
            self.draw_list(ctx)
        elif self.mode == 'view':
            self.draw_view(ctx)
        elif self.mode == 'edit':
            self.draw_edit(ctx)
        elif self.mode == 'new':
            self.draw_new(ctx)
        elif self.mode == 'set_date':
            self.draw_set_date(ctx)
    
    def handle_key(self, ctx, k):
        if self.mode == 'list':
            return self.handle_list_key(ctx, k)
        elif self.mode == 'view':
            return self.handle_view_key(ctx, k)
        elif self.mode == 'edit':
            return self.handle_edit_key(ctx, k)
        elif self.mode == 'new':
            return self.handle_new_key(ctx, k)
        elif self.mode == 'set_date':
            return self.handle_set_date_key(ctx, k)
    
    def handle_list_key(self, ctx, k):
        """Handle keys in list mode"""
        if k in (ord('q'), 27):
            return "pop"
        
        todos = self.get_sorted_todos(ctx)
        
        # Up/Down: Navigate todos
        if k in (0xB5, ord('k')):  # Up
            if todos:
                self.selected_index = max(0, self.selected_index - 1)
        
        elif k in (0xB6, ord('j')):  # Down
            if todos:
                self.selected_index = min(len(todos) - 1, self.selected_index + 1)
        
        # Enter: View todo
        elif k == 13:
            if todos and self.selected_index < len(todos):
                self.selected_todo = todos[self.selected_index]
                self.mode = 'view'
                self.scroll_offset = 0
        
        # Space: Toggle completion
        elif k == ord(' '):
            if todos and self.selected_index < len(todos):
                todos[self.selected_index]['completed'] = not todos[self.selected_index].get('completed', False)
                self.save_todos(ctx, todos)
        
        # N: New todo
        elif k in (ord('n'), ord('N')):
            self.mode = 'new'
            self.edit_buffer = []
            self.scroll_offset = 0
            self.alarm_enabled = False  # Reset alarm for new todo
        
        return None
    
    def handle_view_key(self, ctx, k):
        """Handle keys in view mode"""
        if k in (ord('q'), 27):  # Back
            self.mode = 'list'
            self.selected_todo = None
        
        elif k in (ord('e'), ord('E')) and self.selected_todo:  # Edit
            self.mode = 'edit'
            self.edit_buffer = list(self.selected_todo.get('text', ''))
        
        elif k in (ord('d'), ord('D')) and self.selected_todo:  # Delete
            todos = self.get_sorted_todos(ctx)
            for i, t in enumerate(todos):
                if (t.get('text') == self.selected_todo.get('text') and 
                    t.get('timestamp') == self.selected_todo.get('timestamp')):
                    todos.pop(i)
                    break
            self.save_todos(ctx, todos)
            self.mode = 'list'
            self.selected_todo = None
        
        elif k == ord(' ') and self.selected_todo:  # Toggle completion
            self.selected_todo['completed'] = not self.selected_todo.get('completed', False)
            todos = self.get_sorted_todos(ctx)
            for i, t in enumerate(todos):
                if id(t) == id(self.selected_todo):
                    todos[i] = self.selected_todo
                    break
            self.save_todos(ctx, todos)
        
        elif k in (ord('a'), ord('A')) and self.selected_todo:  # Toggle alarm
            self.selected_todo['alarm'] = not self.selected_todo.get('alarm', False)
            todos = self.get_sorted_todos(ctx)
            for i, t in enumerate(todos):
                if id(t) == id(self.selected_todo):
                    todos[i] = self.selected_todo
                    break
            self.save_todos(ctx, todos)
        
        return None
    
    def handle_edit_key(self, ctx, k):
        """Handle keys in edit mode"""
        if k == 13 and self.selected_todo:  # Save
            new_text = "".join(self.edit_buffer).strip()
            if new_text:
                self.selected_todo['text'] = new_text
                todos = self.get_sorted_todos(ctx)
                for i, t in enumerate(todos):
                    if id(t) == id(self.selected_todo):
                        todos[i] = self.selected_todo
                        break
                self.save_todos(ctx, todos)
            self.mode = 'view'
            self.edit_buffer = []
        
        elif k == 27:  # Cancel
            self.mode = 'view'
            self.edit_buffer = []
        
        elif k in (8, 127):  # Backspace
            if self.edit_buffer:
                self.edit_buffer.pop()
        
        else:
            # Add character (limit to 128)
            if len(self.edit_buffer) < 128:
                try:
                    ch = chr(k)
                    if ch:
                        self.edit_buffer.append(ch)
                except:
                    pass
        
        return None
    
    def handle_new_key(self, ctx, k):
        """Handle keys in new todo mode"""
        if k == 13:  # Next - go to date setting
            new_text = "".join(self.edit_buffer).strip()
            if new_text:
                # Initialize date values to current time + 1 hour
                now = time.localtime()
                self.date_values = [now[0], now[1], now[2], (now[3] + 1) % 24, 0]
                self.date_field = 0
                self.alarm_enabled = False  # Default alarm off
                self._new_text = new_text
                self.mode = 'set_date'
            else:
                # No text, go back to list
                self.mode = 'list'
            self.edit_buffer = []
        
        elif k == 27:  # Cancel
            self.mode = 'list'
            self.edit_buffer = []
        
        elif k in (8, 127):  # Backspace
            if self.edit_buffer:
                self.edit_buffer.pop()
        
        else:
            # Add character (limit to 128)
            if len(self.edit_buffer) < 128:
                try:
                    ch = chr(k)
                    if ch:
                        self.edit_buffer.append(ch)
                except:
                    pass
        
        return None
    
    def handle_set_date_key(self, ctx, k):
        """Handle keys in date setting mode"""
        if k == 13:  # Save with date
            # Create timestamp from date values
            year, month, day, hour, minute = self.date_values
            # Create a timestamp (simplified - may not work on all systems)
            try:
                # Set the time temporarily to get timestamp
                import machine
                rtc = machine.RTC()
                rtc.datetime((year, month, day, 0, hour, minute, 0, 0))
                due_timestamp = time.time()
                # Restore current time (user should set it back if needed)
            except:
                # Fallback: use a simple calculation
                due_timestamp = time.time() + 3600  # 1 hour from now as fallback
            
            todos = self.get_sorted_todos(ctx)
            todos.append({
                'text': self._new_text,
                'completed': False,
                'due_date': due_timestamp,
                'alarm': self.alarm_enabled,
                'timestamp': time.time()
            })
            self.save_todos(ctx, todos)
            self.mode = 'list'
            self.selected_index = 0
        
        elif k == 27:  # Skip date, save without due date
            todos = self.get_sorted_todos(ctx)
            todos.append({
                'text': self._new_text,
                'completed': False,
                'due_date': None,
                'alarm': False,
                'timestamp': time.time()
            })
            self.save_todos(ctx, todos)
            self.mode = 'list'
            self.selected_index = 0
        
        elif k in (9, ord('\t')):  # Tab - next field
            self.date_field = (self.date_field + 1) % 6  # Now 6 fields including alarm
        
        elif k in (0xB5, ord('k')):  # Up - increment value
            if self.date_field == 0:  # Year
                self.date_values[0] = min(2100, self.date_values[0] + 1)
            elif self.date_field == 1:  # Month
                self.date_values[1] = (self.date_values[1] % 12) + 1
            elif self.date_field == 2:  # Day
                self.date_values[2] = (self.date_values[2] % 31) + 1
            elif self.date_field == 3:  # Hour
                self.date_values[3] = (self.date_values[3] + 1) % 24
            elif self.date_field == 4:  # Minute
                self.date_values[4] = (self.date_values[4] + 5) % 60
            elif self.date_field == 5:  # Alarm
                self.alarm_enabled = not self.alarm_enabled
        
        elif k in (0xB6, ord('j')):  # Down - decrement value
            if self.date_field == 0:  # Year
                self.date_values[0] = max(2024, self.date_values[0] - 1)
            elif self.date_field == 1:  # Month
                self.date_values[1] = ((self.date_values[1] - 2) % 12) + 1
            elif self.date_field == 2:  # Day
                self.date_values[2] = ((self.date_values[2] - 2) % 31) + 1
            elif self.date_field == 3:  # Hour
                self.date_values[3] = (self.date_values[3] - 1) % 24
            elif self.date_field == 4:  # Minute
                self.date_values[4] = (self.date_values[4] - 5) % 60
            elif self.date_field == 5:  # Alarm
                self.alarm_enabled = not self.alarm_enabled
        
        return None

