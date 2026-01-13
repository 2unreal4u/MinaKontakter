"""
Databashanterare för KontaktRegister.
Hanterar läsning/skrivning av krypterad databas.
"""

import os
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

from crypto.encryption import CryptoManager, PasswordValidator
from database.models import DatabaseData, DatabaseMetadata, Contact
from config import DEFAULT_DB_NAME, DEFAULT_BACKUP_SUFFIX, BACKUP_KEEP_COUNT

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Hanterar den krypterade databasen.
    
    Ansvarsområden:
    - Skapa ny databas
    - Öppna befintlig databas
    - Spara databas
    - Backup-hantering
    """
    
    def __init__(self):
        self._crypto = CryptoManager()
        self._data: Optional[DatabaseData] = None
        self._db_path: Optional[Path] = None
        self._is_modified: bool = False
    
    @property
    def is_open(self) -> bool:
        """Returnerar True om en databas är öppen."""
        return self._data is not None and self._crypto.is_initialized
    
    @property
    def data(self) -> Optional[DatabaseData]:
        """Returnerar databasdatan."""
        return self._data
    
    @property
    def db_path(self) -> Optional[Path]:
        """Returnerar sökvägen till databasen."""
        return self._db_path
    
    @property
    def backup_path(self) -> Optional[Path]:
        """Returnerar backup-sökvägen."""
        if self._data and self._data.metadata.backup_path:
            return Path(self._data.metadata.backup_path)
        return None
    
    @property
    def is_modified(self) -> bool:
        """Returnerar True om datan har ändrats sedan senaste sparning."""
        return self._is_modified
    
    def mark_modified(self):
        """Markerar databasen som modifierad."""
        self._is_modified = True
    
    def create_database(
        self,
        db_path: str,
        backup_path: str,
        password: str
    ) -> Tuple[bool, str]:
        """
        Skapar en ny krypterad databas.
        
        Args:
            db_path: Sökväg där databasen ska sparas
            backup_path: Sökväg för backups
            password: Användarens valda lösenord
            
        Returns:
            (success, error_message)
        """
        # Validera lösenord
        is_valid, error = PasswordValidator.validate(password)
        if not is_valid:
            return False, error
        
        try:
            db_path = Path(db_path)
            backup_path = Path(backup_path)
            
            # Skapa mappar om de inte finns
            db_path.parent.mkdir(parents=True, exist_ok=True)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Initiera kryptering
            self._crypto.initialize_new(password)
            
            # Skapa tom databas
            metadata = DatabaseMetadata(
                backup_path=str(backup_path),
                auto_backup=True,
            )
            
            self._data = DatabaseData(metadata=metadata)
            
            # Skapa verifieringsdata
            self._data.verification = self._crypto.create_verification_data()
            
            self._db_path = db_path
            
            # Spara
            success, error = self.save()
            if not success:
                return False, error
            
            logger.info(f"Ny databas skapad: {db_path}")
            return True, ""
            
        except Exception as e:
            logger.error(f"Kunde inte skapa databas: {e}")
            return False, f"Kunde inte skapa databas: {str(e)}"
    
    def open_database(self, db_path: str, password: str) -> Tuple[bool, str]:
        """
        Öppnar en befintlig krypterad databas.
        
        Args:
            db_path: Sökväg till databasfilen
            password: Användarens lösenord
            
        Returns:
            (success, error_message)
        """
        try:
            db_path = Path(db_path)
            
            if not db_path.exists():
                return False, "Databasfilen finns inte"
            
            # Läs krypterad fil
            with open(db_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Dekryptera
            try:
                decrypted_data = self._crypto.decrypt_file_data(encrypted_data, password)
            except Exception:
                return False, "Fel lösenord eller skadad databas"
            
            # Deserialisera
            self._data = DatabaseData.from_bytes(decrypted_data)
            
            # Verifiera lösenord
            if self._data.verification:
                if not self._crypto.verify_password(self._data.verification):
                    self._data = None
                    self._crypto.clear()
                    return False, "Fel lösenord"
            
            self._db_path = db_path
            self._is_modified = False
            
            logger.info(f"Databas öppnad: {db_path}")
            return True, ""
            
        except Exception as e:
            logger.error(f"Kunde inte öppna databas: {e}")
            self._crypto.clear()
            self._data = None
            return False, f"Kunde inte öppna databas: {str(e)}"
    
    def save(self) -> Tuple[bool, str]:
        """
        Sparar databasen till disk.
        
        Returns:
            (success, error_message)
        """
        if not self.is_open:
            return False, "Ingen databas är öppen"
        
        try:
            # Serialisera
            json_data = self._data.to_bytes()
            
            # Kryptera
            encrypted_data = self._crypto.encrypt_file_data(json_data)
            
            # Skriv atomärt (skriv till temp, sen rename)
            temp_path = self._db_path.with_suffix('.tmp')
            
            with open(temp_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Ersätt originalfilen
            if self._db_path.exists():
                backup_temp = self._db_path.with_suffix('.bak')
                shutil.move(str(self._db_path), str(backup_temp))
                try:
                    shutil.move(str(temp_path), str(self._db_path))
                    backup_temp.unlink()
                except Exception:
                    shutil.move(str(backup_temp), str(self._db_path))
                    raise
            else:
                shutil.move(str(temp_path), str(self._db_path))
            
            self._is_modified = False
            logger.info(f"Databas sparad: {self._db_path}")
            return True, ""
            
        except Exception as e:
            logger.error(f"Kunde inte spara databas: {e}")
            return False, f"Kunde inte spara databas: {str(e)}"
    
    def create_backup(self, backup_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Skapar en backup av databasen.
        
        Args:
            backup_dir: Valfri annan backup-mapp
            
        Returns:
            (success, backup_path_or_error)
        """
        if not self.is_open:
            return False, "Ingen databas är öppen"
        
        try:
            # Bestäm backup-mapp
            if backup_dir:
                backup_path = Path(backup_dir)
            elif self._data.metadata.backup_path:
                backup_path = Path(self._data.metadata.backup_path)
            else:
                backup_path = self._db_path.parent / "backups"
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Skapa backup-filnamn med tidsstämpel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{self._db_path.stem}_{timestamp}{DEFAULT_BACKUP_SUFFIX}"
            backup_file = backup_path / backup_filename
            
            # Spara först (för att säkerställa senaste data)
            save_success, save_error = self.save()
            if not save_success:
                return False, save_error
            
            # Kopiera databasfilen
            shutil.copy2(str(self._db_path), str(backup_file))
            
            # Rensa gamla backups
            self._cleanup_old_backups(backup_path)
            
            logger.info(f"Backup skapad: {backup_file}")
            return True, str(backup_file)
            
        except Exception as e:
            logger.error(f"Kunde inte skapa backup: {e}")
            return False, f"Kunde inte skapa backup: {str(e)}"
    
    def _cleanup_old_backups(self, backup_dir: Path):
        """Tar bort gamla backups, behåller BACKUP_KEEP_COUNT stycken."""
        try:
            backups = sorted(
                backup_dir.glob(f"*{DEFAULT_BACKUP_SUFFIX}"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            for old_backup in backups[BACKUP_KEEP_COUNT:]:
                old_backup.unlink()
                logger.debug(f"Gammal backup borttagen: {old_backup}")
                
        except Exception as e:
            logger.warning(f"Kunde inte rensa gamla backups: {e}")
    
    def restore_backup(self, backup_file: str, password: str) -> Tuple[bool, str]:
        """
        Återställer från backup.
        
        Args:
            backup_file: Sökväg till backup-filen
            password: Användarens lösenord
            
        Returns:
            (success, error_message)
        """
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            return False, "Backup-filen finns inte"
        
        # Öppna backup som en vanlig databas
        return self.open_database(str(backup_path), password)
    
    def list_backups(self) -> list[dict]:
        """
        Listar tillgängliga backups.
        
        Returns:
            Lista med dict: {"path": str, "date": datetime, "size": int}
        """
        backups = []
        
        if not self._data or not self._data.metadata.backup_path:
            return backups
        
        backup_dir = Path(self._data.metadata.backup_path)
        
        if not backup_dir.exists():
            return backups
        
        for backup_file in backup_dir.glob(f"*{DEFAULT_BACKUP_SUFFIX}"):
            try:
                stat = backup_file.stat()
                backups.append({
                    "path": str(backup_file),
                    "date": datetime.fromtimestamp(stat.st_mtime),
                    "size": stat.st_size,
                })
            except Exception:
                pass
        
        # Sortera med nyast först
        backups.sort(key=lambda b: b["date"], reverse=True)
        return backups
    
    def close(self, auto_backup: bool = False) -> Tuple[bool, str]:
        """
        Stänger databasen och rensar minne.
        
        Args:
            auto_backup: Om True, skapa backup innan stängning
            
        Returns:
            (success, error_message)
        """
        try:
            if self._is_modified:
                success, error = self.save()
                if not success:
                    return False, error
            
            if auto_backup and self._data and self._data.metadata.auto_backup:
                self.create_backup()
            
            # Rensa minne
            self._crypto.clear()
            self._data = None
            self._db_path = None
            self._is_modified = False
            
            logger.info("Databas stängd")
            return True, ""
            
        except Exception as e:
            logger.error(f"Fel vid stängning: {e}")
            return False, str(e)
    
    # === CRUD-operationer för kontakter ===
    
    def get_contacts(
        self,
        query: str = "",
        tag_filter: Optional[str] = None,
        favorites_only: bool = False,
        sort_by: str = "name"
    ) -> list[Contact]:
        """Hämtar kontakter med filter."""
        if not self._data:
            return []
        return self._data.search_contacts(query, tag_filter, favorites_only, sort_by)
    
    def get_contact(self, contact_id: str) -> Optional[Contact]:
        """Hämtar en kontakt via ID."""
        if not self._data:
            return None
        return self._data.get_contact_by_id(contact_id)
    
    def add_contact(self, contact: Contact) -> Contact:
        """Lägger till en ny kontakt."""
        if not self._data:
            raise RuntimeError("Ingen databas öppen")
        self._data.add_contact(contact)
        self.mark_modified()
        return contact
    
    def update_contact(self, contact: Contact) -> bool:
        """Uppdaterar en kontakt."""
        if not self._data:
            return False
        result = self._data.update_contact(contact)
        if result:
            self.mark_modified()
        return result
    
    def delete_contact(self, contact_id: str) -> bool:
        """Tar bort en kontakt."""
        if not self._data:
            return False
        result = self._data.delete_contact(contact_id)
        if result:
            self.mark_modified()
        return result
    
    def get_all_tags(self) -> list[str]:
        """Hämtar alla unika taggar."""
        if not self._data:
            return []
        return self._data.tags.copy()
    
    def get_contact_count(self) -> int:
        """Returnerar antal kontakter."""
        if not self._data:
            return 0
        return len(self._data.contacts)
