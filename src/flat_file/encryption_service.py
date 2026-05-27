import base64
import hashlib
import hmac as hmac_module
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Felter der indeholder persondata og skal krypteres i JSON-filen
ENCRYPTED_FIELDS = ["first_name", "last_name", "address", "street_number"]


class Encryption_service:
    def __init__(self, aes_key: bytes, hmac_secret: bytes):
        if len(aes_key) != 32:
            raise ValueError("AES-nøglen skal være præcis 32 bytes (AES-256)")
        self.aes_key = aes_key
        self.hmac_secret = hmac_secret

    # ── Symmetrisk kryptering: AES-256 EAX ──────────────────────────────────
    # EAX-mode giver både fortrolighed og integritet (authenticated encryption).
    # Nonce (16 bytes) + tag (16 bytes) + ciphertext gemmes samlet i base64.

    def encrypt(self, plaintext: str) -> str:
        cipher = AES.new(self.aes_key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
        combined = cipher.nonce + tag + ciphertext
        return base64.b64encode(combined).decode("utf-8")

    def decrypt(self, token: str) -> str:
        combined = base64.b64decode(token.encode("utf-8"))
        nonce = combined[:16]
        tag = combined[16:32]
        ciphertext = combined[32:]
        cipher = AES.new(self.aes_key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode("utf-8")

    # ── Password hashing: HMAC-SHA256 med salt ───────────────────────────────
    # Salt (16 bytes, tilfældig) + HMAC-digest gemmes samlet i base64.
    # Saltet sikrer at to ens passwords giver forskellige hashes (ingen rainbow tables).

    def hash_password(self, password: str) -> str:
        salt = get_random_bytes(16)
        digest = hmac_module.new(
            self.hmac_secret, salt + password.encode("utf-8"), hashlib.sha256
        ).digest()
        return base64.b64encode(salt + digest).decode("utf-8")

    def verify_password(self, password: str, stored_hash: str) -> bool:
        data = base64.b64decode(stored_hash.encode("utf-8"))
        salt = data[:16]
        stored_digest = data[16:]
        new_digest = hmac_module.new(
            self.hmac_secret, salt + password.encode("utf-8"), hashlib.sha256
        ).digest()
        return hmac_module.compare_digest(stored_digest, new_digest)
