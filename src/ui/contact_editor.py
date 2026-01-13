"""
Kontaktredigerare för KontaktRegister.
Dialog för att skapa/redigera kontakter.
"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Optional, Callable
from PIL import Image
import base64
import io

from ui.theme import Theme
from database.models import Contact, PhoneNumber, EmailAddress, SocialMedia
from config import CONTACT_PHOTO_SIZE

# Sociala medier-plattformar
SOCIAL_PLATFORMS = [
    ("LinkedIn", "linkedin"),
    ("Twitter/X", "twitter"),
    ("Facebook", "facebook"),
    ("Instagram", "instagram"),
    ("GitHub", "github"),
    ("Telegram", "telegram"),
    ("WhatsApp", "whatsapp"),
    ("Signal", "signal"),
    ("Webbsida", "website"),
]


class ContactEditorDialog(ctk.CTkToplevel):
    """Dialog för att skapa eller redigera en kontakt."""
    
    def __init__(
        self,
        parent,
        contact: Optional[Contact] = None,
        on_save: Optional[Callable[[Contact], None]] = None,
        existing_tags: Optional[list[str]] = None
    ):
        super().__init__(parent)
        
        self.contact = contact or Contact()
        self.is_new = contact is None
        self.on_save = on_save
        self.existing_tags = existing_tags or []
        self.result: Optional[Contact] = None
        self.photo_data: Optional[str] = self.contact.photo
        
        # Fönsterinställningar
        title = "Ny kontakt" if self.is_new else "Redigera kontakt"
        self.title(title)
        self.geometry("600x700")
        self.minsize(500, 600)
        self.configure(fg_color=Theme.BG_DARK)
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Centrera
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 600) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        self._populate_fields()
    
    def _create_widgets(self):
        # Huvudcontainer med scrollning
        main_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Theme.BG_HOVER,
            scrollbar_button_hover_color=Theme.BORDER
        )
        main_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # === Foto ===
        photo_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        photo_frame.pack(fill="x", pady=(0, 20))
        
        self.photo_container = ctk.CTkFrame(
            photo_frame,
            fg_color=Theme.BG_MEDIUM,
            corner_radius=12,
            width=120,
            height=120
        )
        self.photo_container.pack(side="left")
        self.photo_container.pack_propagate(False)
        
        self.photo_label = ctk.CTkLabel(
            self.photo_container,
            text="Ingen bild",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_MUTED,
            width=110,
            height=110
        )
        self.photo_label.pack(expand=True, padx=5, pady=5)
        
        photo_buttons = ctk.CTkFrame(photo_frame, fg_color="transparent")
        photo_buttons.pack(side="left", padx=(15, 0))
        
        ctk.CTkButton(
            photo_buttons,
            text="Välj bild...",
            width=100,
            height=32,
            font=Theme.get_font("small"),
            command=self._choose_photo,
            **Theme.get_secondary_button_colors()
        ).pack(pady=(0, 5))
        
        ctk.CTkButton(
            photo_buttons,
            text="Ta bort bild",
            width=100,
            height=32,
            font=Theme.get_font("small"),
            command=self._remove_photo,
            **Theme.get_secondary_button_colors()
        ).pack()
        
        # === Grundinfo ===
        self._create_section(main_scroll, "Grundinformation")
        
        # Namn
        self.name_entry = self._create_field(main_scroll, "Namn *", "Fullständigt namn")
        
        # Företag
        self.company_entry = self._create_field(main_scroll, "Företag", "Företagsnamn")
        
        # Titel/Roll
        self.title_entry = self._create_field(main_scroll, "Titel/Roll", "T.ex. VD, Utvecklare")
        
        # === Kontaktinfo ===
        self._create_section(main_scroll, "Kontaktinformation")
        
        # Telefon 1
        phone_frame1 = ctk.CTkFrame(main_scroll, fg_color="transparent")
        phone_frame1.pack(fill="x", pady=(0, 10))
        
        self.phone1_entry = self._create_field(
            phone_frame1, "Telefon 1", "+46 70 123 45 67", pack=False
        )
        self.phone1_entry.pack(side="left", fill="x", expand=True)
        
        self.phone1_type = ctk.CTkComboBox(
            phone_frame1,
            values=["Mobil", "Hem", "Arbete", "Annan"],
            width=100,
            height=38,
            font=Theme.get_font("normal"),
            fg_color=Theme.BG_MEDIUM,
            border_color=Theme.BORDER,
            button_color=Theme.BG_HOVER,
            button_hover_color=Theme.BORDER,
            dropdown_fg_color=Theme.BG_MEDIUM,
            dropdown_hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY
        )
        self.phone1_type.pack(side="right", padx=(10, 0))
        self.phone1_type.set("Mobil")
        
        # Telefon 2
        phone_frame2 = ctk.CTkFrame(main_scroll, fg_color="transparent")
        phone_frame2.pack(fill="x", pady=(0, 10))
        
        self.phone2_entry = self._create_field(
            phone_frame2, "Telefon 2", "Ytterligare nummer", pack=False
        )
        self.phone2_entry.pack(side="left", fill="x", expand=True)
        
        self.phone2_type = ctk.CTkComboBox(
            phone_frame2,
            values=["Mobil", "Hem", "Arbete", "Annan"],
            width=100,
            height=38,
            font=Theme.get_font("normal"),
            fg_color=Theme.BG_MEDIUM,
            border_color=Theme.BORDER,
            button_color=Theme.BG_HOVER,
            button_hover_color=Theme.BORDER,
            dropdown_fg_color=Theme.BG_MEDIUM,
            dropdown_hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY
        )
        self.phone2_type.pack(side="right", padx=(10, 0))
        self.phone2_type.set("Hem")
        
        # E-post 1
        email_frame1 = ctk.CTkFrame(main_scroll, fg_color="transparent")
        email_frame1.pack(fill="x", pady=(0, 10))
        
        self.email1_entry = self._create_field(
            email_frame1, "E-post 1", "namn@example.com", pack=False
        )
        self.email1_entry.pack(side="left", fill="x", expand=True)
        
        self.email1_type = ctk.CTkComboBox(
            email_frame1,
            values=["Privat", "Arbete", "Annan"],
            width=100,
            height=38,
            font=Theme.get_font("normal"),
            fg_color=Theme.BG_MEDIUM,
            border_color=Theme.BORDER,
            button_color=Theme.BG_HOVER,
            button_hover_color=Theme.BORDER,
            dropdown_fg_color=Theme.BG_MEDIUM,
            dropdown_hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY
        )
        self.email1_type.pack(side="right", padx=(10, 0))
        self.email1_type.set("Privat")
        
        # E-post 2
        email_frame2 = ctk.CTkFrame(main_scroll, fg_color="transparent")
        email_frame2.pack(fill="x", pady=(0, 10))
        
        self.email2_entry = self._create_field(
            email_frame2, "E-post 2", "Ytterligare e-post", pack=False
        )
        self.email2_entry.pack(side="left", fill="x", expand=True)
        
        self.email2_type = ctk.CTkComboBox(
            email_frame2,
            values=["Privat", "Arbete", "Annan"],
            width=100,
            height=38,
            font=Theme.get_font("normal"),
            fg_color=Theme.BG_MEDIUM,
            border_color=Theme.BORDER,
            button_color=Theme.BG_HOVER,
            button_hover_color=Theme.BORDER,
            dropdown_fg_color=Theme.BG_MEDIUM,
            dropdown_hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY
        )
        self.email2_type.pack(side="right", padx=(10, 0))
        self.email2_type.set("Arbete")
        
        # === Adress ===
        self._create_section(main_scroll, "Adress")
        
        self.street_entry = self._create_field(
            main_scroll, "Gatuadress", "Storgatan 1"
        )
        
        # Postnr och ort på samma rad
        postal_city_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        postal_city_frame.pack(fill="x", pady=(0, 10))
        
        postal_frame = ctk.CTkFrame(postal_city_frame, fg_color="transparent")
        postal_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(
            postal_frame,
            text="Postnummer",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        ).pack(fill="x")
        
        self.postal_entry = ctk.CTkEntry(
            postal_frame,
            placeholder_text="123 45",
            width=100,
            **Theme.get_entry_colors(),
            height=38
        )
        self.postal_entry.pack(fill="x", pady=(5, 0))
        
        city_frame = ctk.CTkFrame(postal_city_frame, fg_color="transparent")
        city_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(
            city_frame,
            text="Ort",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        ).pack(fill="x")
        
        self.city_entry = ctk.CTkEntry(
            city_frame,
            placeholder_text="Stockholm",
            **Theme.get_entry_colors(),
            height=38
        )
        self.city_entry.pack(fill="x", pady=(5, 0))
        
        self.country_entry = self._create_field(
            main_scroll, "Land (valfritt)", "Sverige"
        )
        
        # === Övrigt ===
        self._create_section(main_scroll, "Övrigt")
        
        # Födelsedag
        self.birthday_entry = self._create_field(
            main_scroll, "Födelsedag", "ÅÅÅÅ-MM-DD"
        )
        
        # Taggar
        tags_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        tags_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            tags_frame,
            text="Taggar (kommaseparerade):",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        ).pack(fill="x")
        
        self.tags_entry = ctk.CTkEntry(
            tags_frame,
            placeholder_text="kund, vip, vän",
            **Theme.get_entry_colors(),
            height=38
        )
        self.tags_entry.pack(fill="x", pady=(5, 0))
        
        # Befintliga taggar som förslag
        if self.existing_tags:
            tags_hint = ctk.CTkLabel(
                tags_frame,
                text=f"Befintliga: {', '.join(self.existing_tags[:10])}",
                font=Theme.get_font("small"),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            )
            tags_hint.pack(fill="x", pady=(2, 0))
        
        # === Sociala medier ===
        self._create_section(main_scroll, "Sociala medier")
        
        self.social_entries = []
        for i, (label, platform) in enumerate(SOCIAL_PLATFORMS[:5]):  # Visa 5 i MVP
            social_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
            social_frame.pack(fill="x", pady=(0, 8))
            
            ctk.CTkLabel(
                social_frame,
                text=f"{SocialMedia(platform, '').get_icon()} {label}:",
                font=Theme.get_font("small"),
                text_color=Theme.TEXT_SECONDARY,
                width=100,
                anchor="w"
            ).pack(side="left")
            
            entry = ctk.CTkEntry(
                social_frame,
                placeholder_text=f"Användarnamn eller URL",
                **Theme.get_entry_colors(),
                height=34
            )
            entry.pack(side="left", fill="x", expand=True)
            self.social_entries.append((platform, entry))
        
        # Favorit
        self.favorite_var = ctk.BooleanVar(value=self.contact.is_favorite)
        ctk.CTkCheckBox(
            main_scroll,
            text="Markera som favorit",
            variable=self.favorite_var,
            fg_color=Theme.ACCENT_GOLD,
            hover_color=Theme.ACCENT_GOLD_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            font=Theme.get_font("normal")
        ).pack(anchor="w", pady=(0, 15))
        
        # === Anteckningar ===
        self._create_section(main_scroll, "Anteckningar")
        
        self.notes_text = ctk.CTkTextbox(
            main_scroll,
            height=100,
            font=Theme.get_font("normal"),
            fg_color=Theme.BG_MEDIUM,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=8
        )
        self.notes_text.pack(fill="x", pady=(0, 15))
        
        # === Felmeddelande ===
        self.error_label = ctk.CTkLabel(
            main_scroll,
            text="",
            font=Theme.get_font("small"),
            text_color=Theme.ERROR
        )
        self.error_label.pack(fill="x", pady=(0, 10))
        
        # === Knappar ===
        button_frame = ctk.CTkFrame(self, fg_color=Theme.BG_DARK, height=60)
        button_frame.pack(fill="x", side="bottom")
        button_frame.pack_propagate(False)
        
        inner_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        inner_buttons.pack(expand=True, pady=10)
        
        ctk.CTkButton(
            inner_buttons,
            text="Avbryt",
            width=120,
            height=40,
            font=Theme.get_font("normal"),
            command=self._cancel,
            **Theme.get_secondary_button_colors()
        ).pack(side="left", padx=(0, 15))
        
        ctk.CTkButton(
            inner_buttons,
            text="Spara",
            width=120,
            height=40,
            font=Theme.get_font("normal"),
            command=self._save,
            **Theme.get_button_colors()
        ).pack(side="left")
    
    def _create_section(self, parent, title: str):
        """Skapar en sektionsrubrik."""
        ctk.CTkLabel(
            parent,
            text=title,
            font=Theme.get_font("heading", bold=True),
            text_color=Theme.ACCENT_GOLD,
            anchor="w"
        ).pack(fill="x", pady=(15, 10))
    
    def _create_field(
        self,
        parent,
        label: str,
        placeholder: str,
        pack: bool = True
    ) -> ctk.CTkEntry:
        """Skapar ett inmatningsfält med etikett."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        if pack:
            frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_SECONDARY,
            anchor="w"
        ).pack(fill="x")
        
        entry = ctk.CTkEntry(
            frame,
            placeholder_text=placeholder,
            **Theme.get_entry_colors(),
            height=38
        )
        entry.pack(fill="x", pady=(5, 0))
        
        if not pack:
            return frame
        return entry
    
    def _populate_fields(self):
        """Fyller i fälten med befintlig data."""
        if not self.contact:
            return
        
        # Namn
        if self.contact.name:
            self.name_entry.insert(0, self.contact.name)
        
        # Företag
        if self.contact.company:
            self.company_entry.insert(0, self.contact.company)
        
        # Titel
        if self.contact.title:
            self.title_entry.insert(0, self.contact.title)
        
        # Telefoner
        if len(self.contact.phones) > 0:
            self.phone1_entry.winfo_children()[1].insert(0, self.contact.phones[0].number)
            self._set_type_combo(self.phone1_type, self.contact.phones[0].type)
        
        if len(self.contact.phones) > 1:
            self.phone2_entry.winfo_children()[1].insert(0, self.contact.phones[1].number)
            self._set_type_combo(self.phone2_type, self.contact.phones[1].type)
        
        # E-post
        if len(self.contact.emails) > 0:
            self.email1_entry.winfo_children()[1].insert(0, self.contact.emails[0].address)
            self._set_email_type_combo(self.email1_type, self.contact.emails[0].type)
        
        if len(self.contact.emails) > 1:
            self.email2_entry.winfo_children()[1].insert(0, self.contact.emails[1].address)
            self._set_email_type_combo(self.email2_type, self.contact.emails[1].type)
        
        # Adress
        if self.contact.street:
            self.street_entry.insert(0, self.contact.street)
        if self.contact.postal_code:
            self.postal_entry.insert(0, self.contact.postal_code)
        if self.contact.city:
            self.city_entry.insert(0, self.contact.city)
        if self.contact.country:
            self.country_entry.insert(0, self.contact.country)
        
        # Födelsedag
        if self.contact.birthday:
            self.birthday_entry.insert(0, self.contact.birthday)
        
        # Taggar
        if self.contact.tags:
            self.tags_entry.insert(0, ", ".join(self.contact.tags))
        
        # Sociala medier
        for platform, entry in self.social_entries:
            for sm in self.contact.social_media:
                if sm.platform == platform:
                    entry.insert(0, sm.username)
                    break
        
        # Anteckningar
        if self.contact.notes:
            self.notes_text.insert("1.0", self.contact.notes)
        
        # Foto
        self._update_photo_preview()
    
    def _set_type_combo(self, combo: ctk.CTkComboBox, type_value: str):
        """Sätter värde i telefon-typ combobox."""
        type_map = {"mobile": "Mobil", "home": "Hem", "work": "Arbete", "other": "Annan"}
        combo.set(type_map.get(type_value, "Mobil"))
    
    def _set_email_type_combo(self, combo: ctk.CTkComboBox, type_value: str):
        """Sätter värde i e-post-typ combobox."""
        type_map = {"personal": "Privat", "work": "Arbete", "other": "Annan"}
        combo.set(type_map.get(type_value, "Privat"))
    
    def _get_phone_type(self, combo: ctk.CTkComboBox) -> str:
        """Hämtar telefon-typ från combobox."""
        type_map = {"Mobil": "mobile", "Hem": "home", "Arbete": "work", "Annan": "other"}
        return type_map.get(combo.get(), "mobile")
    
    def _get_email_type(self, combo: ctk.CTkComboBox) -> str:
        """Hämtar e-post-typ från combobox."""
        type_map = {"Privat": "personal", "Arbete": "work", "Annan": "other"}
        return type_map.get(combo.get(), "personal")
    
    def _choose_photo(self):
        """Öppnar filväljare för foto."""
        file_path = filedialog.askopenfilename(
            title="Välj bild",
            filetypes=[
                ("Bilder", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("Alla filer", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Ladda och skala om bilden
                image = Image.open(file_path)
                image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Konvertera till RGB om RGBA
                if image.mode == 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[3])
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Spara som base64
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=85)
                self.photo_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                self._update_photo_preview()
                
            except Exception as e:
                self.error_label.configure(text=f"Kunde inte ladda bild: {e}")
    
    def _remove_photo(self):
        """Tar bort foto."""
        self.photo_data = None
        self._update_photo_preview()
    
    def _update_photo_preview(self):
        """Uppdaterar fotot i förhandsvisningen."""
        if self.photo_data:
            try:
                image_data = base64.b64decode(self.photo_data)
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((110, 110), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=image, dark_image=image, size=(110, 110))
                self.photo_label.configure(image=photo, text="")
            except Exception:
                self.photo_label.configure(image=None, text="Fel vid laddning")
        else:
            self.photo_label.configure(image=None, text="Ingen bild")
    
    def _get_entry_value(self, widget) -> str:
        """Hämtar värde från entry (hanterar frame-wrapper)."""
        if isinstance(widget, ctk.CTkFrame):
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkEntry):
                    return child.get().strip()
        elif isinstance(widget, ctk.CTkEntry):
            return widget.get().strip()
        return ""
    
    def _validate(self) -> Optional[str]:
        """Validerar formuläret."""
        name = self.name_entry.get().strip()
        
        if not name:
            return "Namn är obligatoriskt"
        
        return None
    
    def _save(self):
        """Sparar kontakten."""
        error = self._validate()
        if error:
            self.error_label.configure(text=error)
            return
        
        # Samla in data
        self.contact.name = self.name_entry.get().strip()
        self.contact.company = self.company_entry.get().strip()
        self.contact.title = self.title_entry.get().strip()
        self.contact.street = self.street_entry.get().strip()
        self.contact.postal_code = self.postal_entry.get().strip()
        self.contact.city = self.city_entry.get().strip()
        self.contact.country = self.country_entry.get().strip()
        self.contact.birthday = self.birthday_entry.get().strip()
        self.contact.is_favorite = self.favorite_var.get()
        self.contact.photo = self.photo_data
        
        # Anteckningar
        self.contact.notes = self.notes_text.get("1.0", "end-1c").strip()
        
        # Telefoner
        self.contact.phones = []
        phone1 = self._get_entry_value(self.phone1_entry)
        if phone1:
            self.contact.phones.append(PhoneNumber(
                number=phone1,
                type=self._get_phone_type(self.phone1_type)
            ))
        phone2 = self._get_entry_value(self.phone2_entry)
        if phone2:
            self.contact.phones.append(PhoneNumber(
                number=phone2,
                type=self._get_phone_type(self.phone2_type)
            ))
        
        # E-post
        self.contact.emails = []
        email1 = self._get_entry_value(self.email1_entry)
        if email1:
            self.contact.emails.append(EmailAddress(
                address=email1,
                type=self._get_email_type(self.email1_type)
            ))
        email2 = self._get_entry_value(self.email2_entry)
        if email2:
            self.contact.emails.append(EmailAddress(
                address=email2,
                type=self._get_email_type(self.email2_type)
            ))
        
        # Taggar
        tags_str = self.tags_entry.get().strip()
        if tags_str:
            self.contact.tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        else:
            self.contact.tags = []
        
        # Sociala medier
        self.contact.social_media = []
        for platform, entry in self.social_entries:
            username = entry.get().strip()
            if username:
                self.contact.social_media.append(SocialMedia(
                    platform=platform,
                    username=username
                ))
        
        self.result = self.contact
        
        if self.on_save:
            self.on_save(self.contact)
        
        self.destroy()
    
    def _cancel(self):
        """Avbryter redigeringen."""
        self.result = None
        self.destroy()
    
    def get_result(self) -> Optional[Contact]:
        """Returnerar resultatet efter att dialogen stängts."""
        self.wait_window()
        return self.result
