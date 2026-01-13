"""
Krypteringshantering för KontaktRegister.

Säkerhetsarkitektur:
- KDF: Argon2id (minneshard, motståndskraftig mot GPU/ASIC-attacker)
- Kryptering: AES-256-GCM (authenticated encryption with associated data)
- Salt: 16 bytes kryptografiskt slumpmässigt per databas
- Nonce: 12 bytes slumpmässigt per krypteringsoperation

Dataformat (krypterad fil):
[VERSION: 1 byte][SALT: 16 bytes][NONCE: 12 bytes][CIPHERTEXT][AUTH_TAG: 16 bytes]
"""

import os
import re
import secrets
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2 import PasswordHasher
from argon2.low_level import Type, hash_secret_raw

from config import (
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_HASH_LEN,
    SALT_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
)

logger = logging.getLogger(__name__)

# Filformat-version (för framtida kompatibilitet)
CRYPTO_VERSION = b'\x01'


@dataclass
class PasswordStrength:
    """Resultat av lösenordsstyrkeanalys."""
    score: int  # 0-4 (0=mycket svagt, 4=mycket starkt)
    label: str  # "Mycket svagt", "Svagt", etc.
    feedback: list[str]  # Förbättringsförslag
    is_valid: bool  # Uppfyller minimikrav


class PasswordValidator:
    """Validerar och analyserar lösenordsstyrka."""
    
    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        """
        Validerar att lösenordet uppfyller minimikraven.
        
        Returns:
            (is_valid, error_message)
        """
        if len(password) < PASSWORD_MIN_LENGTH:
            return False, f"Lösenordet måste vara minst {PASSWORD_MIN_LENGTH} tecken"
        
        if len(password) > PASSWORD_MAX_LENGTH:
            return False, f"Lösenordet får vara max {PASSWORD_MAX_LENGTH} tecken"
        
        if not re.search(r'[a-zA-Z]', password):
            return False, "Lösenordet måste innehålla minst en bokstav"
        
        if not re.search(r'\d', password):
            return False, "Lösenordet måste innehålla minst en siffra"
        
        return True, ""
    
    @staticmethod
    def analyze_strength(password: str) -> PasswordStrength:
        """
        Analyserar lösenordsstyrka och ger feedback.
        
        Returnerar en PasswordStrength med:
        - score: 0-4
        - label: Beskrivning
        - feedback: Förbättringsförslag
        - is_valid: Om det uppfyller minimikrav
        """
        is_valid, error = PasswordValidator.validate(password)
        
        score = 0
        feedback = []
        
        if not is_valid:
            feedback.append(error)
        
        # Längdpoäng
        length = len(password)
        if length >= 12:
            score += 2
        elif length >= 9:
            score += 1
        else:
            feedback.append("Längre lösenord är säkrare")
        
        # Teckenvariationspoäng
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', password))
        
        variety = sum([has_lower, has_upper, has_digit, has_special])
        
        if variety >= 4:
            score += 2
        elif variety >= 3:
            score += 1
        
        if not has_upper and has_lower:
            feedback.append("Lägg till versaler")
        if not has_special:
            feedback.append("Lägg till specialtecken")
        
        # Kontrollera vanliga mönster
        common_patterns = [
            r'12345', r'qwerty', r'password', r'lösenord',
            r'(.)\1{2,}',  # Upprepade tecken
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                score = max(0, score - 1)
                feedback.append("Undvik vanliga mönster")
                break
        
        # Begränsa score till 0-4
        score = max(0, min(4, score))
        
        # Sätt etikett
        labels = ["Mycket svagt", "Svagt", "Medel", "Starkt", "Mycket starkt"]
        label = labels[score]
        
        return PasswordStrength(
            score=score,
            label=label,
            feedback=feedback[:3],  # Max 3 förslag
            is_valid=is_valid
        )


class CryptoManager:
    """
    Hanterar kryptering och dekryptering av data.
    
    Använder:
    - Argon2id för nyckelderivering (minneshard KDF)
    - AES-256-GCM för authenticated encryption
    """
    
    def __init__(self):
        self._key: Optional[bytes] = None
        self._salt: Optional[bytes] = None
    
    @property
    def is_initialized(self) -> bool:
        """Returnerar True om krypteringsnyckeln är laddad."""
        return self._key is not None
    
    def generate_salt(self) -> bytes:
        """Genererar ett kryptografiskt säkert salt."""
        return secrets.token_bytes(SALT_LENGTH)
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Deriverar en krypteringsnyckel från lösenord med Argon2id.
        
        Args:
            password: Användarens lösenord
            salt: Unikt salt för denna databas
            
        Returns:
            32-byte nyckel för AES-256
        """
        key = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=ARGON2_TIME_COST,
            memory_cost=ARGON2_MEMORY_COST,
            parallelism=ARGON2_PARALLELISM,
            hash_len=ARGON2_HASH_LEN,
            type=Type.ID  # Argon2id
        )
        return key
    
    def initialize_new(self, password: str) -> bytes:
        """
        Initialiserar kryptering för en ny databas.
        
        Args:
            password: Användarens valda lösenord
            
        Returns:
            Salt som ska sparas med databasen
        """
        self._salt = self.generate_salt()
        self._key = self.derive_key(password, self._salt)
        logger.info("Kryptering initialiserad för ny databas")
        return self._salt
    
    def initialize_existing(self, password: str, salt: bytes) -> bool:
        """
        Initialiserar kryptering för befintlig databas.
        
        Args:
            password: Användarens lösenord
            salt: Salt från databasen
            
        Returns:
            True (verifiering görs separat via verify_password)
        """
        self._salt = salt
        self._key = self.derive_key(password, salt)
        return True
    
    def create_verification_data(self) -> bytes:
        """
        Skapar verifieringsdata som kan användas för att kontrollera
        att rätt lösenord angetts.
        
        Returns:
            Krypterad verifieringssträng
        """
        if not self._key:
            raise RuntimeError("Kryptering inte initialiserad")
        
        # Kryptera en känd sträng
        verification_plaintext = b"KONTAKTREGISTER_VERIFICATION_V1"
        return self.encrypt(verification_plaintext)
    
    def verify_password(self, verification_data: bytes) -> bool:
        """
        Verifierar att lösenordet är korrekt genom att dekryptera
        verifieringsdata.
        
        Args:
            verification_data: Data skapad av create_verification_data
            
        Returns:
            True om lösenordet är korrekt
        """
        if not self._key:
            raise RuntimeError("Kryptering inte initialiserad")
        
        try:
            plaintext = self.decrypt(verification_data)
            return plaintext == b"KONTAKTREGISTER_VERIFICATION_V1"
        except Exception:
            return False
    
    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Krypterar data med AES-256-GCM.
        
        Args:
            plaintext: Data att kryptera
            
        Returns:
            Krypterad data med nonce prepended
        """
        if not self._key:
            raise RuntimeError("Kryptering inte initialiserad")
        
        # Generera unik nonce för varje kryptering
        nonce = secrets.token_bytes(12)  # 96 bitar för GCM
        
        aesgcm = AESGCM(self._key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # Format: nonce || ciphertext (inkluderar auth tag)
        return nonce + ciphertext
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Dekrypterar AES-256-GCM-krypterad data.
        
        Args:
            ciphertext: Krypterad data (nonce || ciphertext || tag)
            
        Returns:
            Dekrypterad plaintext
            
        Raises:
            cryptography.exceptions.InvalidTag: Om dekryptering misslyckas
        """
        if not self._key:
            raise RuntimeError("Kryptering inte initialiserad")
        
        # Extrahera nonce (första 12 bytes)
        nonce = ciphertext[:12]
        actual_ciphertext = ciphertext[12:]
        
        aesgcm = AESGCM(self._key)
        return aesgcm.decrypt(nonce, actual_ciphertext, None)
    
    def encrypt_file_data(self, data: bytes) -> bytes:
        """
        Krypterar data för fillagring med version och salt.
        
        Format: VERSION || SALT || ENCRYPTED_DATA
        
        Args:
            data: Data att kryptera
            
        Returns:
            Komplett krypterad fil-payload
        """
        if not self._key or not self._salt:
            raise RuntimeError("Kryptering inte initialiserad")
        
        encrypted = self.encrypt(data)
        return CRYPTO_VERSION + self._salt + encrypted
    
    def decrypt_file_data(self, file_data: bytes, password: str) -> bytes:
        """
        Dekrypterar fildata och initialiserar kryptering.
        
        Args:
            file_data: Komplett fil-payload
            password: Användarens lösenord
            
        Returns:
            Dekrypterad data
            
        Raises:
            ValueError: Om filformat är ogiltigt
            cryptography.exceptions.InvalidTag: Om lösenord är fel
        """
        if len(file_data) < 1 + SALT_LENGTH + 12 + 16:
            raise ValueError("Ogiltig fildata: för kort")
        
        # Extrahera komponenter
        version = file_data[0:1]
        if version != CRYPTO_VERSION:
            raise ValueError(f"Okänd filversion: {version}")
        
        salt = file_data[1:1 + SALT_LENGTH]
        encrypted_data = file_data[1 + SALT_LENGTH:]
        
        # Initiera med lösenord och salt
        self.initialize_existing(password, salt)
        
        # Dekryptera
        return self.decrypt(encrypted_data)
    
    def clear(self):
        """
        Rensar känsligt nyckelmaterial från minnet.
        
        OBS: Python har ingen garanterad säker minnesrensning,
        men vi gör vårt bästa genom att skriva över och ta bort referensen.
        """
        if self._key:
            # Skriv över med slumpmässiga bytes
            key_len = len(self._key)
            self._key = secrets.token_bytes(key_len)
            self._key = None
        
        if self._salt:
            salt_len = len(self._salt)
            self._salt = secrets.token_bytes(salt_len)
            self._salt = None
        
        logger.debug("Nyckelmaterial rensat från minnet")
    
    def __del__(self):
        """Rensa nycklar vid destruktion."""
        self.clear()
