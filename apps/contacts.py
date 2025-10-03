# Contacts App

import time
from apps.base import App
from core.ui import cls, header, use_font
from core.input import read_key


class ContactsApp(App):
    title = "TEL"
    tick_ms = 200
    
    def __init__(self):
        self.current_letter = 'A'
        self.selected_index = 0
        self.mode = 'list'  # 'list', 'detail', 'edit', 'new'
        self.selected_contact = None
        self.edit_field = None  # 'name' or 'phone'
        self.edit_buffer = []
        
        # Alphabet bitmap: 99x8 pixels (approx), each letter 4px wide, no separation in bitmap
        self.alphabet_bitmap = [
            0b00110011100111001110011110111100111010010111100001010010100001001010010111101111011110111001111011110100101001010010100101111000,
            0b00110010010100101001010000100001000010010010000001010010100001111010010100101001010010100101000000100100101001010010100100001000,
            0b01001010010100001001010000100001000010010010000001010100100001001011010100101001010010101001000000100100101001001100111100010000,
            0b01001011100100001001011100111001000011110010000001011000100001001011010100101111010010110001111000100100101001001000001000010000,
            0b01111010010100001001010000100001000010010010000001011000100001001010110100101000010010101000001000100100101001000100001000100000,
            0b01001010010100001001010000100001011010010010000001010100100001001010110100101000010010100100001000100100101001001100001000100000,
            0b01001010010100101001010000100001001010010010000001010010100001001010010100101000001100100100001000100100101111010010001001000000,
            0b01001011110111001110011110100000111010010111101111010010111101001010010111101000000010100101111000100111101111010010001001111000,]
    
    def draw_icon(self, ctx, x, y, w, h):
        icon = [
            0b0011111111111110,
            0b0100000000000001,
            0b0100110000111001,
            0b0101001101000101,
            0b0101001000111001,
            0b0101001100000001,
            0b0101001001010101,
            0b0101001100000001,
            0b0101001001010101,
            0b0101001100000001,
            0b0101111001010101,
            0b0100010000000001,
            0b0100010000111001,
            0b0100010000000001,
            0b0011111111111110,
            0b0001110000000000,
        ]
        start_x = x + (w - 16) // 2
        start_y = y + (h - 12) // 2
        
        for row, bits in enumerate(icon):
            for col in range(16):
                if bits & (1 << (15 - col)):
                    ctx.d.pixel(start_x + col, start_y + row)
    
    def get_contacts_by_letter(self, ctx):
        """Group contacts alphabetically by first letter"""
        contacts = ctx.ds.load_contacts()
        grouped = {}
        
        for contact in contacts:
            name = contact.get('name', '').strip().upper()
            if not name:
                continue
            letter = name[0] if name[0].isalpha() else '#'
            if letter not in grouped:
                grouped[letter] = []
            grouped[letter].append(contact)
        
        # Sort contacts within each letter
        for letter in grouped:
            grouped[letter].sort(key=lambda c: c.get('name', '').lower())
        
        return grouped
    
    def draw_letter_from_bitmap(self, ctx, letter_index, x, y, invert=False):
        """Draw a single letter from the alphabet bitmap"""
        # Each letter is 4 pixels wide, consecutive in bitmap (no separation)
        # Bitmap has 99 bits total, so we use the actual bit length
        start_bit = letter_index * 4  # Starting position - letters are consecutive
        bitmap_width = 128  # Actual width of the bitmap
        
        for row in range(8):
            bitmap_row = self.alphabet_bitmap[row]
            for col in range(4):  # Each letter is 4 pixels wide
                bit_pos = start_bit + col
                # Safety check to prevent overflow
                if bit_pos >= bitmap_width:
                    continue
                # Access from MSB (left) to LSB (right)
                # For a 99-bit number, leftmost bit is at position 98 (when counting from right)
                if bitmap_row & (1 << (bitmap_width - 1 - bit_pos)):
                    if invert:
                        # Don't draw (will show as background color when inverted)
                        pass
                    else:
                        ctx.d.pixel(x + col, y + row)
                else:
                    if invert:
                        ctx.d.pixel(x + col, y + row)
    
    def draw_alphabet_bar(self, ctx, grouped):
        """Draw alphabet navigation bar at bottom using bitmap"""
        # Single line at y=56 (near bottom of 64px display)
        y = 56
        x = 0  # Start at x=0 (26 letters * 6px = 156px, will need to scroll or fit)
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        for i, letter in enumerate(letters):
            # Skip letters that would go off screen (128px width)
            if x + 4 > 128:
                break
                
            # Highlight current letter or letters with contacts
            if letter == self.current_letter:
                # Selected letter - filled background
                ctx.d.set_pen(ctx.INK)
                ctx.d.rectangle(x, y, 4, 8)
                ctx.d.set_pen(ctx.BG)
                self.draw_letter_from_bitmap(ctx, i, x, y, invert=True)
                ctx.d.set_pen(ctx.INK)
            elif letter in grouped:
                # Letter with contacts - draw frame
                #ctx.d.rectangle(x - 1, y - 1, 6, 10)
                pass
                self.draw_letter_from_bitmap(ctx, i, x, y, invert=False)
            else:
                # Normal letter
                self.draw_letter_from_bitmap(ctx, i, x, y, invert=False)
            
            # Move to next letter position (4px letter + 2px separation)
            x += 6
    
    def draw_list(self, ctx):
        """Draw contacts list view"""
        cls(ctx)
        # No header to save space
        
        grouped = self.get_contacts_by_letter(ctx)
        contacts_in_letter = grouped.get(self.current_letter, [])
        
        use_font(ctx, "6")
        # Display current letter and count at top
        letter_info = "{}: {} contact{}".format(
            self.current_letter, 
            len(contacts_in_letter),
            's' if len(contacts_in_letter) != 1 else ''
        )
        ctx.d.text(letter_info, 2, 2, ctx.W, 1)
        
        # Display contacts - limited area to avoid alphabet bar
        y = 10
        max_visible = 3  # Increased - single line alphabet bar gives more room
        max_y = 40  # Stop before help text and alphabet bar (now at y=56)
        
        # Ensure selected index is valid
        if self.selected_index >= len(contacts_in_letter):
            self.selected_index = max(0, len(contacts_in_letter) - 1)
        
        # Calculate visible range
        start_idx = max(0, self.selected_index - 1)
        visible_contacts = contacts_in_letter[start_idx:start_idx + max_visible]
        
        for i, contact in enumerate(visible_contacts):
            actual_idx = start_idx + i
            
            # Stop rendering if we would exceed the safe area
            if y + 14 > max_y:
                break
            
            name = contact.get('name', '')[:16]
            phone = contact.get('phone', '')
            
            # Show last 6 digits of phone
            phone_excerpt = phone[-6:] if len(phone) > 6 else phone
            
            # Highlight selected
            if actual_idx == self.selected_index:
                ctx.d.set_pen(ctx.INK)
                ctx.d.rectangle(0, y - 1, ctx.W, 15)
                ctx.d.set_pen(ctx.BG)
            
            # Contact info on two lines
            ctx.d.text(name, 2, y, ctx.W, 1)
            ctx.d.text("..{}".format(phone_excerpt), 2, y + 7, ctx.W, 1)
            
            if actual_idx == self.selected_index:
                ctx.d.set_pen(ctx.INK)
            
            y += 16
        
        # Help text above alphabet bar
        use_font(ctx, "6")
        ctx.d.text("n=new  Enter=view  q=quit", 2, 48, ctx.W, 1)
        
        # Draw alphabet bar
        self.draw_alphabet_bar(ctx, grouped)
    
    def draw_detail(self, ctx):
        """Draw contact detail view"""
        if not self.selected_contact:
            return
        
        cls(ctx)
        header(ctx, "Contact Detail")
        
        use_font(ctx, "8")
        ctx.d.text("Name:", 2, 12, ctx.W, 1)
        use_font(ctx, "6")
        name = self.selected_contact.get('name', '') if self.selected_contact else ''
        # Word wrap name if too long
        if len(name) <= 20:
            ctx.d.text(name, 2, 22, ctx.W, 1)
        else:
            ctx.d.text(name[:20], 2, 22, ctx.W, 1)
            ctx.d.text(name[20:40], 2, 29, ctx.W, 1)
        
        use_font(ctx, "8")
        ctx.d.text("Phone:", 2, 38, ctx.W, 1)
        use_font(ctx, "6")
        phone = self.selected_contact.get('phone', '') if self.selected_contact else ''
        ctx.d.text(phone, 2, 48, ctx.W, 1)
        
        # Actions
        use_font(ctx, "6")
        ctx.d.text("e=edit  d=delete  q=back", 2, ctx.H - 6, ctx.W, 1)
    
    def draw_edit(self, ctx):
        """Draw contact edit view"""
        if not self.selected_contact:
            return
            
        cls(ctx)
        header(ctx, "Edit Contact")
        
        use_font(ctx, "8")
        ctx.d.text("Name:", 2, 12, ctx.W, 1)
        use_font(ctx, "6")
        name = self.selected_contact.get('name', '')
        if self.edit_field == 'name':
            name = "".join(self.edit_buffer)
            ctx.d.set_pen(ctx.INK)
            ctx.d.rectangle(0, 21, ctx.W, 9)
            ctx.d.set_pen(ctx.BG)
        ctx.d.text(name[:20], 2, 22, ctx.W, 1)
        ctx.d.set_pen(ctx.INK)
        
        use_font(ctx, "8")
        ctx.d.text("Phone:", 2, 34, ctx.W, 1)
        use_font(ctx, "6")
        phone = self.selected_contact.get('phone', '')
        if self.edit_field == 'phone':
            phone = "".join(self.edit_buffer)
            ctx.d.set_pen(ctx.INK)
            ctx.d.rectangle(0, 43, ctx.W, 9)
            ctx.d.set_pen(ctx.BG)
        ctx.d.text(phone[:20], 2, 44, ctx.W, 1)
        ctx.d.set_pen(ctx.INK)
        
        # Help
        use_font(ctx, "6")
        if self.edit_field:
            ctx.d.text("Enter=save  Esc=cancel", 2, ctx.H - 6, ctx.W, 1)
        else:
            ctx.d.text("n=name  p=phone  q=back", 2, ctx.H - 6, ctx.W, 1)
    
    def draw_new(self, ctx):
        """Draw new contact view"""
        cls(ctx)
        header(ctx, "New Contact")
        
        use_font(ctx, "8")
        ctx.d.text("Name:", 2, 12, ctx.W, 1)
        use_font(ctx, "6")
        if self.edit_field == 'name':
            name = "".join(self.edit_buffer)
            ctx.d.set_pen(ctx.INK)
            ctx.d.rectangle(0, 21, ctx.W, 9)
            ctx.d.set_pen(ctx.BG)
            ctx.d.text(name[:20], 2, 22, ctx.W, 1)
            ctx.d.set_pen(ctx.INK)
        else:
            name = getattr(self, '_new_name', '')
            ctx.d.text(name[:20], 2, 22, ctx.W, 1)
        
        use_font(ctx, "8")
        ctx.d.text("Phone:", 2, 34, ctx.W, 1)
        use_font(ctx, "6")
        if self.edit_field == 'phone':
            phone = "".join(self.edit_buffer)
            ctx.d.set_pen(ctx.INK)
            ctx.d.rectangle(0, 43, ctx.W, 9)
            ctx.d.set_pen(ctx.BG)
            ctx.d.text(phone[:20], 2, 44, ctx.W, 1)
            ctx.d.set_pen(ctx.INK)
        else:
            phone = getattr(self, '_new_phone', '')
            ctx.d.text(phone[:20], 2, 44, ctx.W, 1)
        
        # Help
        use_font(ctx, "6")
        if self.edit_field:
            ctx.d.text("Enter=next  Esc=cancel", 2, ctx.H - 6, ctx.W, 1)
        else:
            ctx.d.text("Press 'n' to start", 2, ctx.H - 6, ctx.W, 1)
    
    def draw(self, ctx):
        if self.mode == 'list':
            self.draw_list(ctx)
        elif self.mode == 'detail':
            self.draw_detail(ctx)
        elif self.mode == 'edit':
            self.draw_edit(ctx)
        elif self.mode == 'new':
            self.draw_new(ctx)
    
    def handle_key(self, ctx, k):
        if self.mode == 'list':
            return self.handle_list_key(ctx, k)
        elif self.mode == 'detail':
            return self.handle_detail_key(ctx, k)
        elif self.mode == 'edit':
            return self.handle_edit_key(ctx, k)
        elif self.mode == 'new':
            return self.handle_new_key(ctx, k)
    
    def handle_list_key(self, ctx, k):
        """Handle keys in list mode"""
        if k in (ord('q'), 27):
            return "pop"
        
        grouped = self.get_contacts_by_letter(ctx)
        contacts_in_letter = grouped.get(self.current_letter, [])
        
        # Left/Right: Navigate letters
        if k in (0xB4, ord('h')):  # Left arrow or 'h'
            letters = sorted([l for l in grouped.keys() if l.isalpha()])
            if letters:
                try:
                    idx = letters.index(self.current_letter)
                    idx = (idx - 1) % len(letters)
                    self.current_letter = letters[idx]
                    self.selected_index = 0
                except ValueError:
                    self.current_letter = letters[0]
                    self.selected_index = 0
        
        elif k in (0xB7, ord('l')):  # Right arrow or 'l'
            letters = sorted([l for l in grouped.keys() if l.isalpha()])
            if letters:
                try:
                    idx = letters.index(self.current_letter)
                    idx = (idx + 1) % len(letters)
                    self.current_letter = letters[idx]
                    self.selected_index = 0
                except ValueError:
                    self.current_letter = letters[0]
                    self.selected_index = 0
        
        # Up/Down: Navigate contacts
        elif k in (0xB5, ord('k')):  # Up arrow or 'k'
            if contacts_in_letter:
                self.selected_index = max(0, self.selected_index - 1)
        
        elif k in (0xB6, ord('j')):  # Down arrow or 'j'
            if contacts_in_letter:
                self.selected_index = min(len(contacts_in_letter) - 1, self.selected_index + 1)
        
        # Enter: View details
        elif k == 13:
            if contacts_in_letter and self.selected_index < len(contacts_in_letter):
                self.selected_contact = contacts_in_letter[self.selected_index]
                self.mode = 'detail'
        
        # N: New contact
        elif k in (ord('n'), ord('N')):
            self.mode = 'new'
            self.edit_field = 'name'
            self.edit_buffer = []
            self._new_name = ''
            self._new_phone = ''
        
        return None
    
    def handle_detail_key(self, ctx, k):
        """Handle keys in detail mode"""
        if k in (ord('q'), 27):  # Back to list
            self.mode = 'list'
            self.selected_contact = None
        
        elif k in (ord('e'), ord('E')):  # Edit
            self.mode = 'edit'
            self.edit_field = None
        
        elif k in (ord('d'), ord('D')) and self.selected_contact:  # Delete
            contacts = ctx.ds.load_contacts()
            # Find and remove the contact
            for i, c in enumerate(contacts):
                if (c.get('name') == self.selected_contact.get('name') and 
                    c.get('phone') == self.selected_contact.get('phone')):
                    contacts.pop(i)
                    break
            ctx.ds.save_contacts(contacts)
            self.mode = 'list'
            self.selected_contact = None
        
        return None
    
    def handle_edit_key(self, ctx, k):
        """Handle keys in edit mode"""
        if self.edit_field and self.selected_contact:
            # Editing a field
            if k == 13:  # Enter - save
                if self.edit_field == 'name':
                    self.selected_contact['name'] = "".join(self.edit_buffer).strip()
                elif self.edit_field == 'phone':
                    self.selected_contact['phone'] = "".join(self.edit_buffer).strip()
                
                # Save to storage
                contacts = ctx.ds.load_contacts()
                # Find the original contact and update it
                for i, c in enumerate(contacts):
                    if id(c) == id(self.selected_contact):
                        contacts[i] = self.selected_contact
                        break
                ctx.ds.save_contacts(contacts)
                
                self.edit_field = None
                self.edit_buffer = []
            
            elif k == 27:  # Esc - cancel
                self.edit_field = None
                self.edit_buffer = []
            
            elif k in (8, 127):  # Backspace
                if self.edit_buffer:
                    self.edit_buffer.pop()
            
            else:
                # Add character
                try:
                    ch = chr(k)
                    if ch and len(self.edit_buffer) < 24:
                        self.edit_buffer.append(ch)
                except:
                    pass
        
        else:
            # Not editing, choose field
            if k in (ord('q'), 27):
                self.mode = 'detail'
            
            elif k in (ord('n'), ord('N')) and self.selected_contact:
                self.edit_field = 'name'
                self.edit_buffer = list(self.selected_contact.get('name', ''))
            
            elif k in (ord('p'), ord('P')) and self.selected_contact:
                self.edit_field = 'phone'
                self.edit_buffer = list(self.selected_contact.get('phone', ''))
        
        return None
    
    def handle_new_key(self, ctx, k):
        """Handle keys in new contact mode"""
        if self.edit_field:
            # Editing a field
            if k == 13:  # Enter - next field or save
                if self.edit_field == 'name':
                    self._new_name = "".join(self.edit_buffer).strip()
                    if not self._new_name:
                        return None  # Can't proceed without name
                    self.edit_field = 'phone'
                    self.edit_buffer = []
                
                elif self.edit_field == 'phone':
                    self._new_phone = "".join(self.edit_buffer).strip()
                    # Save new contact
                    contacts = ctx.ds.load_contacts()
                    contacts.append({"name": self._new_name, "phone": self._new_phone})
                    ctx.ds.save_contacts(contacts)
                    
                    # Return to list
                    self.mode = 'list'
                    self.edit_field = None
                    self.edit_buffer = []
                    # Jump to the letter of new contact
                    if self._new_name:
                        self.current_letter = self._new_name[0].upper()
                        self.selected_index = 0
            
            elif k == 27:  # Esc - cancel
                self.mode = 'list'
                self.edit_field = None
                self.edit_buffer = []
            
            elif k in (8, 127):  # Backspace
                if self.edit_buffer:
                    self.edit_buffer.pop()
            
            else:
                # Add character
                try:
                    ch = chr(k)
                    if ch and len(self.edit_buffer) < 24:
                        self.edit_buffer.append(ch)
                except:
                    pass
        
        else:
            # Start editing
            if k in (ord('n'), ord('N')):
                self.edit_field = 'name'
                self.edit_buffer = []
            elif k in (ord('q'), 27):
                self.mode = 'list'
        
        return None
