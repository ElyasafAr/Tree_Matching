from cryptography.fernet import Fernet
from config import Config

class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        encryption_key = Config.ENCRYPTION_KEY
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY not found in environment variables")
        
        # Convert string key to bytes if needed
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        self.cipher = Fernet(encryption_key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string and return as base64 encoded string"""
        if not data:
            return None
        
        encrypted_bytes = self.cipher.encrypt(data.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a base64 encoded string and return original string"""
        if not encrypted_data:
            return None
        
        decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()

# Singleton instance
encryption_service = EncryptionService()

