"""
Konfiguration och konstanter för MinaKontakter.
"""

import os
from pathlib import Path

# Applikationsinfo
APP_NAME = "MinaKontakter"
APP_VERSION = "1.0.0"

# Standardsökvägar
DEFAULT_DB_NAME = "kontakter.krdb"
DEFAULT_BACKUP_SUFFIX = ".backup"
CONFIG_FILE_NAME = "minakontakter.conf"

# Användarens dokument-mapp som standard
USER_DOCUMENTS = Path(os.path.expanduser("~")) / "Documents"
DEFAULT_DB_DIR = USER_DOCUMENTS / "MinaKontakter"
DEFAULT_BACKUP_DIR = USER_DOCUMENTS / "MinaKontakter" / "backups"

# Lösenordskrav
PASSWORD_MIN_LENGTH = 7
PASSWORD_MAX_LENGTH = 16

# Krypteringsinställningar (Argon2id)
ARGON2_TIME_COST = 3          # Antal iterationer
ARGON2_MEMORY_COST = 65536    # 64 MB
ARGON2_PARALLELISM = 4        # Antal trådar
ARGON2_HASH_LEN = 32          # 256 bitar för AES-256
SALT_LENGTH = 16              # 128 bitar

# UI-tema (Navy Blue + Gul accent)
THEME = {
    "bg_dark": "#0a1628",           # Mörkaste bakgrund
    "bg_medium": "#132238",         # Medium bakgrund
    "bg_light": "#1a2d47",          # Ljusare bakgrund (paneler)
    "bg_hover": "#243a5e",          # Hover-effekt
    "bg_selected": "#2d4a6f",       # Vald item
    "accent_gold": "#d4a84b",       # Gul accent (text, knappar)
    "accent_gold_hover": "#e6bc5f", # Gul hover
    "accent_gold_dark": "#b8923f",  # Mörkare gul
    "text_primary": "#ffffff",      # Vit text
    "text_secondary": "#a0aec0",    # Grå text
    "text_muted": "#6b7c93",        # Dämpad text
    "border": "#2d4a6f",            # Ram/border
    "border_light": "#3d5a7f",      # Ljusare border
    "success": "#48bb78",           # Grön (success)
    "warning": "#ed8936",           # Orange (varning)
    "error": "#fc8181",             # Röd (fel)
}

# Fönsterstorlek
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 600

# Kontaktlista
CONTACT_LIST_WIDTH = 280
CONTACT_THUMBNAIL_SIZE = (40, 40)
CONTACT_PHOTO_SIZE = (150, 150)

# Backup-inställningar
AUTO_BACKUP_ON_CLOSE = True
BACKUP_KEEP_COUNT = 10  # Behåll max antal backups

# Loggning
LOG_FILE = "minakontakter.log"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3

# CSV-inställningar
CSV_ENCODING = "utf-8-sig"  # Med BOM för Excel-kompatibilitet
CSV_DELIMITER = ","

# Databas-version (för framtida migrering)
DB_VERSION = "1.0"
