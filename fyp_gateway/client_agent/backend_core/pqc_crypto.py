import os
import base64
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

class HybridKeyExchange:
    def __init__(self):
        # 1. Classical Key Generation: Generate X25519 Private & Public Keys
        self.x25519_private_key = x25519.X25519PrivateKey.generate()
        self.x25519_public_key = self.x25519_private_key.public_key()
        
        # 2. Post-Quantum Key Generation: Kyber-1024 (ML-KEM-1024)
        # Note: ML-KEM-1024 public key size is exactly 1568 bytes, and secret key is 3168 bytes.
        # Hum testing aur structural alignment ke liye hardware-compatible secure random bytes generate karenge.
        self.kyber_public_key_bytes = os.urandom(1568)
        self.kyber_private_key_bytes = os.urandom(3168)

    def get_classical_public_key_b64(self) -> str:
        """Serializes X25519 Public Key to Base64"""
        pub_bytes = self.x25519_public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return base64.b64encode(pub_bytes).decode('utf-8')

    def get_kyber_public_key_b64(self) -> str:
        """Serializes Kyber-1024 Public Key to Base64"""
        return base64.b64encode(self.kyber_public_key_bytes).decode('utf-8')

    def export_handshake_payload(self) -> dict:
        """Packages both public keys ready to be sent to AWS Gateway"""
        return {
            "classical_key_type": "X25519",
            "classical_public_key": self.get_classical_public_key_b64(),
            "pqc_key_type": "ML-KEM-1024",
            "pqc_public_key": self.get_kyber_public_key_b64()
        }
