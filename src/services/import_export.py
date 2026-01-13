"""
Import/Export-service för KontaktRegister.
Hanterar CSV import och export.
"""

import csv
import logging
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime

from database.models import Contact, PhoneNumber, EmailAddress, SocialMedia
from config import CSV_ENCODING, CSV_DELIMITER

logger = logging.getLogger(__name__)

# CSV-kolumner för export/import
CSV_COLUMNS = [
    "Name",
    "Phone1", "Phone1Type",
    "Phone2", "Phone2Type",
    "Phone3", "Phone3Type",
    "Email1", "Email1Type",
    "Email2", "Email2Type",
    "Street", "PostalCode", "City", "Country",
    "Company",
    "Title",
    "Birthday",
    "Notes",
    "Tags",
    "LinkedIn", "Twitter", "Facebook", "Instagram", "Website",
    "IsFavorite",
]


class ImportExportService:
    """Hanterar import och export av kontakter."""
    
    @staticmethod
    def export_to_csv(contacts: list[Contact], file_path: str) -> Tuple[bool, str]:
        """
        Exporterar kontakter till CSV-fil.
        
        Args:
            contacts: Lista med kontakter att exportera
            file_path: Sökväg till CSV-fil
            
        Returns:
            (success, error_message_or_count)
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', newline='', encoding=CSV_ENCODING) as f:
                writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, delimiter=CSV_DELIMITER)
                writer.writeheader()
                
                for contact in contacts:
                    row = ImportExportService._contact_to_row(contact)
                    writer.writerow(row)
            
            logger.info(f"Exporterade {len(contacts)} kontakter till {file_path}")
            return True, f"{len(contacts)} kontakter exporterade"
            
        except Exception as e:
            logger.error(f"Export misslyckades: {e}")
            return False, f"Export misslyckades: {str(e)}"
    
    @staticmethod
    def import_from_csv(file_path: str) -> Tuple[list[Contact], str]:
        """
        Importerar kontakter från CSV-fil.
        
        Args:
            file_path: Sökväg till CSV-fil
            
        Returns:
            (lista med kontakter, felmeddelande om fel)
        """
        contacts = []
        errors = []
        
        try:
            path = Path(file_path)
            
            if not path.exists():
                return [], "Filen finns inte"
            
            # Försök identifiera encoding och delimiter
            encoding = CSV_ENCODING
            delimiter = CSV_DELIMITER
            
            with open(path, 'r', encoding=encoding) as f:
                # Läs första raden för att avgöra delimiter
                first_line = f.readline()
                if ';' in first_line and ',' not in first_line:
                    delimiter = ';'
                f.seek(0)
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        contact = ImportExportService._row_to_contact(row)
                        if contact.name:  # Kräv minst namn
                            contacts.append(contact)
                        else:
                            errors.append(f"Rad {row_num}: Namn saknas")
                    except Exception as e:
                        errors.append(f"Rad {row_num}: {str(e)}")
            
            error_msg = ""
            if errors:
                error_msg = f"Varningar: {'; '.join(errors[:5])}"
                if len(errors) > 5:
                    error_msg += f" (+{len(errors) - 5} fler)"
            
            logger.info(f"Importerade {len(contacts)} kontakter från {file_path}")
            return contacts, error_msg
            
        except UnicodeDecodeError:
            # Försök med annan encoding
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    for row in reader:
                        contact = ImportExportService._row_to_contact(row)
                        if contact.name:
                            contacts.append(contact)
                return contacts, ""
            except Exception as e:
                return [], f"Kunde inte läsa filen: {str(e)}"
        except Exception as e:
            logger.error(f"Import misslyckades: {e}")
            return [], f"Import misslyckades: {str(e)}"
    
    @staticmethod
    def _contact_to_row(contact: Contact) -> dict:
        """Konverterar Contact till CSV-rad."""
        row = {col: "" for col in CSV_COLUMNS}
        
        row["Name"] = contact.name
        row["Street"] = contact.street
        row["PostalCode"] = contact.postal_code
        row["City"] = contact.city
        row["Country"] = contact.country
        row["Company"] = contact.company
        row["Title"] = contact.title
        row["Birthday"] = contact.birthday
        row["Notes"] = contact.notes
        row["Tags"] = ",".join(contact.tags)
        row["IsFavorite"] = "Yes" if contact.is_favorite else "No"
        
        # Telefonnummer
        for i, phone in enumerate(contact.phones[:3], start=1):
            row[f"Phone{i}"] = phone.number
            row[f"Phone{i}Type"] = phone.type
        
        # E-post
        for i, email in enumerate(contact.emails[:2], start=1):
            row[f"Email{i}"] = email.address
            row[f"Email{i}Type"] = email.type
        
        # Sociala medier
        for sm in contact.social_media:
            platform_map = {
                "linkedin": "LinkedIn",
                "twitter": "Twitter",
                "facebook": "Facebook",
                "instagram": "Instagram",
                "website": "Website",
            }
            col = platform_map.get(sm.platform.lower())
            if col and col in row:
                row[col] = sm.username
        
        return row
    
    @staticmethod
    def _row_to_contact(row: dict) -> Contact:
        """Konverterar CSV-rad till Contact."""
        # Hantera olika kolumnnamn (kompatibilitet med olika format)
        # Försök flera varianter för namn
        first_name = row.get("First Name", "") or row.get("Förnamn", "") or ""
        last_name = row.get("Last Name", "") or row.get("Efternamn", "") or ""
        
        name = (
            row.get("Name") or 
            row.get("Namn") or 
            row.get("Full Name") or 
            row.get("Fullständigt namn") or
            row.get("Display Name") or
            f"{first_name} {last_name}".strip()
        )
        
        # Om fortfarande inget namn, använd företag eller e-post som fallback
        if not name:
            name = row.get("Company") or row.get("Företag") or ""
        if not name:
            # Försök hitta e-post att använda som namn
            for key in row:
                if "mail" in key.lower() and row[key]:
                    name = row[key].split("@")[0]  # Använd delen före @
                    break
        
        name = (name or "").strip()
        
        # Telefonnummer
        phones = []
        for i in range(1, 4):
            phone = row.get(f"Phone{i}") or row.get(f"Phone {i}") or row.get(f"Telefon{i}")
            if phone:
                phone_type = row.get(f"Phone{i}Type") or row.get(f"Phone {i} Type") or "mobile"
                phones.append(PhoneNumber(number=phone.strip(), type=phone_type.lower()))
        
        # Fallback för Outlook-format och andra varianter
        if not phones:
            phone_fields = [
                ("Mobile Phone", "mobile"), ("Business Phone", "work"), 
                ("Home Phone", "home"), ("Primary Phone", "mobile"),
                ("Telefon", "mobile"), ("Mobil", "mobile"), ("Mobiltelefon", "mobile"),
                ("Phone", "mobile"), ("Tel", "mobile")
            ]
            for field, ptype in phone_fields:
                phone = row.get(field)
                if phone:
                    phones.append(PhoneNumber(number=phone.strip(), type=ptype))
        
        # Om fortfarande inga telefoner, leta efter kolumner med "phone" eller "tel" i namnet
        if not phones:
            for key, value in row.items():
                if value and any(x in key.lower() for x in ["phone", "tel", "mobil"]):
                    phones.append(PhoneNumber(number=value.strip(), type="mobile"))
                    break
        
        # E-post
        emails = []
        for i in range(1, 3):
            email = row.get(f"Email{i}") or row.get(f"E-mail {i}") or row.get(f"Email {i} Address")
            if email:
                email_type = row.get(f"Email{i}Type") or "personal"
                emails.append(EmailAddress(address=email.strip(), type=email_type.lower()))
        
        # Fallback för Outlook-format och andra varianter
        if not emails:
            email_fields = [
                "E-mail Address", "E-mail 2 Address", "E-mail 3 Address",
                "Email", "E-post", "Mail", "E-mail"
            ]
            for field in email_fields:
                email = row.get(field)
                if email:
                    emails.append(EmailAddress(address=email.strip(), type="personal"))
        
        # Om fortfarande inga e-poster, leta efter kolumner med "mail" i namnet
        if not emails:
            for key, value in row.items():
                if value and "mail" in key.lower() and "@" in str(value):
                    emails.append(EmailAddress(address=value.strip(), type="personal"))
                    break
        
        # Adress - försök separata fält först
        street = row.get("Street") or row.get("Gata") or row.get("Gatuadress") or ""
        postal_code = row.get("PostalCode") or row.get("Postnummer") or row.get("Postal Code") or ""
        city = row.get("City") or row.get("Ort") or row.get("Stad") or ""
        country = row.get("Country") or row.get("Land") or ""
        
        # Fallback: försök Outlook-format
        if not street:
            for field in ["Business Street", "Home Street", "Address", "Adress"]:
                if row.get(field):
                    street = row[field]
                    break
        if not city:
            for field in ["Business City", "Home City"]:
                if row.get(field):
                    city = row[field]
                    break
        if not postal_code:
            for field in ["Business Postal Code", "Home Postal Code"]:
                if row.get(field):
                    postal_code = row[field]
                    break
        
        # Företag
        company = row.get("Company") or row.get("Företag") or row.get("Company Name") or ""
        
        # Titel
        title = row.get("Title") or row.get("Titel") or row.get("Job Title") or ""
        
        # Födelsedag
        birthday = row.get("Birthday") or row.get("Födelsedag") or ""
        
        # Notes
        notes = row.get("Notes") or row.get("Anteckningar") or row.get("Body") or ""
        
        # Taggar
        tags_str = row.get("Tags") or row.get("Taggar") or row.get("Categories") or ""
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        
        # Sociala medier
        social_media = []
        social_fields = [
            ("LinkedIn", "linkedin"), ("Twitter", "twitter"), 
            ("Facebook", "facebook"), ("Instagram", "instagram"),
            ("Website", "website"), ("GitHub", "github"),
            ("Telegram", "telegram"), ("WhatsApp", "whatsapp"),
        ]
        for csv_col, platform in social_fields:
            value = row.get(csv_col) or row.get(csv_col.lower()) or ""
            if value:
                social_media.append(SocialMedia(platform=platform, username=value.strip()))
        
        # Favorit
        is_favorite = row.get("IsFavorite", "").lower() in ["yes", "ja", "true", "1"]
        
        return Contact(
            name=name,
            phones=phones,
            emails=emails,
            street=street.strip(),
            postal_code=postal_code.strip(),
            city=city.strip(),
            country=country.strip(),
            company=company.strip(),
            title=title.strip(),
            birthday=birthday.strip(),
            notes=notes.strip(),
            tags=tags,
            social_media=social_media,
            is_favorite=is_favorite,
        )
    
    @staticmethod
    def get_csv_template() -> str:
        """Returnerar en tom CSV-mall."""
        return CSV_DELIMITER.join(CSV_COLUMNS) + "\n"
