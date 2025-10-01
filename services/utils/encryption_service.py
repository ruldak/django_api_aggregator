# install di requirements.txt
# cryptography==3.4.8

# services/encryption_service.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from django.conf import settings

class EncryptionService:
    def __init__(self):
        # Generate key dari Django SECRET_KEY
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=settings.SECRET_KEY.encode()[:16].ljust(16, b'0'),
            iterations=100000,
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        self.fernet = Fernet(self.key)

    def encrypt(self, text):
        """Encrypt text dan return base64 string"""
        if not text:
            return None
        encrypted = self.fernet.encrypt(text.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_text):
        """Decrypt base64 encoded encrypted text"""
        if not encrypted_text:
            return None
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            return None

# Singleton instance
encryption_service = EncryptionService()
