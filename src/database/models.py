"""
Datamodeller för KontaktRegister.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
import json
import base64


@dataclass
class PhoneNumber:
    """Telefonnummer med typ."""
    number: str
    type: str = "mobile"  # mobile, home, work, other
    
    def to_dict(self) -> dict:
        return {"number": self.number, "type": self.type}
    
    @classmethod
    def from_dict(cls, data: dict) -> "PhoneNumber":
        return cls(number=data.get("number", ""), type=data.get("type", "mobile"))


@dataclass
class EmailAddress:
    """E-postadress med typ."""
    address: str
    type: str = "personal"  # personal, work, other
    
    def to_dict(self) -> dict:
        return {"address": self.address, "type": self.type}
    
    @classmethod
    def from_dict(cls, data: dict) -> "EmailAddress":
        return cls(address=data.get("address", ""), type=data.get("type", "personal"))


@dataclass
class SocialMedia:
    """Social media-profil."""
    platform: str  # linkedin, twitter, facebook, instagram, telegram, signal, whatsapp, github, website
    username: str  # Användarnamn eller URL
    
    def to_dict(self) -> dict:
        return {"platform": self.platform, "username": self.username}
    
    @classmethod
    def from_dict(cls, data: dict) -> "SocialMedia":
        return cls(platform=data.get("platform", ""), username=data.get("username", ""))
    
    def get_url(self) -> str:
        """Returnerar fullständig URL för plattformen."""
        username = self.username.strip()
        
        # Om redan en URL, returnera direkt
        if username.startswith("http://") or username.startswith("https://"):
            return username
        
        # Ta bort @ om det finns i början
        if username.startswith("@"):
            username = username[1:]
        
        urls = {
            "linkedin": f"https://linkedin.com/in/{username}",
            "twitter": f"https://twitter.com/{username}",
            "x": f"https://x.com/{username}",
            "facebook": f"https://facebook.com/{username}",
            "instagram": f"https://instagram.com/{username}",
            "github": f"https://github.com/{username}",
            "telegram": f"https://t.me/{username}",
            "whatsapp": f"https://wa.me/{username.replace('+', '').replace(' ', '')}",
            "signal": f"https://signal.me/#p/{username}",
            "website": username if username.startswith("http") else f"https://{username}",
        }
        return urls.get(self.platform.lower(), username)
    
    def get_icon(self) -> str:
        """Returnerar emoji-ikon för plattformen."""
        icons = {
            "linkedin": "💼",
            "twitter": "🐦",
            "x": "𝕏",
            "facebook": "📘",
            "instagram": "📷",
            "github": "🐙",
            "telegram": "✈️",
            "whatsapp": "💬",
            "signal": "🔒",
            "website": "🌐",
        }
        return icons.get(self.platform.lower(), "🔗")


@dataclass
class Contact:
    """
    Kontaktmodell med alla fält.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    phones: list[PhoneNumber] = field(default_factory=list)
    emails: list[EmailAddress] = field(default_factory=list)
    street: str = ""  # Gatuadress
    postal_code: str = ""  # Postnummer
    city: str = ""  # Ort
    country: str = ""  # Land (valfritt)
    company: str = ""
    title: str = ""
    birthday: str = ""  # ISO format: YYYY-MM-DD
    notes: str = ""
    tags: list[str] = field(default_factory=list)
    social_media: list[SocialMedia] = field(default_factory=list)  # LinkedIn, Twitter, etc.
    photo: Optional[str] = None  # Base64-kodad bild
    is_favorite: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Konverterar till dictionary för serialisering."""
        return {
            "id": self.id,
            "name": self.name,
            "phones": [p.to_dict() for p in self.phones],
            "emails": [e.to_dict() for e in self.emails],
            "street": self.street,
            "postal_code": self.postal_code,
            "city": self.city,
            "country": self.country,
            "company": self.company,
            "title": self.title,
            "birthday": self.birthday,
            "notes": self.notes,
            "tags": self.tags,
            "social_media": [s.to_dict() for s in self.social_media],
            "photo": self.photo,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        """Skapar Contact från dictionary."""
        phones = [PhoneNumber.from_dict(p) for p in data.get("phones", [])]
        emails = [EmailAddress.from_dict(e) for e in data.get("emails", [])]
        social_media = [SocialMedia.from_dict(s) for s in data.get("social_media", [])]
        
        # Bakåtkompatibilitet: om "address" finns men inte nya fält, migrera
        street = data.get("street", "")
        postal_code = data.get("postal_code", "")
        city = data.get("city", "")
        country = data.get("country", "")
        
        if not street and "address" in data and data["address"]:
            # Försök parsa gammal adress (gata, postnr ort)
            old_addr = data["address"]
            street = old_addr  # Sätt hela som gata som fallback
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            phones=phones,
            emails=emails,
            street=street,
            postal_code=postal_code,
            city=city,
            country=country,
            company=data.get("company", ""),
            title=data.get("title", ""),
            birthday=data.get("birthday", ""),
            notes=data.get("notes", ""),
            tags=data.get("tags", []),
            social_media=social_media,
            photo=data.get("photo"),
            is_favorite=data.get("is_favorite", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )
    
    def get_primary_phone(self) -> str:
        """Returnerar första telefonnumret eller tom sträng."""
        if self.phones:
            return self.phones[0].number
        return ""
    
    def get_primary_email(self) -> str:
        """Returnerar första e-postadressen eller tom sträng."""
        if self.emails:
            return self.emails[0].address
        return ""
    
    def matches_search(self, query: str) -> bool:
        """
        Kontrollerar om kontakten matchar sökfråga.
        Söker i: namn, telefon, e-post, företag, taggar.
        """
        query_lower = query.lower()
        
        # Sök i namn
        if query_lower in self.name.lower():
            return True
        
        # Sök i telefonnummer (ta bort mellanslag för matchning)
        for phone in self.phones:
            if query_lower in phone.number.replace(" ", "").lower():
                return True
        
        # Sök i e-post
        for email in self.emails:
            if query_lower in email.address.lower():
                return True
        
        # Sök i företag
        if query_lower in self.company.lower():
            return True
        
        # Sök i titel
        if query_lower in self.title.lower():
            return True
        
        # Sök i taggar
        for tag in self.tags:
            if query_lower in tag.lower():
                return True
        
        return False
    
    def touch(self):
        """Uppdaterar updated_at till nu."""
        self.updated_at = datetime.now().isoformat()


@dataclass
class DatabaseMetadata:
    """Metadata om databasen."""
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    backup_path: str = ""
    auto_backup: bool = True
    language: str = "sv"  # sv = svenska, en = engelska (brittisk)
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "backup_path": self.backup_path,
            "auto_backup": self.auto_backup,
            "language": self.language,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DatabaseMetadata":
        return cls(
            version=data.get("version", "1.0"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            backup_path=data.get("backup_path", ""),
            auto_backup=data.get("auto_backup", True),
            language=data.get("language", "sv"),
        )


@dataclass
class DatabaseData:
    """
    Komplett databasstruktur.
    Detta är vad som serialiseras och krypteras.
    """
    metadata: DatabaseMetadata = field(default_factory=DatabaseMetadata)
    contacts: list[Contact] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)  # Alla unika taggar
    verification: bytes = b""  # Verifieringsdata för lösenord
    
    def to_json(self) -> str:
        """Serialiserar till JSON."""
        data = {
            "metadata": self.metadata.to_dict(),
            "contacts": [c.to_dict() for c in self.contacts],
            "tags": self.tags,
            "verification": base64.b64encode(self.verification).decode('utf-8') if self.verification else "",
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def to_bytes(self) -> bytes:
        """Serialiserar till bytes för kryptering."""
        return self.to_json().encode('utf-8')
    
    @classmethod
    def from_json(cls, json_str: str) -> "DatabaseData":
        """Deserialiserar från JSON."""
        data = json.loads(json_str)
        
        metadata = DatabaseMetadata.from_dict(data.get("metadata", {}))
        contacts = [Contact.from_dict(c) for c in data.get("contacts", [])]
        tags = data.get("tags", [])
        verification = base64.b64decode(data.get("verification", "")) if data.get("verification") else b""
        
        return cls(
            metadata=metadata,
            contacts=contacts,
            tags=tags,
            verification=verification,
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> "DatabaseData":
        """Deserialiserar från bytes."""
        return cls.from_json(data.decode('utf-8'))
    
    def update_tags(self):
        """Uppdaterar tagglistan baserat på kontakternas taggar."""
        all_tags = set()
        for contact in self.contacts:
            all_tags.update(contact.tags)
        self.tags = sorted(list(all_tags))
    
    def get_contact_by_id(self, contact_id: str) -> Optional[Contact]:
        """Hämtar kontakt via ID."""
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None
    
    def add_contact(self, contact: Contact) -> Contact:
        """Lägger till kontakt och uppdaterar taggar."""
        self.contacts.append(contact)
        self.update_tags()
        return contact
    
    def update_contact(self, contact: Contact) -> bool:
        """Uppdaterar befintlig kontakt."""
        for i, c in enumerate(self.contacts):
            if c.id == contact.id:
                contact.touch()
                self.contacts[i] = contact
                self.update_tags()
                return True
        return False
    
    def delete_contact(self, contact_id: str) -> bool:
        """Tar bort kontakt."""
        for i, contact in enumerate(self.contacts):
            if contact.id == contact_id:
                del self.contacts[i]
                self.update_tags()
                return True
        return False
    
    def search_contacts(
        self,
        query: str = "",
        tag_filter: Optional[str] = None,
        favorites_only: bool = False,
        sort_by: str = "name"
    ) -> list[Contact]:
        """
        Söker och filtrerar kontakter.
        
        Args:
            query: Söktext (matchar namn, telefon, e-post, företag)
            tag_filter: Filtrera på specifik tagg
            favorites_only: Visa endast favoriter
            sort_by: Sorteringskolumn (name, company, updated_at)
        
        Returns:
            Lista med matchande kontakter
        """
        results = self.contacts.copy()
        
        # Sökfilter
        if query:
            results = [c for c in results if c.matches_search(query)]
        
        # Taggfilter
        if tag_filter:
            results = [c for c in results if tag_filter in c.tags]
        
        # Favoritfilter
        if favorites_only:
            results = [c for c in results if c.is_favorite]
        
        # Sortering
        if sort_by == "name":
            results.sort(key=lambda c: c.name.lower())
        elif sort_by == "company":
            results.sort(key=lambda c: (c.company.lower(), c.name.lower()))
        elif sort_by == "updated_at":
            results.sort(key=lambda c: c.updated_at, reverse=True)
        
        return results
