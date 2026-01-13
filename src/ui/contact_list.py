"""
Kontaktlista-panel för KontaktRegister.
Vänster panel med lista över kontakter.
"""

import customtkinter as ctk
from typing import Optional, Callable, List
from PIL import Image, ImageDraw
import base64
import io

from ui.theme import Theme
from database.models import Contact
from config import CONTACT_LIST_WIDTH, CONTACT_THUMBNAIL_SIZE


class ContactListItem(ctk.CTkFrame):
    """En kontakt i listan."""
    
    def __init__(
        self,
        parent,
        contact: Contact,
        on_select: Callable[[Contact], None],
        is_selected: bool = False
    ):
        super().__init__(
            parent,
            fg_color=Theme.BG_SELECTED if is_selected else Theme.BG_LIGHT,
            corner_radius=8,
            height=56
        )
        
        self.contact = contact
        self.on_select = on_select
        self.is_selected = is_selected
        
        self.pack_propagate(False)
        
        # Bind klick på hela ramen
        self.bind("<Button-1>", self._on_click)
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Thumbnail
        thumbnail_frame = ctk.CTkFrame(self, fg_color="transparent", width=50)
        thumbnail_frame.pack(side="left", padx=(8, 0), pady=8)
        thumbnail_frame.pack_propagate(False)
        
        # Skapa eller ladda thumbnail
        thumbnail_image = self._get_thumbnail()
        
        self.thumbnail_label = ctk.CTkLabel(
            thumbnail_frame,
            text="",
            image=thumbnail_image,
            width=40,
            height=40
        )
        self.thumbnail_label.pack(expand=True)
        self.thumbnail_label.bind("<Button-1>", self._on_click)
        
        # Textinfo
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        text_frame.bind("<Button-1>", self._on_click)
        
        # Namn
        name_text = self.contact.name or "(Inget namn)"
        self.name_label = ctk.CTkLabel(
            text_frame,
            text=name_text,
            font=Theme.get_font("normal", bold=True),
            text_color=Theme.ACCENT_GOLD if self.is_selected else Theme.TEXT_PRIMARY,
            anchor="w"
        )
        self.name_label.pack(fill="x")
        self.name_label.bind("<Button-1>", self._on_click)
        
        # Företag/titel
        subtitle = self.contact.company or self.contact.title or ""
        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                text_frame,
                text=subtitle,
                font=Theme.get_font("small"),
                text_color=Theme.TEXT_SECONDARY,
                anchor="w"
            )
            self.subtitle_label.pack(fill="x")
            self.subtitle_label.bind("<Button-1>", self._on_click)
        
        # Favorit-indikator
        if self.contact.is_favorite:
            star_label = ctk.CTkLabel(
                self,
                text="★",
                font=Theme.get_font("normal"),
                text_color=Theme.ACCENT_GOLD,
                width=20
            )
            star_label.pack(side="right", padx=(0, 8))
            star_label.bind("<Button-1>", self._on_click)
        
        # Pil
        arrow_label = ctk.CTkLabel(
            self,
            text="›",
            font=("Segoe UI", 18),
            text_color=Theme.ACCENT_GOLD if self.is_selected else Theme.TEXT_MUTED,
            width=20
        )
        arrow_label.pack(side="right", padx=(0, 5))
        arrow_label.bind("<Button-1>", self._on_click)
        
        # Hover-effekt
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _get_thumbnail(self) -> ctk.CTkImage:
        """Skapar eller laddar thumbnail för kontakten."""
        size = CONTACT_THUMBNAIL_SIZE
        
        if self.contact.photo:
            try:
                # Ladda från base64
                image_data = base64.b64decode(self.contact.photo)
                image = Image.open(io.BytesIO(image_data))
                image = image.resize(size, Image.Resampling.LANCZOS)
                return ctk.CTkImage(light_image=image, dark_image=image, size=size)
            except Exception:
                pass
        
        # Skapa default avatar med initialer
        image = Image.new('RGBA', size, Theme.BG_HOVER)
        draw = ImageDraw.Draw(image)
        
        # Rita cirkel
        draw.ellipse([0, 0, size[0]-1, size[1]-1], fill=Theme.BG_SELECTED, outline=Theme.BORDER)
        
        # Initialer
        initials = self._get_initials()
        
        # Enkel textpositionering (centrerad)
        text_bbox = draw.textbbox((0, 0), initials)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2 - 2
        draw.text((x, y), initials, fill=Theme.ACCENT_GOLD)
        
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
    
    def _get_initials(self) -> str:
        """Returnerar initialer från namn."""
        name = self.contact.name.strip()
        if not name:
            return "?"
        
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[0].upper()
    
    def _on_click(self, event=None):
        self.on_select(self.contact)
    
    def _on_enter(self, event=None):
        if not self.is_selected:
            self.configure(fg_color=Theme.BG_HOVER)
    
    def _on_leave(self, event=None):
        if not self.is_selected:
            self.configure(fg_color=Theme.BG_LIGHT)
    
    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.configure(fg_color=Theme.BG_SELECTED if selected else Theme.BG_LIGHT)
        self.name_label.configure(
            text_color=Theme.ACCENT_GOLD if selected else Theme.TEXT_PRIMARY
        )


class ContactListPanel(ctk.CTkFrame):
    """Panel med kontaktlista."""
    
    def __init__(
        self,
        parent,
        on_select: Callable[[Contact], None],
        on_add: Callable[[], None]
    ):
        super().__init__(
            parent,
            fg_color=Theme.BG_LIGHT,
            corner_radius=12,
            width=CONTACT_LIST_WIDTH
        )
        
        self.on_select = on_select
        self.on_add = on_add
        self.contacts: List[Contact] = []
        self.selected_contact: Optional[Contact] = None
        self.contact_items: List[ContactListItem] = []
        
        self.pack_propagate(False)
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Rubrik
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="Kontaktlista",
            font=Theme.get_font("heading", bold=True),
            text_color=Theme.ACCENT_GOLD
        ).pack(side="left", anchor="w")
        
        # Sökfält (lokal sökning i listan)
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="🔍 Sök kontakter...",
            **Theme.get_entry_colors(),
            height=36,
            corner_radius=8
        )
        self.search_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Scrollbar container
        self.list_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Theme.BG_HOVER,
            scrollbar_button_hover_color=Theme.BORDER
        )
        self.list_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Lägg till-knapp
        add_button = ctk.CTkButton(
            self,
            text="+ Lägg till kontakt",
            font=Theme.get_font("normal"),
            height=40,
            corner_radius=8,
            command=self.on_add,
            **Theme.get_button_colors()
        )
        add_button.pack(fill="x", padx=15, pady=(0, 15))
    
    def _on_search(self, event=None):
        """Lokal filtrering av listan."""
        query = self.search_entry.get().strip().lower()
        
        for item in self.contact_items:
            if not query or item.contact.matches_search(query):
                item.pack(fill="x", pady=2)
            else:
                item.pack_forget()
    
    def update_contacts(self, contacts: List[Contact]):
        """Uppdaterar kontaktlistan."""
        self.contacts = contacts
        
        # Rensa gamla items
        for item in self.contact_items:
            item.destroy()
        self.contact_items.clear()
        
        # Skapa nya items
        for contact in contacts:
            is_selected = (
                self.selected_contact is not None and 
                contact.id == self.selected_contact.id
            )
            item = ContactListItem(
                self.list_container,
                contact,
                self._on_item_select,
                is_selected
            )
            item.pack(fill="x", pady=2)
            self.contact_items.append(item)
        
        # Återapplicera sökfilter
        self._on_search()
    
    def _on_item_select(self, contact: Contact):
        """Hanterar val av kontakt."""
        self.selected_contact = contact
        
        # Uppdatera visuellt
        for item in self.contact_items:
            item.set_selected(item.contact.id == contact.id)
        
        self.on_select(contact)
    
    def select_contact(self, contact: Optional[Contact]):
        """Väljer en kontakt programmatiskt."""
        self.selected_contact = contact
        
        for item in self.contact_items:
            if contact and item.contact.id == contact.id:
                item.set_selected(True)
            else:
                item.set_selected(False)
    
    def get_selected(self) -> Optional[Contact]:
        """Returnerar vald kontakt."""
        return self.selected_contact
    
    def clear_search(self):
        """Rensar sökfältet."""
        self.search_entry.delete(0, "end")
        self._on_search()
