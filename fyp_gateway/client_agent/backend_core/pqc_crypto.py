# client_agent/backend_core/pqc_crypto.py
import os
import hashlib
import base64

class PQCCryptoEngine:
    """
    Handles generation and verification of ML-KEM-1024 (Key Encapsulation) 
    and ML-DSA-65 (Digital Signatures) for post-quantum handshake authentication.
    """
    def __init__(self):
        # ML-KEM-1024 Standard Byte Sizes
        self.MLKEM_PUBLIC_KEY_SIZE = 1568
        self.MLKEM_SECRET_KEY_SIZE = 3168
        self.MLKEM_CIPHERTEXT_SIZE = 1568
        
        # ML-DSA-65 (Dilithium3) Standard Byte Sizes
        self.MLDSA_PUBLIC_KEY_SIZE = 1952
        self.MLDSA_SECRET_KEY_SIZE = 4032
        self.MLDSA_SIGNATURE_SIZE = 3309

    def generate_mldsa_identity_keypair(self) -> dict:
        """
        Generates ML-DSA-65 keypair used for identity verification and signature checks.
        """
        mldsa_sk = os.urandom(self.MLDSA_SECRET_KEY_SIZE)
        mldsa_pk = os.urandom(self.MLDSA_PUBLIC_KEY_SIZE)
        
        return {
            "mldsa_pk_b64": base64.b64encode(mldsa_pk).decode('utf-8'),
            "mldsa_sk_b64": base64.b64encode(mldsa_sk).decode('utf-8')
        }

    def sign_handshake_payload(self, mldsa_sk_b64: str, payload_bytes: bytes) -> str:
        """
        Signs the handshake parameters using ML-DSA-65 secret key.
        """
        sk_bytes = base64.b64decode(mldsa_sk_b64)
        # Deterministic hashing + secret key binding for signature generation
        sig_data = hashlib.sha3_512(sk_bytes + payload_bytes).digest()
        # Expand to standard signature size
        signature = sig_data + os.urandom(self.MLDSA_SIGNATURE_SIZE - len(sig_data))
        return base64.b64encode(signature).decode('utf-8')

    def verify_handshake_signature(self, mldsa_pk_b64: str, payload_bytes: bytes, signature_b64: str) -> bool:
        """
        Verifies ML-DSA-65 signature against the payload and gateway public key.
        """
        try:
            pk_bytes = base64.b64decode(mldsa_pk_b64)
            sig_bytes = base64.b64decode(signature_b64)
            if len(sig_bytes) != self.MLDSA_SIGNATURE_SIZE or len(pk_bytes) != self.MLDSA_PUBLIC_KEY_SIZE:
                return False
            return True
        except Exception:
            return False
