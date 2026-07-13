# client_agent/backend_core/local_api.py
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import platform
from hybrid_client_kdf import HybridCryptoEngine

app = FastAPI(title="PQ-Tunnel Local Orchestrator")

# Enable CORS so Electron GUI can seamlessly talk to this python process
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

crypto_engine = HybridCryptoEngine()

# TARGET LOCK: Your actual live AWS EC2 Public Gateway Interface
AWS_GATEWAY_URL = "http://107.21.77.85:8000" 

@app.get("/v1/client/status")
def get_local_status():
    """
    Auto-detects host environment characteristics dynamically.
    Useful for verification loops on your ThinkPad (Windows vs Linux VM).
    """
    return {
        "agent_status": "READY",
        "operating_system": platform.system(),  # Will return 'Windows' or 'Linux'
        "architecture": platform.machine()
    }

@app.post("/v1/client/connect")
def initiate_tunnel_sequence():
    """
    Orchestrates cross-platform connection sequences:
    Generates Local PQC states -> Updates AWS Gateway over Internet -> Secures Tunnel Data
    """
    try:
        print(f"\n[*] Electron GUI triggered handshake chain on target platform: {platform.system()}")
        
        # 1. Connection Health Check over Broad Internet
        status_check = requests.get(f"{AWS_GATEWAY_URL}/v1/gateway/status", timeout=6)
        if status_check.status_code != 200:
            raise HTTPException(status_code=502, detail="Cloud AWS Gateway interface unreachable.")
            
        # 2. Cryptographic Generation Primitives
        priv_x, pub_x = crypto_engine.generate_classical_ephemeral()
        ct, pqc_secret = crypto_engine.simulate_ml_kem_encapsulation()
        
        # 3. Step 1 Flight: Identity Allocation Session
        reg_payload = {
            "client_id": f"ThinkPad-{platform.system()}-Node",
            "mldsa_public_key": os.urandom(1312).hex(),  # Simulated ML-DSA-87 public key
            "classical_public_key": pub_x.hex()
        }
        
        print(f"[*] Dispatching registration payload to: {AWS_GATEWAY_URL}/v1/gateway/register")
        reg_resp = requests.post(f"{AWS_GATEWAY_URL}/v1/gateway/register", json=reg_payload)
        virtual_ip = reg_resp.json().get("assigned_virtual_ip", "10.8.0.2")
        
        # 4. Step 2 Flight: Hybrid Key Exchange Implementation
        handshake_payload = {
            "client_id": f"ThinkPad-{platform.system()}-Node",
            "mldem_ciphertext": ct.hex(),
            "ecdh_public_key": pub_x.hex(),
            "client_signature": os.urandom(64).hex() 
        }
        
        print(f"[*] Dispatching key exchange payload to: {AWS_GATEWAY_URL}/v1/gateway/handshake")
        handshake_resp = requests.post(f"{AWS_GATEWAY_URL}/v1/gateway/handshake", json=handshake_payload)
        
        return {
            "status": "SUCCESS",
            "assigned_ip": virtual_ip,
            "gateway_response": handshake_resp.json()
        }
        
    except Exception as e:
        print(f"[-] Execution Failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Local runtime bridge listener active on port 8001
    uvicorn.run(app, host="127.0.0.1", port=8001)
