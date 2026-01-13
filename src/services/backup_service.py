"""
Backup-service för KontaktRegister.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class BackupService:
    """
    Hanterar backup-relaterade operationer.
    
    OBS: Huvudsaklig backup-logik finns i DatabaseManager.
    Denna klass kan användas för utökad funktionalitet.
    """
    
    @staticmethod
    def format_backup_info(backup: dict) -> str:
        """
        Formaterar backup-information för visning.
        
        Args:
            backup: Dict med path, date, size
            
        Returns:
            Formaterad sträng
        """
        date_str = backup["date"].strftime("%Y-%m-%d %H:%M")
        size_kb = backup["size"] / 1024
        
        if size_kb < 1024:
            size_str = f"{size_kb:.1f} KB"
        else:
            size_str = f"{size_kb / 1024:.1f} MB"
        
        return f"{date_str} ({size_str})"
    
    @staticmethod
    def get_backup_age(backup: dict) -> str:
        """
        Returnerar backup-ålder i läsbar form.
        
        Args:
            backup: Dict med date
            
        Returns:
            T.ex. "2 dagar sedan"
        """
        now = datetime.now()
        delta = now - backup["date"]
        
        if delta.days == 0:
            hours = delta.seconds // 3600
            if hours == 0:
                minutes = delta.seconds // 60
                return f"{minutes} minuter sedan"
            return f"{hours} timmar sedan"
        elif delta.days == 1:
            return "igår"
        elif delta.days < 7:
            return f"{delta.days} dagar sedan"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks} veckor sedan"
        else:
            return backup["date"].strftime("%Y-%m-%d")
    
    @staticmethod
    def validate_backup_path(path: str) -> Tuple[bool, str]:
        """
        Validerar att backup-sökvägen är giltig och skrivbar.
        
        Args:
            path: Sökväg att validera
            
        Returns:
            (is_valid, error_message)
        """
        try:
            backup_path = Path(path)
            
            # Skapa om den inte finns
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Kontrollera skrivbarhet
            test_file = backup_path / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            return True, ""
            
        except PermissionError:
            return False, "Ingen skrivrättighet till mappen"
        except Exception as e:
            return False, f"Ogiltig sökväg: {str(e)}"
