"""
Kontaktdetaljvy för KontaktRegister.
Höger panel med detaljerad information om vald kontakt.
"""

import customtkinter as ctk
from typing import Optional, Callable
from PIL import Image, ImageDraw
import base64
import io
import webbrowser
import subprocess
import urllib.parse

from ui.theme import Theme
from database.models import Contact, SocialMedia
from config import CONTACT_PHOTO_SIZE


class ContactDetailPanel(ctk.CTkFrame):
    """Panel med kontaktdetaljer."""
    
    def __init__(
        self,
        parent,
        on_edit: Callable[[Contact], None],
        on_delete: Callable[[Contact], None],
        on_export: Callable[[Contact], None]
    ):
        super().__init__(
            parent,
            fg_color=Theme.BG_LIGHT,
            corner_radius=12
        )
        
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_export = on_export
        self.contact: Optional[Contact] = None
        
        self._create_widgets()
        self._show_empty_state()
    
    def _create_widgets(self):
        # Huvudcontainer med scrollning
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Theme.BG_HOVER,
            scrollbar_button_hover_color=Theme.BORDER
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tomt meddelande (visas när ingen kontakt är vald)
        self.empty_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        
        # Detaljcontainer
        self.detail_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        
        # === Header med foto och namn ===
        self.header_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=20)
        
        # Foto
        self.photo_frame = ctk.CTkFrame(
            self.header_frame,
            fg_color=Theme.BG_MEDIUM,
            corner_radius=12,
            width=160,
            height=160
        )
        self.photo_frame.pack(side="left")
        self.photo_frame.pack_propagate(False)
        
        self.photo_label = ctk.CTkLabel(
            self.photo_frame,
            text="",
            width=150,
            height=150
        )
        self.photo_label.pack(expand=True, padx=5, pady=5)
        
        # Namn och titel
        self.name_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.name_frame.pack(side="left", fill="both", expand=True, padx=(20, 0))
        
        self.name_label = ctk.CTkLabel(
            self.name_frame,
            text="",
            font=Theme.get_font("title", bold=True),
            text_color=Theme.ACCENT_GOLD,
            anchor="w"
        )
        self.name_label.pack(fill="x", anchor="w")
        
        self.title_label = ctk.CTkLabel(
            self.name_frame,
            text="",
            font=Theme.get_font("heading"),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        )
        self.title_label.pack(fill="x", anchor="w")
        
        # Favorit-knapp
        self.favorite_button = ctk.CTkButton(
            self.name_frame,
            text="☆ Favorit",
            width=100,
            height=32,
            font=Theme.get_font("small"),
            command=self._toggle_favorite,
            **Theme.get_secondary_button_colors()
        )
        self.favorite_button.pack(anchor="w", pady=(10, 0))
        
        # === Kontaktinfo ===
        self.info_frame = ctk.CTkFrame(
            self.detail_frame,
            fg_color=Theme.BG_MEDIUM,
            corner_radius=10
        )
        self.info_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # === Taggar ===
        self.tags_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        self.tags_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # === Anteckningar ===
        self.notes_frame = ctk.CTkFrame(
            self.detail_frame,
            fg_color=Theme.BG_MEDIUM,
            corner_radius=10
        )
        self.notes_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # === Knappar ===
        self.button_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Redigera
        ctk.CTkButton(
            self.button_frame,
            text="✎ Redigera",
            width=110,
            height=38,
            font=Theme.get_font("normal"),
            command=self._on_edit,
            **Theme.get_button_colors()
        ).pack(side="left", padx=(0, 10))
        
        # Radera
        delete_colors = Theme.get_secondary_button_colors()
        delete_colors["text_color"] = Theme.ERROR
        ctk.CTkButton(
            self.button_frame,
            text="🗑 Radera",
            width=100,
            height=38,
            font=Theme.get_font("normal"),
            command=self._on_delete,
            **delete_colors
        ).pack(side="left", padx=(0, 10))
        
        # Exportera
        ctk.CTkButton(
            self.button_frame,
            text="📤 Exportera",
            width=110,
            height=38,
            font=Theme.get_font("normal"),
            command=self._on_export,
            **Theme.get_secondary_button_colors()
        ).pack(side="left")
    
    def _show_empty_state(self):
        """Visar tomt meddelande."""
        self.detail_frame.pack_forget()
        self.empty_frame.pack(fill="both", expand=True)
        
        # Rensa och skapa nytt innehåll
        for widget in self.empty_frame.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self.empty_frame,
            text="Välj en kontakt",
            font=Theme.get_font("heading"),
            text_color=Theme.TEXT_MUTED
        ).pack(expand=True)
    
    def show_contact(self, contact: Contact):
        """Visar en kontakts detaljer."""
        self.contact = contact
        
        self.empty_frame.pack_forget()
        self.detail_frame.pack(fill="both", expand=True)
        
        # Uppdatera foto
        self._update_photo()
        
        # Uppdatera namn och titel
        self.name_label.configure(text=contact.name or "(Inget namn)")
        
        title_text = ""
        if contact.title and contact.company:
            title_text = f"{contact.title} på {contact.company}"
        elif contact.title:
            title_text = contact.title
        elif contact.company:
            title_text = contact.company
        self.title_label.configure(text=title_text)
        
        # Favorit-knapp
        if contact.is_favorite:
            self.favorite_button.configure(text="★ Favorit", fg_color=Theme.ACCENT_GOLD_DARK)
        else:
            self.favorite_button.configure(text="☆ Favorit", fg_color=Theme.BG_LIGHT)
        
        # Uppdatera kontaktinfo
        self._update_info()
        
        # Uppdatera taggar
        self._update_tags()
        
        # Uppdatera anteckningar
        self._update_notes()
    
    def _update_photo(self):
        """Uppdaterar kontaktfotot."""
        size = CONTACT_PHOTO_SIZE
        
        if self.contact and self.contact.photo:
            try:
                image_data = base64.b64decode(self.contact.photo)
                image = Image.open(io.BytesIO(image_data))
                image = image.resize(size, Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=image, dark_image=image, size=size)
                self.photo_label.configure(image=photo, text="")
                return
            except Exception:
                pass
        
        # Default avatar
        image = Image.new('RGBA', size, Theme.BG_HOVER)
        draw = ImageDraw.Draw(image)
        
        # Cirkel
        padding = 10
        draw.ellipse(
            [padding, padding, size[0]-padding, size[1]-padding],
            fill=Theme.BG_SELECTED,
            outline=Theme.BORDER
        )
        
        # Initialer
        initials = self._get_initials()
        
        # Stor text
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("segoeui.ttf", 48)
        except Exception:
            font = None
        
        if font:
            text_bbox = draw.textbbox((0, 0), initials, font=font)
        else:
            text_bbox = draw.textbbox((0, 0), initials)
        
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2 - 5
        
        draw.text((x, y), initials, fill=Theme.ACCENT_GOLD, font=font)
        
        photo = ctk.CTkImage(light_image=image, dark_image=image, size=size)
        self.photo_label.configure(image=photo, text="")
    
    def _get_initials(self) -> str:
        """Returnerar initialer."""
        if not self.contact or not self.contact.name:
            return "?"
        
        name = self.contact.name.strip()
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[0].upper()
    
    def _update_info(self):
        """Uppdaterar kontaktinformation."""
        # Rensa befintlig info
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        if not self.contact:
            return
        
        info_padding = {"padx": 15, "pady": 8}
        
        # Telefon
        for phone in self.contact.phones:
            self._add_info_row(
                "📱" if phone.type == "mobile" else "📞",
                "Telefon:",
                phone.number,
                self._copy_phone,
                phone.number
            )
        
        # E-post
        for email in self.contact.emails:
            self._add_info_row(
                "✉",
                "E-post:",
                email.address,
                self._open_email,
                email.address
            )
        
        # Adress (visa om någon del finns)
        has_address = self.contact.street or self.contact.postal_code or self.contact.city
        if has_address:
            # Bygg adresstext
            addr_parts = []
            if self.contact.street:
                addr_parts.append(self.contact.street)
            
            postal_city = []
            if self.contact.postal_code:
                postal_city.append(self.contact.postal_code)
            if self.contact.city:
                postal_city.append(self.contact.city)
            if postal_city:
                addr_parts.append(" ".join(postal_city))
            
            if self.contact.country:
                addr_parts.append(self.contact.country)
            
            full_address = ", ".join(addr_parts)
            
            self._add_info_row(
                "📍",
                "Adress:",
                full_address,
                self._open_map,
                full_address
            )
        
        # Företag
        if self.contact.company:
            self._add_info_row(
                "🏢",
                "Företag:",
                self.contact.company
            )
        
        # Födelsedag
        if self.contact.birthday:
            self._add_info_row(
                "🎂",
                "Födelsedag:",
                self.contact.birthday
            )
        
        # Sociala medier
        if self.contact.social_media:
            # Separator
            sep = ctk.CTkFrame(self.info_frame, height=1, fg_color=Theme.BORDER)
            sep.pack(fill="x", padx=15, pady=10)
            
            for sm in self.contact.social_media:
                self._add_info_row(
                    sm.get_icon(),
                    f"{sm.platform.capitalize()}:",
                    sm.username,
                    self._open_social,
                    sm
                )
    
    def _add_info_row(
        self,
        icon: str,
        label: str,
        value: str,
        on_click: Optional[Callable] = None,
        click_data: Optional[str] = None
    ):
        """Lägger till en info-rad."""
        row = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=8)
        
        # Ikon och etikett
        ctk.CTkLabel(
            row,
            text=f"{icon}  {label}",
            font=Theme.get_font("normal"),
            text_color=Theme.TEXT_MUTED,
            width=100,
            anchor="w"
        ).pack(side="left")
        
        # Värde (klickbar om on_click finns)
        if on_click:
            value_label = ctk.CTkLabel(
                row,
                text=value,
                font=Theme.get_font("normal"),
                text_color=Theme.ACCENT_GOLD,
                anchor="w",
                cursor="hand2"
            )
            value_label.pack(side="left", fill="x", expand=True)
            value_label.bind("<Button-1>", lambda e, d=click_data: on_click(d))
            value_label.bind("<Enter>", lambda e: value_label.configure(
                font=Theme.get_font("normal", bold=False)
            ))
        else:
            ctk.CTkLabel(
                row,
                text=value,
                font=Theme.get_font("normal"),
                text_color=Theme.TEXT_PRIMARY,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
    
    def _update_tags(self):
        """Uppdaterar taggvisning."""
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        
        if not self.contact or not self.contact.tags:
            return
        
        ctk.CTkLabel(
            self.tags_frame,
            text="Taggar:",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        tags_container = ctk.CTkFrame(self.tags_frame, fg_color="transparent")
        tags_container.pack(fill="x")
        
        for tag in self.contact.tags:
            tag_label = ctk.CTkLabel(
                tags_container,
                text=f" {tag} ",
                font=Theme.get_font("small"),
                text_color=Theme.BG_DARK,
                fg_color=Theme.ACCENT_GOLD,
                corner_radius=4
            )
            tag_label.pack(side="left", padx=(0, 5), pady=2)
    
    def _update_notes(self):
        """Uppdaterar anteckningar."""
        for widget in self.notes_frame.winfo_children():
            widget.destroy()
        
        if not self.contact or not self.contact.notes:
            self.notes_frame.pack_forget()
            return
        
        self.notes_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            self.notes_frame,
            text="📝 Anteckningar",
            font=Theme.get_font("normal", bold=True),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        ).pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            self.notes_frame,
            text=self.contact.notes,
            font=Theme.get_font("normal"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
            justify="left",
            wraplength=400
        ).pack(fill="x", padx=15, pady=(0, 10))
    
    def _toggle_favorite(self):
        """Växlar favorit-status."""
        if self.contact:
            self.contact.is_favorite = not self.contact.is_favorite
            self.show_contact(self.contact)
            # Trigga uppdatering (hanteras av huvudfönstret)
            if hasattr(self, '_on_favorite_changed'):
                self._on_favorite_changed(self.contact)
    
    def set_favorite_callback(self, callback: Callable[[Contact], None]):
        """Sätter callback för favorit-ändring."""
        self._on_favorite_changed = callback
    
    def _copy_phone(self, phone: str):
        """Visar meny för telefonnummer med alternativ."""
        self._show_phone_menu(phone)
    
    def _show_phone_menu(self, phone: str):
        """Visar popup-meny med telefon-alternativ."""
        # Stäng eventuell befintlig meny
        if hasattr(self, '_active_menu') and self._active_menu:
            try:
                self._active_menu.destroy()
            except:
                pass
            self._active_menu = None
        
        if hasattr(self, '_menu_overlay') and self._menu_overlay:
            try:
                self._menu_overlay.destroy()
            except:
                pass
            self._menu_overlay = None
        
        # Skapa osynlig overlay som täcker skärmen
        overlay = ctk.CTkToplevel(self)
        self._menu_overlay = overlay
        overlay.title("")
        overlay.attributes("-alpha", 0.01)  # Nästan osynlig
        overlay.attributes("-topmost", True)
        overlay.overrideredirect(True)
        
        # Täck hela skärmen
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        overlay.geometry(f"{screen_w}x{screen_h}+0+0")
        
        # Skapa menyn
        menu = ctk.CTkToplevel(self)
        self._active_menu = menu
        menu.title("")
        menu.geometry("220x200")
        menu.overrideredirect(True)
        menu.configure(fg_color=Theme.BG_MEDIUM)
        menu.attributes("-topmost", True)
        
        # Positionera vid muspekare
        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        menu.geometry(f"+{x}+{y}")
        
        # Rensa telefonnummer för URL:er
        clean_phone = phone.replace(" ", "").replace("-", "")
        if not clean_phone.startswith("+"):
            clean_phone = phone  # Behåll original om inget +
        
        def close_all(event=None):
            try:
                if self._active_menu:
                    self._active_menu.destroy()
                    self._active_menu = None
                if self._menu_overlay:
                    self._menu_overlay.destroy()
                    self._menu_overlay = None
            except:
                pass
        
        # Klick på overlay stänger allt
        overlay.bind("<Button-1>", close_all)
        
        options = [
            ("📋 Kopiera nummer", lambda: self._do_copy_phone(phone, menu)),
            ("✈️ Öppna i Telegram", lambda: self._open_telegram(clean_phone, menu)),
            ("💬 Öppna i WhatsApp", lambda: self._open_whatsapp(clean_phone, menu)),
            ("🔒 Öppna i Signal", lambda: self._open_signal(clean_phone, menu)),
            ("📞 Ring (om möjligt)", lambda: self._call_phone(phone, menu)),
        ]
        
        for text, command in options:
            btn = ctk.CTkButton(
                menu,
                text=text,
                anchor="w",
                height=36,
                fg_color="transparent",
                hover_color=Theme.BG_HOVER,
                text_color=Theme.TEXT_PRIMARY,
                font=Theme.get_font("normal"),
                command=lambda c=command: (close_all(), c())
            )
            btn.pack(fill="x", padx=5, pady=2)
        
        menu.bind("<Escape>", close_all)
        menu.lift()  # Säkerställ att menyn är ovanpå overlay
    
    def _do_copy_phone(self, phone: str, menu):
        """Kopierar telefonnummer och stänger meny."""
        try:
            self.clipboard_clear()
            self.clipboard_append(phone)
            menu.destroy()
            self._show_toast("Telefonnummer kopierat!")
        except Exception:
            menu.destroy()
    
    def _open_telegram(self, phone: str, menu):
        """Öppnar Telegram med numret."""
        menu.destroy()
        webbrowser.open(f"https://t.me/{phone.replace('+', '')}")
    
    def _open_whatsapp(self, phone: str, menu):
        """Öppnar WhatsApp med numret."""
        menu.destroy()
        clean = phone.replace("+", "").replace(" ", "").replace("-", "")
        webbrowser.open(f"https://wa.me/{clean}")
    
    def _open_signal(self, phone: str, menu):
        """Öppnar Signal med numret."""
        menu.destroy()
        webbrowser.open(f"https://signal.me/#p/{phone}")
    
    def _call_phone(self, phone: str, menu):
        """Försöker ringa numret via tel:-protokollet."""
        menu.destroy()
        webbrowser.open(f"tel:{phone}")
    
    def _open_social(self, sm: SocialMedia):
        """Öppnar social media-profil i webbläsare."""
        try:
            url = sm.get_url()
            webbrowser.open(url)
        except Exception:
            pass
    
    def _open_email(self, email: str):
        """Öppnar e-postklient."""
        try:
            webbrowser.open(f"mailto:{email}")
        except Exception:
            pass
    
    def _open_map(self, address: str):
        """Öppnar kartapp med adressen."""
        try:
            encoded = urllib.parse.quote(address)
            # Öppna i Google Maps (fungerar på alla plattformar)
            webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={encoded}")
        except Exception:
            pass
    
    def _show_toast(self, message: str):
        """Visar ett kort meddelande."""
        toast = ctk.CTkLabel(
            self,
            text=message,
            font=Theme.get_font("small"),
            text_color=Theme.BG_DARK,
            fg_color=Theme.ACCENT_GOLD,
            corner_radius=6
        )
        toast.place(relx=0.5, rely=0.9, anchor="center")
        self.after(1500, toast.destroy)
    
    def _on_edit(self):
        if self.contact:
            self.on_edit(self.contact)
    
    def _on_delete(self):
        if self.contact:
            self.on_delete(self.contact)
    
    def _on_export(self):
        if self.contact:
            self.on_export(self.contact)
    
    def clear(self):
        """Rensar vyn."""
        self.contact = None
        self._show_empty_state()
