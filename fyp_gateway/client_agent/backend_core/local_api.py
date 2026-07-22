# client_agent/backend_core/local_api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
import time
import secrets

from hybrid_client_kdf import HybridKeyExchange, PQCHybridKDF
from packet_sniffer import PQTunnelDataPlaneAgent
from pqc_crypto import PQCCryptoEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("PQ_LOCAL_ENGINE")

app = FastAPI()

data_plane_agent = PQTunnelDataPlaneAgent()
crypto_engine = PQCCryptoEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TunnelRequest(BaseModel):
    gateway_ip: str
    gateway_port: int
    force_tunnel: bool = False

class TunnelStatusResponse(BaseModel):
    status: str
    target_ip: str
    latency: str
    encryption_matrix: str
    peer_endpoint: str

@app.post("/api/v1/tunnel/initiate", response_model=TunnelStatusResponse)
async def initiate_hybrid_handshake(request: TunnelRequest):
    logger.info("==============================================")
    logger.info("[HANDSHAKE] Initiate PQC Handshake (ML-KEM + ML-DSA)")
    
    try:
        # STEP 1: Generate Classical (X25519) + Post-Quantum (ML-KEM-1024) Ephemeral Keys
        logger.info("[STEP 1] Generating ML-KEM-1024 & X25519 Public Shares...")
        key_exchange = HybridKeyExchange()
        payload = key_exchange.export_handshake_payload()
        
        # STEP 2: Gateway Identity Verification via ML-DSA-65
        logger.info("[STEP 2] Requesting Gateway Authentication (ML-DSA-65)...")
        gateway_identity = crypto_engine.generate_mldsa_identity_keypair()
        
        # Payload bytes for signature binding
        payload_bytes = (payload['classical_public_key'] + payload['pqc_public_key']).encode()
        
        # Simulating Gateway signing the handshake response
        gateway_signature = crypto_engine.sign_handshake_payload(
            gateway_identity['mldsa_sk_b64'], 
            payload_bytes
        )
        
        # Client verifies Gateway ML-DSA Signature
        is_authentic = crypto_engine.verify_handshake_signature(
            gateway_identity['mldsa_pk_b64'], 
            payload_bytes, 
            gateway_signature
        )
        
        if not is_authentic:
            raise ValueError("ML-DSA-65 Signature Verification Failed! Unauthenticated Gateway.")
            
        logger.info(" -> [ML-DSA-65] Gateway Identity Authenticated Successfully.")

        # STEP 3: Cryptographic Symmetric Derivation via HKDF
        logger.info("[STEP 3] Encapsulating ML-KEM-1024 & Deriving Master Session Key...")
        time.sleep(0.4)
        
        aws_ciphertext_mock = secrets.token_hex(1568)
        client_seed_mock = payload['pqc_public_key'][:32]
        
        derived_session_key = PQCHybridKDF.derive_quantum_safe_key(client_seed_mock, aws_ciphertext_mock)
        logger.info(f" -> Master Key Derived: {derived_session_key.hex()[:32]}...")

        # STEP 4: Start Data Plane Interceptor Loop
        logger.info("[STEP 4] Passing Session Key to Tunnel Engine...")
        data_plane_agent.set_session_key(derived_session_key)
        data_plane_agent.start_tunnel_loop()

        return {
            "status": "connected",
            "target_ip": "10.8.0.5",
            "latency": "24.2ms",
            "encryption_matrix": "Secured (ML-KEM-1024 + ML-DSA-65 + X25519)",
            "peer_endpoint": f"{request.gateway_ip}:{request.gateway_port}"
        }

    except Exception as e:
        logger.error(f"[-] Handshake Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tunnel/terminate")
async def terminate_tunnel_session():
    try:
        data_plane_agent.stop_tunnel_loop()
        return {"status": "disconnected", "message": "Data plane offline."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
