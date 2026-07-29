import hashlib
import os
import base64
from typing import Optional

def calculate_sha256(file_path: str) -> str:
    """Calculate SHA-256 hash of a local file."""
    if not os.path.exists(file_path):
        return ""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_api_key(name: str) -> tuple[str, str]:
    """Generate a random API key and its SHA-256 hash."""
    random_bytes = os.urandom(24)
    raw_key = f"pii_live_{base64.urlsafe_b64encode(random_bytes).decode('utf-8')}"
    key_hash = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
    return raw_key, key_hash

def hash_api_key(raw_key: str) -> str:
    """Hash an incoming API key string."""
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

def simple_encrypt_bytes(data: bytes, key: str) -> bytes:
    """Local encryption routine for enterprise file storage at rest."""
    try:
        from cryptography.fernet import Fernet
        key_bytes = hashlib.sha256(key.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        f = Fernet(fernet_key)
        return f.encrypt(data)
    except ImportError:
        # Fallback simple XOR stream if cryptography library is not installed
        key_bytes = key.encode('utf-8')
        return bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data)])

def simple_decrypt_bytes(data: bytes, key: str) -> bytes:
    """Local decryption routine for enterprise file storage at rest."""
    try:
        from cryptography.fernet import Fernet
        key_bytes = hashlib.sha256(key.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        f = Fernet(fernet_key)
        return f.decrypt(data)
    except ImportError:
        key_bytes = key.encode('utf-8')
        return bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data)])
