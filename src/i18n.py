"""
Internationalisering (i18n) för MinaKontakter.
Stöder svenska och engelska (brittisk).
"""

from typing import Dict

# Språkkoder
LANG_SWEDISH = "sv"
LANG_ENGLISH = "en"

# Tillgängliga språk
LANGUAGES = {
    LANG_SWEDISH: "Svenska",
    LANG_ENGLISH: "English (UK)",
}

# Översättningar
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # === Allmänt ===
    "app_title": {
        "sv": "MinaKontakter",
        "en": "My Contacts",
    },
    "ok": {
        "sv": "OK",
        "en": "OK",
    },
    "cancel": {
        "sv": "Avbryt",
        "en": "Cancel",
    },
    "save": {
        "sv": "Spara",
        "en": "Save",
    },
    "close": {
        "sv": "Stäng",
        "en": "Close",
    },
    "delete": {
        "sv": "Radera",
        "en": "Delete",
    },
    "edit": {
        "sv": "Redigera",
        "en": "Edit",
    },
    "new": {
        "sv": "Ny",
        "en": "New",
    },
    "search": {
        "sv": "Sök...",
        "en": "Search...",
    },
    "yes": {
        "sv": "Ja",
        "en": "Yes",
    },
    "no": {
        "sv": "Nej",
        "en": "No",
    },
    
    # === Setup/Login ===
    "create_new_database": {
        "sv": "Skapa ny databas",
        "en": "Create new database",
    },
    "open_existing_database": {
        "sv": "Öppna befintlig databas",
        "en": "Open existing database",
    },
    "database_location": {
        "sv": "Databas-plats:",
        "en": "Database location:",
    },
    "backup_location": {
        "sv": "Backup-plats:",
        "en": "Backup location:",
    },
    "choose": {
        "sv": "Välj...",
        "en": "Choose...",
    },
    "password": {
        "sv": "Lösenord",
        "en": "Password",
    },
    "confirm_password": {
        "sv": "Bekräfta lösenord",
        "en": "Confirm password",
    },
    "show_password": {
        "sv": "Visa lösenord",
        "en": "Show password",
    },
    "language": {
        "sv": "Språk:",
        "en": "Language:",
    },
    "password_requirements": {
        "sv": "Minst 1 bokstav och 1 siffra",
        "en": "At least 1 letter and 1 digit",
    },
    "passwords_dont_match": {
        "sv": "Lösenorden matchar inte",
        "en": "Passwords do not match",
    },
    "wrong_password": {
        "sv": "Fel lösenord",
        "en": "Wrong password",
    },
    "unlock_database": {
        "sv": "Lås upp databas",
        "en": "Unlock database",
    },
    
    # === Kontakt ===
    "contact": {
        "sv": "Kontakt",
        "en": "Contact",
    },
    "contacts": {
        "sv": "Kontakter",
        "en": "Contacts",
    },
    "new_contact": {
        "sv": "Ny kontakt",
        "en": "New contact",
    },
    "edit_contact": {
        "sv": "Redigera kontakt",
        "en": "Edit contact",
    },
    "delete_contact": {
        "sv": "Radera kontakt",
        "en": "Delete contact",
    },
    "name": {
        "sv": "Namn",
        "en": "Name",
    },
    "name_required": {
        "sv": "Namn är obligatoriskt",
        "en": "Name is required",
    },
    "phone": {
        "sv": "Telefon",
        "en": "Phone",
    },
    "email": {
        "sv": "E-post",
        "en": "Email",
    },
    "address": {
        "sv": "Adress",
        "en": "Address",
    },
    "street": {
        "sv": "Gatuadress",
        "en": "Street",
    },
    "postal_code": {
        "sv": "Postnummer",
        "en": "Postal code",
    },
    "city": {
        "sv": "Ort",
        "en": "City",
    },
    "country": {
        "sv": "Land",
        "en": "Country",
    },
    "company": {
        "sv": "Företag",
        "en": "Company",
    },
    "title": {
        "sv": "Titel",
        "en": "Title",
    },
    "birthday": {
        "sv": "Födelsedag",
        "en": "Birthday",
    },
    "notes": {
        "sv": "Anteckningar",
        "en": "Notes",
    },
    "tags": {
        "sv": "Taggar",
        "en": "Tags",
    },
    "favourite": {
        "sv": "Favorit",
        "en": "Favourite",
    },
    "mark_as_favourite": {
        "sv": "Markera som favorit",
        "en": "Mark as favourite",
    },
    "photo": {
        "sv": "Foto",
        "en": "Photo",
    },
    "choose_photo": {
        "sv": "Välj bild",
        "en": "Choose photo",
    },
    "remove_photo": {
        "sv": "Ta bort bild",
        "en": "Remove photo",
    },
    
    # === Telefon-typer ===
    "mobile": {
        "sv": "Mobil",
        "en": "Mobile",
    },
    "home": {
        "sv": "Hem",
        "en": "Home",
    },
    "work": {
        "sv": "Arbete",
        "en": "Work",
    },
    "other": {
        "sv": "Annan",
        "en": "Other",
    },
    "personal": {
        "sv": "Privat",
        "en": "Personal",
    },
    
    # === Sociala medier ===
    "social_media": {
        "sv": "Sociala medier",
        "en": "Social media",
    },
    
    # === Telefon-meny ===
    "copy_number": {
        "sv": "Kopiera nummer",
        "en": "Copy number",
    },
    "open_in_telegram": {
        "sv": "Öppna i Telegram",
        "en": "Open in Telegram",
    },
    "open_in_whatsapp": {
        "sv": "Öppna i WhatsApp",
        "en": "Open in WhatsApp",
    },
    "open_in_signal": {
        "sv": "Öppna i Signal",
        "en": "Open in Signal",
    },
    "call": {
        "sv": "Ring",
        "en": "Call",
    },
    "number_copied": {
        "sv": "Telefonnummer kopierat!",
        "en": "Phone number copied!",
    },
    
    # === Import/Export ===
    "import": {
        "sv": "Importera",
        "en": "Import",
    },
    "export": {
        "sv": "Exportera",
        "en": "Export",
    },
    "import_csv": {
        "sv": "Importera från CSV",
        "en": "Import from CSV",
    },
    "export_csv": {
        "sv": "Exportera till CSV",
        "en": "Export to CSV",
    },
    "import_success": {
        "sv": "kontakter importerade",
        "en": "contacts imported",
    },
    "export_success": {
        "sv": "kontakter exporterade",
        "en": "contacts exported",
    },
    
    # === Backup ===
    "backup": {
        "sv": "Backup",
        "en": "Backup",
    },
    "create_backup": {
        "sv": "Skapa backup",
        "en": "Create backup",
    },
    "restore_backup": {
        "sv": "Återställ backup",
        "en": "Restore backup",
    },
    "backup_created": {
        "sv": "Backup skapad",
        "en": "Backup created",
    },
    
    # === Meny ===
    "file": {
        "sv": "Arkiv",
        "en": "File",
    },
    "settings": {
        "sv": "Inställningar",
        "en": "Settings",
    },
    "help": {
        "sv": "Hjälp",
        "en": "Help",
    },
    "about": {
        "sv": "Om",
        "en": "About",
    },
    "quit": {
        "sv": "Avsluta",
        "en": "Quit",
    },
    
    # === Bekräftelser ===
    "confirm_delete": {
        "sv": "Är du säker på att du vill radera denna kontakt?",
        "en": "Are you sure you want to delete this contact?",
    },
    "confirm_quit": {
        "sv": "Vill du avsluta?",
        "en": "Do you want to quit?",
    },
    
    # === Lösenordsstyrka ===
    "strength_very_weak": {
        "sv": "Mycket svagt",
        "en": "Very weak",
    },
    "strength_weak": {
        "sv": "Svagt",
        "en": "Weak",
    },
    "strength_fair": {
        "sv": "Okej",
        "en": "Fair",
    },
    "strength_good": {
        "sv": "Bra",
        "en": "Good",
    },
    "strength_strong": {
        "sv": "Starkt",
        "en": "Strong",
    },
}


class I18n:
    """Hanterare för översättningar."""
    
    _current_language: str = LANG_SWEDISH
    
    @classmethod
    def set_language(cls, lang: str):
        """Sätter aktuellt språk."""
        if lang in LANGUAGES:
            cls._current_language = lang
    
    @classmethod
    def get_language(cls) -> str:
        """Returnerar aktuellt språk."""
        return cls._current_language
    
    @classmethod
    def t(cls, key: str) -> str:
        """Översätter en nyckel till aktuellt språk."""
        if key in TRANSLATIONS:
            return TRANSLATIONS[key].get(cls._current_language, TRANSLATIONS[key].get("sv", key))
        return key
    
    @classmethod
    def get_available_languages(cls) -> dict:
        """Returnerar tillgängliga språk."""
        return LANGUAGES.copy()


# Kortform för översättning
def t(key: str) -> str:
    """Översätter en nyckel till aktuellt språk."""
    return I18n.t(key)
