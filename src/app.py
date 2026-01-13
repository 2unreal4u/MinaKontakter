"""
KontaktRegister - Huvudapplikation
Hanterar uppstart, login och databasval.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Konfigurera loggning
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

from config import (
    APP_NAME, APP_VERSION,
    DEFAULT_DB_DIR, DEFAULT_DB_NAME, DEFAULT_BACKUP_DIR,
    WINDOW_WIDTH, WINDOW_HEIGHT
)
from database.db_manager import DatabaseManager
from ui.theme import Theme
from ui.dialogs import SetupDialog, LoginDialog
from ui.main_window import MainWindow


class AppLauncher:
    """
    Hanterar applikationens uppstart.
    Visar antingen login-dialog eller setup-dialog beroende på om
    det finns en befintlig databas.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.config_file = Path(os.path.expanduser("~")) / ".kontaktregister"
        self.last_db_path: Optional[str] = None
        
        # Ladda senast använda databas
        self._load_last_db()
    
    def _load_last_db(self):
        """Laddar sökväg till senast använda databas."""
        try:
            if self.config_file.exists():
                self.last_db_path = self.config_file.read_text().strip()
                if self.last_db_path and not Path(self.last_db_path).exists():
                    self.last_db_path = None
        except Exception as e:
            logger.warning(f"Kunde inte ladda senaste databas: {e}")
    
    def _save_last_db(self, path: str):
        """Sparar sökväg till senast använda databas."""
        try:
            self.config_file.write_text(path)
            self.last_db_path = path
        except Exception as e:
            logger.warning(f"Kunde inte spara databasväg: {e}")
    
    def run(self):
        """Startar applikationen."""
        # Konfigurera CTk
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Skapa rotfönster (dold)
        root = ctk.CTk()
        root.withdraw()
        
        # Centrera
        root.update_idletasks()
        
        # Visa rätt dialog baserat på om databas finns
        if self.last_db_path and Path(self.last_db_path).exists():
            self._show_login(root)
        else:
            self._show_startup_choice(root)
        
        root.mainloop()
    
    def _show_startup_choice(self, root: ctk.CTk):
        """Visar val mellan att skapa ny eller öppna befintlig databas."""
        dialog = StartupChoiceDialog(
            root,
            on_new=lambda: self._on_new_database(root, dialog),
            on_open=lambda: self._on_open_existing(root, dialog)
        )
    
    def _on_new_database(self, root: ctk.CTk, startup_dialog):
        """Hanterar skapande av ny databas."""
        startup_dialog.destroy()
        
        def on_setup_complete(db_path: str, backup_path: str, password: str, language: str):
            # Sätt språk
            from i18n import I18n
            I18n.set_language(language)
            
            success, error = self.db_manager.create_database(db_path, backup_path, password, language)
            
            if success:
                self._save_last_db(db_path)
                root.destroy()
                self._launch_main_window()
            else:
                messagebox.showerror("Fel", f"Kunde inte skapa databas:\n{error}")
                self._show_startup_choice(root)
        
        SetupDialog(root, on_setup_complete)
    
    def _on_open_existing(self, root: ctk.CTk, startup_dialog):
        """Hanterar öppnande av befintlig databas."""
        startup_dialog.destroy()
        
        file_path = filedialog.askopenfilename(
            title="Öppna databas",
            filetypes=[
                ("KontaktRegister databas", "*.krdb"),
                ("Alla filer", "*.*")
            ]
        )
        
        if file_path:
            self.last_db_path = file_path
            self._show_login(root)
        else:
            self._show_startup_choice(root)
    
    def _show_login(self, root: ctk.CTk):
        """Visar login-dialog."""
        login_dialog = None
        
        def on_login(password: str):
            success, error = self.db_manager.open_database(self.last_db_path, password)
            
            if success:
                self._save_last_db(self.last_db_path)
                if login_dialog:
                    login_dialog.destroy()
                root.destroy()
                self._launch_main_window()
            else:
                if login_dialog:
                    login_dialog.show_error(error)
        
        login_dialog = LoginDialog(root, self.last_db_path, on_login)
        
        # Hantera "Annan databas"-val
        def check_result():
            if login_dialog.result == "OTHER_DB":
                self.last_db_path = None
                self._show_startup_choice(root)
        
        login_dialog.bind("<Destroy>", lambda e: check_result())
    
    def _launch_main_window(self):
        """Startar huvudfönstret."""
        logger.info(f"Startar {APP_NAME} v{APP_VERSION}")
        
        main_window = MainWindow(self.db_manager)
        main_window.mainloop()


class StartupChoiceDialog(ctk.CTkToplevel):
    """Dialog för att välja mellan ny eller befintlig databas."""
    
    def __init__(self, parent, on_new, on_open):
        super().__init__(parent)
        
        self.on_new = on_new
        self.on_open = on_open
        
        # Fönsterinställningar
        self.title(APP_NAME)
        self.geometry("450x350")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_DARK)
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Centrera
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 350) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        # Hantera stängning
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Titel
        ctk.CTkLabel(
            main_frame,
            text=APP_NAME,
            font=("Segoe UI", 32, "bold"),
            text_color=Theme.ACCENT_GOLD
        ).pack(pady=(0, 5))
        
        # Undertitel
        ctk.CTkLabel(
            main_frame,
            text="Lokalt kontaktregister med krypterad databas",
            font=Theme.get_font("normal"),
            text_color=Theme.TEXT_SECONDARY
        ).pack(pady=(0, 30))
        
        # Välkommen-text
        ctk.CTkLabel(
            main_frame,
            text="Välkommen! Vad vill du göra?",
            font=Theme.get_font("heading"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(0, 25))
        
        # Knappar
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Ny databas
        new_btn = ctk.CTkButton(
            button_frame,
            text="🆕  Skapa ny databas",
            height=50,
            font=Theme.get_font("normal", bold=True),
            command=self.on_new,
            **Theme.get_button_colors()
        )
        new_btn.pack(fill="x", pady=(0, 15))
        
        # Öppna befintlig
        open_btn = ctk.CTkButton(
            button_frame,
            text="📂  Öppna befintlig databas",
            height=50,
            font=Theme.get_font("normal", bold=True),
            command=self.on_open,
            **Theme.get_secondary_button_colors()
        )
        open_btn.pack(fill="x")
        
        # Version
        ctk.CTkLabel(
            main_frame,
            text=f"Version {APP_VERSION}",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_MUTED
        ).pack(side="bottom", pady=(20, 0))
    
    def _on_close(self):
        """Avslutar applikationen vid stängning."""
        self.quit()
        sys.exit(0)


def main():
    """Entry point för applikationen."""
    try:
        launcher = AppLauncher()
        launcher.run()
    except Exception as e:
        logger.exception(f"Kritiskt fel: {e}")
        messagebox.showerror("Kritiskt fel", f"Ett oväntat fel uppstod:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
