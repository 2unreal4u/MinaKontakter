"""
Huvudfönster för KontaktRegister.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional
import logging

from ui.theme import Theme
from ui.contact_list import ContactListPanel
from ui.contact_detail import ContactDetailPanel
from ui.contact_editor import ContactEditorDialog
from ui.dialogs import SetupDialog, LoginDialog, ConfirmDialog
from database.db_manager import DatabaseManager
from database.models import Contact
from services.import_export import ImportExportService
from config import (
    APP_NAME, APP_VERSION,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    DEFAULT_DB_DIR, DEFAULT_BACKUP_DIR
)

logger = logging.getLogger(__name__)


class MainWindow(ctk.CTk):
    """Huvudfönster för applikationen."""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        
        self.db_manager = db_manager
        
        # Konfigurera fönster
        self.title(f"{APP_NAME}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(fg_color=Theme.BG_DARK)
        
        # Ikon (om tillgänglig)
        try:
            self.iconbitmap("assets/icon.ico")
        except Exception:
            pass
        
        # Tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self._create_widgets()
        self._create_menu()
        self._bind_events()
        
        # Ladda kontakter
        self._refresh_contacts()
    
    def _create_widgets(self):
        # === Topbar ===
        self.topbar = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_MEDIUM,
            height=60,
            corner_radius=0
        )
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)
        
        # Titel
        title_label = ctk.CTkLabel(
            self.topbar,
            text=APP_NAME,
            font=("Segoe UI", 24, "bold"),
            text_color=Theme.ACCENT_GOLD
        )
        title_label.pack(side="left", padx=20)
        
        # Sökfält (global sökning)
        search_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        search_frame.pack(side="right", padx=20)
        
        self.global_search = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Sök kontakter...",
            width=250,
            height=36,
            **Theme.get_entry_colors(),
            corner_radius=18
        )
        self.global_search.pack(side="right")
        self.global_search.bind("<KeyRelease>", self._on_global_search)
        
        # Kontaktantal
        self.count_label = ctk.CTkLabel(
            search_frame,
            text="",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        self.count_label.pack(side="right", padx=(0, 15))
        
        # === Huvudinnehåll ===
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Vänster panel - kontaktlista
        self.contact_list = ContactListPanel(
            self.main_content,
            on_select=self._on_contact_selected,
            on_add=self._add_contact
        )
        self.contact_list.pack(side="left", fill="y", padx=(0, 15))
        
        # Höger panel - kontaktdetaljer
        self.contact_detail = ContactDetailPanel(
            self.main_content,
            on_edit=self._edit_contact,
            on_delete=self._delete_contact,
            on_export=self._export_contact
        )
        self.contact_detail.pack(side="left", fill="both", expand=True)
        self.contact_detail.set_favorite_callback(self._on_favorite_changed)
        
        # === Statusrad ===
        self.statusbar = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_MEDIUM,
            height=30,
            corner_radius=0
        )
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.statusbar,
            text="Redo",
            font=Theme.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        self.status_label.pack(side="left", padx=15)
        
        # Databasinfo
        if self.db_manager.db_path:
            db_info = ctk.CTkLabel(
                self.statusbar,
                text=f"📁 {self.db_manager.db_path.name}",
                font=Theme.get_font("small"),
                text_color=Theme.TEXT_MUTED
            )
            db_info.pack(side="right", padx=15)
    
    def _create_menu(self):
        """Skapar menyraden."""
        self.menu_frame = ctk.CTkFrame(
            self.topbar,
            fg_color="transparent"
        )
        self.menu_frame.pack(side="left", padx=(20, 0))
        
        # Arkiv-meny (simulerad med knappar)
        file_btn = ctk.CTkButton(
            self.menu_frame,
            text="Arkiv ▾",
            width=70,
            height=30,
            font=Theme.get_font("small"),
            fg_color="transparent",
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            command=self._show_file_menu
        )
        file_btn.pack(side="left", padx=2)
        
        # Import-knapp direkt
        import_btn = ctk.CTkButton(
            self.menu_frame,
            text="📥 Importera",
            width=90,
            height=30,
            font=Theme.get_font("small"),
            fg_color="transparent",
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            command=self._import_csv
        )
        import_btn.pack(side="left", padx=2)
        
        # Export-knapp direkt
        export_btn = ctk.CTkButton(
            self.menu_frame,
            text="📤 Exportera",
            width=90,
            height=30,
            font=Theme.get_font("small"),
            fg_color="transparent",
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            command=self._export_all_csv
        )
        export_btn.pack(side="left", padx=2)
        
        # Backup-knapp
        backup_btn = ctk.CTkButton(
            self.menu_frame,
            text="💾 Backup",
            width=80,
            height=30,
            font=Theme.get_font("small"),
            fg_color="transparent",
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            command=self._create_backup
        )
        backup_btn.pack(side="left", padx=2)
    
    def _show_file_menu(self):
        """Visar arkiv-menyn."""
        # Stäng befintlig meny om den finns
        if hasattr(self, '_active_file_menu') and self._active_file_menu:
            try:
                self._active_file_menu.destroy()
            except:
                pass
            self._active_file_menu = None
        
        menu = ctk.CTkToplevel(self)
        self._active_file_menu = menu
        menu.title("")
        menu.geometry("200x220")
        menu.overrideredirect(True)
        menu.configure(fg_color=Theme.BG_MEDIUM)
        
        # Positionera under knappen
        x = self.winfo_x() + 100
        y = self.winfo_y() + 90
        menu.geometry(f"+{x}+{y}")
        
        def close_menu(event=None):
            """Stänger menyn."""
            try:
                if self._active_file_menu:
                    self._active_file_menu.destroy()
                    self._active_file_menu = None
            except:
                pass
        
        def run_command(cmd):
            """Stänger meny och kör kommando."""
            close_menu()
            if cmd:
                self.after(50, cmd)
        
        # Menyalternativ
        items = [
            ("📥 Importera CSV...", self._import_csv),
            ("📤 Exportera alla...", self._export_all_csv),
            ("", None),  # Separator
            ("💾 Backup nu", self._create_backup),
            ("📂 Återställ backup...", self._restore_backup),
            ("", None),
            ("⚙️ Inställningar", self._show_settings),
            ("", None),
            ("🚪 Avsluta", self._quit_app),
        ]
        
        for text, command in items:
            if not text:
                # Separator
                sep = ctk.CTkFrame(menu, height=1, fg_color=Theme.BORDER)
                sep.pack(fill="x", padx=10, pady=5)
            else:
                btn = ctk.CTkButton(
                    menu,
                    text=text,
                    anchor="w",
                    height=30,
                    fg_color="transparent",
                    hover_color=Theme.BG_HOVER,
                    text_color=Theme.TEXT_PRIMARY,
                    font=Theme.get_font("small"),
                    command=lambda c=command: run_command(c)
                )
                btn.pack(fill="x", padx=5, pady=1)
        
        # Använd grab för att fånga klick utanför
        menu.grab_set()
        menu.bind("<Escape>", close_menu)
        
        # Bind klick utanför till stängning
        def on_click_outside(event):
            try:
                widget = event.widget
                if widget != menu and not str(widget).startswith(str(menu)):
                    close_menu()
            except:
                close_menu()
        
        menu.bind_all("<Button-1>", on_click_outside, add="+")
        
        # Ta bort global binding när menyn stängs
        def on_destroy(event):
            try:
                menu.unbind_all("<Button-1>")
            except:
                pass
        
        menu.bind("<Destroy>", on_destroy)
        menu.focus_set()
    
    def _bind_events(self):
        """Binder händelser."""
        # Stängning
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Kortkommandon
        self.bind("<Control-n>", lambda e: self._add_contact())
        self.bind("<Control-f>", lambda e: self.global_search.focus_set())
        self.bind("<Control-s>", lambda e: self._save_database())
        self.bind("<Control-b>", lambda e: self._create_backup())
        self.bind("<Escape>", lambda e: self._clear_selection())
    
    def _refresh_contacts(self):
        """Uppdaterar kontaktlistan."""
        query = self.global_search.get().strip()
        contacts = self.db_manager.get_contacts(query=query, sort_by="name")
        self.contact_list.update_contacts(contacts)
        
        # Uppdatera antal
        total = self.db_manager.get_contact_count()
        if query:
            self.count_label.configure(text=f"{len(contacts)} av {total} kontakter")
        else:
            self.count_label.configure(text=f"{total} kontakter")
    
    def _on_global_search(self, event=None):
        """Hanterar global sökning."""
        self._refresh_contacts()
    
    def _on_contact_selected(self, contact: Contact):
        """Hanterar val av kontakt."""
        self.contact_detail.show_contact(contact)
        self._set_status(f"Visar: {contact.name}")
    
    def _add_contact(self):
        """Öppnar dialog för att lägga till ny kontakt."""
        existing_tags = self.db_manager.get_all_tags()
        
        dialog = ContactEditorDialog(
            self,
            contact=None,
            existing_tags=existing_tags
        )
        
        result = dialog.get_result()
        
        if result:
            self.db_manager.add_contact(result)
            self._save_database()
            self._refresh_contacts()
            self.contact_list.select_contact(result)
            self.contact_detail.show_contact(result)
            self._set_status(f"Kontakt tillagd: {result.name}")
    
    def _edit_contact(self, contact: Contact):
        """Öppnar dialog för att redigera kontakt."""
        existing_tags = self.db_manager.get_all_tags()
        
        dialog = ContactEditorDialog(
            self,
            contact=contact,
            existing_tags=existing_tags
        )
        
        result = dialog.get_result()
        
        if result:
            self.db_manager.update_contact(result)
            self._save_database()
            self._refresh_contacts()
            self.contact_list.select_contact(result)
            self.contact_detail.show_contact(result)
            self._set_status(f"Kontakt uppdaterad: {result.name}")
    
    def _delete_contact(self, contact: Contact):
        """Tar bort kontakt efter bekräftelse."""
        dialog = ConfirmDialog(
            self,
            title="Radera kontakt",
            message=f"Är du säker på att du vill radera '{contact.name}'?\n\nDetta kan inte ångras.",
            confirm_text="Radera",
            cancel_text="Avbryt",
            is_destructive=True
        )
        
        if dialog.get_result():
            self.db_manager.delete_contact(contact.id)
            self._save_database()
            self._refresh_contacts()
            self.contact_detail.clear()
            self._set_status(f"Kontakt raderad: {contact.name}")
    
    def _export_contact(self, contact: Contact):
        """Exporterar en enskild kontakt."""
        file_path = filedialog.asksaveasfilename(
            title="Exportera kontakt",
            defaultextension=".csv",
            filetypes=[("CSV-fil", "*.csv")],
            initialfile=f"{contact.name}.csv"
        )
        
        if file_path:
            success, message = ImportExportService.export_to_csv([contact], file_path)
            if success:
                self._set_status(f"Kontakt exporterad: {contact.name}")
                messagebox.showinfo("Export klar", f"Kontakten exporterades till:\n{file_path}")
            else:
                messagebox.showerror("Exportfel", message)
    
    def _on_favorite_changed(self, contact: Contact):
        """Hanterar ändring av favorit-status."""
        self.db_manager.update_contact(contact)
        self._save_database()
        self._refresh_contacts()
        self.contact_list.select_contact(contact)
    
    def _import_csv(self):
        """Importerar kontakter från CSV."""
        file_path = filedialog.askopenfilename(
            title="Importera kontakter",
            filetypes=[
                ("CSV-filer", "*.csv"),
                ("Alla filer", "*.*")
            ]
        )
        
        if file_path:
            contacts, error = ImportExportService.import_from_csv(file_path)
            
            if contacts:
                # Bekräfta import
                dialog = ConfirmDialog(
                    self,
                    title="Bekräfta import",
                    message=f"Importera {len(contacts)} kontakter?\n\n{error}" if error else f"Importera {len(contacts)} kontakter?",
                    confirm_text="Importera",
                    cancel_text="Avbryt"
                )
                
                if dialog.get_result():
                    imported = 0
                    for contact in contacts:
                        self.db_manager.add_contact(contact)
                        imported += 1
                    
                    self._save_database()
                    self._refresh_contacts()
                    self._set_status(f"{imported} kontakter importerade")
                    messagebox.showinfo("Import klar", f"{imported} kontakter importerades.")
            elif error:
                messagebox.showerror("Importfel", error)
            else:
                messagebox.showinfo("Import", "Inga kontakter hittades i filen.")
    
    def _export_all_csv(self):
        """Exporterar alla kontakter till CSV."""
        contacts = self.db_manager.get_contacts()
        
        if not contacts:
            messagebox.showinfo("Export", "Inga kontakter att exportera.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportera alla kontakter",
            defaultextension=".csv",
            filetypes=[("CSV-fil", "*.csv")],
            initialfile="kontakter_export.csv"
        )
        
        if file_path:
            success, message = ImportExportService.export_to_csv(contacts, file_path)
            if success:
                self._set_status(message)
                messagebox.showinfo("Export klar", f"Exporterade till:\n{file_path}")
            else:
                messagebox.showerror("Exportfel", message)
    
    def _create_backup(self):
        """Skapar backup."""
        success, result = self.db_manager.create_backup()
        
        if success:
            self._set_status(f"Backup skapad")
            messagebox.showinfo("Backup klar", f"Backup skapad:\n{result}")
        else:
            messagebox.showerror("Backup-fel", result)
    
    def _restore_backup(self):
        """Återställer från backup."""
        # Lista tillgängliga backups
        backups = self.db_manager.list_backups()
        
        if not backups:
            messagebox.showinfo("Inga backups", "Inga backups hittades.")
            return
        
        # Välj backup-fil
        file_path = filedialog.askopenfilename(
            title="Välj backup att återställa",
            initialdir=self.db_manager.backup_path,
            filetypes=[
                ("Backup-filer", "*.backup"),
                ("Alla filer", "*.*")
            ]
        )
        
        if file_path:
            dialog = ConfirmDialog(
                self,
                title="Bekräfta återställning",
                message="Återställ från backup?\n\nNuvarande data kommer att ersättas.",
                confirm_text="Återställ",
                cancel_text="Avbryt",
                is_destructive=True
            )
            
            if dialog.get_result():
                # Be om lösenord
                from ui.dialogs import LoginDialog
                
                def on_login(password: str):
                    success, error = self.db_manager.restore_backup(file_path, password)
                    if success:
                        self._refresh_contacts()
                        self._set_status("Backup återställd")
                        messagebox.showinfo("Återställd", "Backup återställdes framgångsrikt.")
                        login.destroy()
                    else:
                        login.show_error(error)
                
                login = LoginDialog(self, file_path, on_login)
    
    def _show_settings(self):
        """Visar inställningar (förenklad version)."""
        messagebox.showinfo(
            "Inställningar",
            "Inställningar kommer i nästa version.\n\n"
            "Nuvarande funktioner:\n"
            "• Automatisk backup vid stängning\n"
            "• Krypterad databas (AES-256-GCM)\n"
            f"• Backup-plats: {self.db_manager.backup_path}"
        )
    
    def _save_database(self):
        """Sparar databasen."""
        success, error = self.db_manager.save()
        if not success:
            logger.error(f"Kunde inte spara: {error}")
            messagebox.showerror("Sparfel", f"Kunde inte spara databasen:\n{error}")
    
    def _clear_selection(self):
        """Rensar val och fokus."""
        self.contact_list.select_contact(None)
        self.contact_detail.clear()
        self.global_search.delete(0, "end")
        self._refresh_contacts()
    
    def _set_status(self, message: str):
        """Sätter statusmeddelande."""
        self.status_label.configure(text=message)
        logger.info(message)
    
    def _quit_app(self):
        """Avslutar applikationen."""
        self._on_close()
    
    def _on_close(self):
        """Hanterar stängning av applikationen."""
        # Stäng eventuella öppna menyer/overlays
        if hasattr(self, '_active_file_menu') and self._active_file_menu:
            try:
                self._active_file_menu.destroy()
            except:
                pass
        if hasattr(self, '_menu_overlay') and self._menu_overlay:
            try:
                self._menu_overlay.destroy()
            except:
                pass
        
        # Stäng menyer i contact_detail om den finns
        if hasattr(self, 'detail_panel'):
            if hasattr(self.detail_panel, '_active_menu') and self.detail_panel._active_menu:
                try:
                    self.detail_panel._active_menu.destroy()
                except:
                    pass
            if hasattr(self.detail_panel, '_menu_overlay') and self.detail_panel._menu_overlay:
                try:
                    self.detail_panel._menu_overlay.destroy()
                except:
                    pass
        
        # Skapa backup om aktiverat
        if self.db_manager.is_open:
            if self.db_manager.data and self.db_manager.data.metadata.auto_backup:
                self._set_status("Skapar backup...")
                self.db_manager.create_backup()
            
            # Stäng databas
            self.db_manager.close()
        
        # Avsluta mainloop och förstör fönstret
        self.quit()
        self.destroy()
