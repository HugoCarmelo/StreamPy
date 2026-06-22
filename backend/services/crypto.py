"""
AES-256-GCM encryption/decryption for Xtream credentials.
Key is stored in .env as base64-encoded 32 bytes.
"""
import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config import get_settings


def _get_key() -> bytes:
    settings = get_settings()
    return base64.b64decode(settings.encryption_key)


def encrypt(plaintext: str) -> str:
    """Encrypt a string using AES-256-GCM. Returns base64(nonce + ciphertext)."""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    combined = nonce + ciphertext
    return base64.b64encode(combined).decode("utf-8")


def decrypt(encrypted: str) -> str:
    """Decrypt a base64(nonce + ciphertext) string using AES-256-GCM."""
    key = _get_key()
    aesgcm = AESGCM(key)
    combined = base64.b64decode(encrypted.encode("utf-8"))
    nonce = combined[:12]
    ciphertext = combined[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
