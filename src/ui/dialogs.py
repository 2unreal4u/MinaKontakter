"""
Dialogrutor för KontaktRegister.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional, Callable

from ui.theme import Theme, PASSWORD_STRENGTH_COLORS
from crypto.encryption import PasswordValidator
from config import PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH
from i18n import I18n, LANGUAGES, LANG_SWEDISH


class SetupDialog(ctk.CTkToplevel):
    """
    Dialog för att skapa ny databas.
    Samlar in: databas-sökväg, backup-sökväg, lösenord, språk.
    """
    
    def __init__(self, parent, on_complete: Callable[[str, str, str, str], None]):
        super().__init__(parent)
        
        self.on_complete = on_complete  # (db_path, backup_path, password, language)
        self.result = None
        self.selected_language = LANG_SWEDISH
        
        # Fönsterinställningar
        self.title("Skapa ny databas")
        self.geometry("550x700")
        self.resizable(True, True)
        self.configure(fg_color=Theme.BG_DARK)
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Centrera
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 550) // 2
        y = (self.winfo_screenheight() - 620) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        # Fokus på första fältet
        self.db_path_entry.focus_set()
    
    def _create_widgets(self):
        # Scrollbar huvudcontainer
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title = ctk.CTkLabel(
            main_frame,
            text="Skapa ny databas",
            font=Theme.get_font("title", bold=True),
            text_color=Theme.ACCENT_GOLD
        )
        title.pack(pady=(0, 5))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Välj var din kontaktdatabas ska sparas",
            font=Theme.get_font("normal"),
            text_color=Theme.TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, 20))
        
        # Språkval
        lang_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        lang_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            lang_frame,
            text="🌐 Språk / Language:",
            font=Theme.get_font("normal", bold=True),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x")
        
        self.language_combo = ctk.CTkComboBox(
            lang_frame,
            values=list(LANGUAGES.values()),
            width=200,
            height=38,
            command=self._on_language_change,
            fg_color=Theme.BG_MEDIUM,
            border_color=Theme.BORDER,
            button_color=Theme.BG_HOVER,
            button_hover_color=Theme.BORDER,
            dropdown_fg_color=Theme.BG_MEDIUM,
            dropdown_hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY
        )
        self.language_combo.pack(fill="x", pady=(5, 0))
        self.language_combo.set("Svenska")  # Default
        
        # Databas-sökväg
        db_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        db_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            db_frame,
            text="Databas-plats:",
            font=Theme.get_font("normal", bold=True),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x")
        
        db_input_frame = ctk.CTkFrame(db_frame, fg_color="transparent")
        db_input_frame.pack(fill="x", pady=(5, 0))
        
        self.db_path_entry = ctk.CTkEntry(
            db_input_frame,
            placeholder_text="Välj plats för databasen...",
            **Theme.get_entry_colors(),
            height=38
        )
        self.db_path_entry.pack(side="left", fill="x", expand=True)
        
        ctk.CTkButton(
            db_input_frame,
            text="Välj...",
            width=80,
            height=38,
            command=self._browse_db_path,
            **Theme.get_secondary_button_colors()
        ).pack(side="right", padx=(10, 0))
        
        # Backup-sökväg
        backup_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        backup_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            backup_frame,
            text="Backup-plats:",
            font=Theme.get_font("normal", bold=True),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x")
        
        backup_input_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
        backup_input_frame.pack(fill="x", pady=(5, 0))
        
        self.backup_path_entry = ctk.CTkEntry(
            backup_input_frame,
            placeholder_text="Välj plats för backups...",
            **Theme.get_entry_colors(),
            height=38
        )
        self.backup_path_entry.pack(side="left", fill="x", expand=True)
        
        ctk.CTkButton(
            backup_input_frame,
            text="Välj...",
            width=80,
            height=38,
            command=self._browse_backup_path,
            **Theme.get_secondary_button_colors()
        ).pack(side="right", padx=(10, 0))
        
        # Lösenord
        pwd_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        pwd_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            pwd_frame,
            text=f"Lösenord ({PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} tecken):",
            font=Theme.get_font("normal", bold=True),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x")
        
        self.password_entry = ctk.CTkEntry(
            pwd_frame,
            placeholder_text="Minst 1 bokstav och 1 siffra",
            show="●",
            **Theme.get_entry_colors(),
            height=38
        )
        self.password_entry.pack(fill="x", pady=(5, 0))
        self.password_entry.bind("<KeyRelease>", self._update_strength)
        
        # Styrkeindikator
        strength_frame = ctk.CTkFrame(pwd_frame, fg_color="transparent")
        strength_frame.pack(fill="x", pady=(8, 0))
        
        self.strength_bars = []
        for i in range(5):
            bar = ctk.CTkFrame(
                strength_frame,
                height=4,
                fg_color=Theme.BG_HOVER,
                corner_radius=2
            )
            bar.pack(side="left", fill="x", expand=True, padx=1)
            self.strength_bars.append(bar)
        
        self.strength_label = ctk.CTkLabel(
            pwd_frame,
            text="",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        )
        self.strength_label.pack(fill="x", pady=(5, 0))
        
        # Bekräfta lösenord
        confirm_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        confirm_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            confirm_frame,
            text="Bekräfta lösenord:",
            font=Theme.get_font("normal", bold=True),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x")
        
        self.confirm_entry = ctk.CTkEntry(
            confirm_frame,
            placeholder_text="Skriv lösenordet igen",
            show="●",
            **Theme.get_entry_colors(),
            height=38
        )
        self.confirm_entry.pack(fill="x", pady=(5, 0))
        
        # Visa/dölj lösenord
        self.show_password_var = ctk.BooleanVar(value=False)
        show_check = ctk.CTkCheckBox(
            main_frame,
            text="Visa lösenord",
            variable=self.show_password_var,
            command=self._toggle_password_visibility,
            fg_color=Theme.ACCENT_GOLD,
            hover_color=Theme.ACCENT_GOLD_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            font=Theme.get_font("small")
        )
        show_check.pack(anchor="w", pady=(5, 15))
        
        # Felmeddelande
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=Theme.get_font("small"),
            text_color=Theme.ERROR,
            anchor="w"
        )
        self.error_label.pack(fill="x")
        
        # Knappar
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Avbryt",
            width=120,
            height=40,
            command=self._cancel,
            **Theme.get_secondary_button_colors()
        ).pack(side="left")
        
        ctk.CTkButton(
            button_frame,
            text="Skapa databas",
            width=160,
            height=40,
            command=self._create,
            **Theme.get_button_colors()
        ).pack(side="right")
    
    def _browse_db_path(self):
        # Släpp grab tillfälligt så fil-dialogen fungerar
        self.grab_release()
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Välj plats för databasen",
            defaultextension=".krdb",
            filetypes=[("KontaktRegister databas", "*.krdb")],
            initialfile="kontakter.krdb"
        )
        self.grab_set()
        if path:
            self.db_path_entry.delete(0, "end")
            self.db_path_entry.insert(0, path)
    
    def _browse_backup_path(self):
        # Släpp grab tillfälligt så fil-dialogen fungerar
        self.grab_release()
        path = filedialog.askdirectory(
            parent=self,
            title="Välj mapp för backups"
        )
        self.grab_set()
        if path:
            self.backup_path_entry.delete(0, "end")
            self.backup_path_entry.insert(0, path)
    
    def _update_strength(self, event=None):
        password = self.password_entry.get()
        strength = PasswordValidator.analyze_strength(password)
        
        # Uppdatera indikatorbarer
        for i, bar in enumerate(self.strength_bars):
            if i <= strength.score:
                bar.configure(fg_color=PASSWORD_STRENGTH_COLORS.get(strength.score, Theme.BG_HOVER))
            else:
                bar.configure(fg_color=Theme.BG_HOVER)
        
        # Uppdatera etikett
        if password:
            feedback = f"{strength.label}"
            if strength.feedback:
                feedback += f" - {strength.feedback[0]}"
            self.strength_label.configure(
                text=feedback,
                text_color=PASSWORD_STRENGTH_COLORS.get(strength.score, Theme.TEXT_MUTED)
            )
        else:
            self.strength_label.configure(text="", text_color=Theme.TEXT_MUTED)
    
    def _toggle_password_visibility(self):
        show = "" if self.show_password_var.get() else "●"
        self.password_entry.configure(show=show)
        self.confirm_entry.configure(show=show)
    
    def _validate(self) -> Optional[str]:
        """Validerar formuläret. Returnerar felmeddelande eller None."""
        db_path = self.db_path_entry.get().strip()
        backup_path = self.backup_path_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not db_path:
            return "Välj var databasen ska sparas"
        
        if not backup_path:
            return "Välj var backups ska sparas"
        
        # Validera lösenord
        is_valid, error = PasswordValidator.validate(password)
        if not is_valid:
            return error
        
        if password != confirm:
            return "Lösenorden matchar inte"
        
        # Kontrollera att mappen är skrivbar
        try:
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            return "Kan inte skriva till vald databas-plats"
        
        return None
    
    def _on_language_change(self, value: str):
        """Hanterar språkbyte."""
        # Hitta språkkod från visningsnamn
        for code, name in LANGUAGES.items():
            if name == value:
                self.selected_language = code
                break
    
    def _create(self):
        try:
            error = self._validate()
            if error:
                self.error_label.configure(text=error)
                return
            
            self.result = (
                self.db_path_entry.get().strip(),
                self.backup_path_entry.get().strip(),
                self.password_entry.get(),
                self.selected_language
            )
            
            self.on_complete(*self.result)
            self.destroy()
        except Exception as e:
            self.error_label.configure(text=f"Fel: {str(e)}")
    
    def _cancel(self):
        self.result = None
        self.destroy()


class LoginDialog(ctk.CTkToplevel):
    """Dialog för att logga in med befintlig databas."""
    
    def __init__(self, parent, db_path: str, on_complete: Callable[[str], None]):
        super().__init__(parent)
        
        self.db_path = db_path
        self.on_complete = on_complete
        self.result = None
        
        # Fönsterinställningar
        self.title("Öppna databas")
        self.geometry("540x360")
        self.resizable(True, True)
        self.configure(fg_color=Theme.BG_DARK)
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Centrera
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 540) // 2
        y = (self.winfo_screenheight() - 360) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
        self.password_entry.focus_set()
        
        # Bind Enter
        self.bind("<Return>", lambda e: self._login())
    
    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Titel
        title = ctk.CTkLabel(
            main_frame,
            text="KontaktRegister",
            font=Theme.get_font("title", bold=True),
            text_color=Theme.ACCENT_GOLD
        )
        title.pack(pady=(0, 5))
        
        # Databas-info
        db_name = Path(self.db_path).name
        ctk.CTkLabel(
            main_frame,
            text=f"Databas: {db_name}",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_MUTED
        ).pack(pady=(0, 20))
        
        # Lösenord
        ctk.CTkLabel(
            main_frame,
            text="Ange lösenord:",
            font=Theme.get_font("normal", bold=True),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x")
        
        self.password_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Ditt lösenord",
            show="●",
            **Theme.get_entry_colors(),
            height=40
        )
        self.password_entry.pack(fill="x", pady=(5, 0))
        
        # Visa lösenord
        self.show_password_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            main_frame,
            text="Visa lösenord",
            variable=self.show_password_var,
            command=self._toggle_visibility,
            fg_color=Theme.ACCENT_GOLD,
            hover_color=Theme.ACCENT_GOLD_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            font=Theme.get_font("small")
        ).pack(anchor="w", pady=(10, 0))
        
        # Felmeddelande
        self.error_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=Theme.get_font("small"),
            text_color=Theme.ERROR
        )
        self.error_label.pack(pady=(10, 0))
        
        # Knappar
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Annan databas",
            width=120,
            height=40,
            command=self._other_db,
            **Theme.get_secondary_button_colors()
        ).pack(side="left")
        
        ctk.CTkButton(
            button_frame,
            text="Öppna",
            width=120,
            height=40,
            command=self._login,
            **Theme.get_button_colors()
        ).pack(side="right")
    
    def _toggle_visibility(self):
        show = "" if self.show_password_var.get() else "●"
        self.password_entry.configure(show=show)
    
    def _login(self):
        password = self.password_entry.get()
        if not password:
            self.error_label.configure(text="Ange lösenord")
            return
        
        self.result = password
        self.on_complete(password)
    
    def _other_db(self):
        self.result = "OTHER_DB"
        self.destroy()
    
    def show_error(self, message: str):
        self.error_label.configure(text=message)
        self.password_entry.delete(0, "end")
        self.password_entry.focus_set()


class ConfirmDialog(ctk.CTkToplevel):
    """Bekräftelsedialog."""
    
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        confirm_text: str = "OK",
        cancel_text: str = "Avbryt",
        is_destructive: bool = False
    ):
        super().__init__(parent)
        
        self.result = False
        
        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_DARK)
        
        self.transient(parent)
        self.grab_set()
        
        # Centrera
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 180) // 2
        self.geometry(f"+{x}+{y}")
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text=message,
            font=Theme.get_font("normal"),
            text_color=Theme.TEXT_PRIMARY,
            wraplength=340
        ).pack(pady=(0, 20))
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        ctk.CTkButton(
            button_frame,
            text=cancel_text,
            width=100,
            height=38,
            command=self._cancel,
            **Theme.get_secondary_button_colors()
        ).pack(side="left")
        
        confirm_colors = Theme.get_button_colors()
        if is_destructive:
            confirm_colors["fg_color"] = Theme.ERROR
            confirm_colors["hover_color"] = "#e05555"
        
        ctk.CTkButton(
            button_frame,
            text=confirm_text,
            width=100,
            height=38,
            command=self._confirm,
            **confirm_colors
        ).pack(side="right")
        
        self.bind("<Return>", lambda e: self._confirm())
        self.bind("<Escape>", lambda e: self._cancel())
    
    def _confirm(self):
        self.result = True
        self.destroy()
    
    def _cancel(self):
        self.result = False
        self.destroy()
    
    def get_result(self) -> bool:
        self.wait_window()
        return self.result
