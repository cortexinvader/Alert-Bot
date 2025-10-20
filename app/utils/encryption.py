import crypto
import os

ENCRYPTION_KEY = os.getenv('SECRET_KEY', 'default-encryption-key')[:32]

def encrypt_data(data: str) -> str:
    return crypto.encrypt(data, ENCRYPTION_KEY)

def decrypt_data(encrypted: str) -> str:
    return crypto.decrypt(encrypted, ENCRYPTION_KEY)

def load_env_encrypted(key: str, default: str = '') -> str:
    value = os.getenv(key, default)
    if value and value.startswith('ENC:'):
        return decrypt_data(value[4:])
    return value
