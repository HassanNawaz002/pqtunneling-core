import os
import sys
import logging
import ctypes
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import our custom Stage 1 Hybrid Cryptography module
try:
    from pqc_crypto import HybridKeyExchange
except ImportError:
    # Fallback to make sure path resolution works if executed from parent directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from pqc_crypto import HybridKeyExchange

# Configure logging to write clean visual outputs to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = FastAPI(title="Post-Quantum Tunneling - Local Client Core")

# Enable CORS so our Electron UI can securely fetch data on port 8001
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# DATA VALIDATION SCHEMAS
# =====================================================================
class TunnelRequest(BaseModel):
    gateway_ip: str
    gateway_port: int
    force_tunnel: bool

# =====================================================================
# UTILITY: PLATFORM SPECIFIC PRIVILEGE DETECTION
# =====================================================================
def is_running_as_admin() -> bool:
    """
    Evaluates whether the executing process has administrative/root permissions.
    """
    try:
        # For Windows environments
        if os.name == 'nt':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        # For Linux / POSIX environments
        else:
            return os.getuid() == 0
    except Exception as e:
        logging.error(f"[-] Privilege check execution error: {str(e)}")
        return False

# =====================================================================
# SYSTEM API ENDPOINTS
# =====================================================================
@app.get("/api/v1/system/privilege-check")
async def privilege_check():
    """
    Electron GUI polls this endpoint on boot and before tunnel initiation
    to verify network adapter capability.
    """
    has_elevation = is_running_as_admin()
    logging.info(f"Privilege check invoked. Result: Elevated={has_elevation} (OS: {os.name})")
    return {"has_root_privileges": has_elevation}

@app.post("/api/v1/tunnel/initiate")
async def initiate_tunnel(payload: TunnelRequest):
    """
    Stage 1: Generates client-side Classical (X25519) and Post-Quantum (ML-KEM-1024)
    public keys, packaging them dynamically to transition into the handshake phase.
    """
    # Hard enforcement: Block execution if backend does not possess administrative capabilities
    if not is_running_as_admin():
        logging.warning("[!] BLOCKED: Tunnel initiation attempt without Root/Admin rights.")
        raise HTTPException(
            status_code=403, 
            detail="Forbidden: Administrative privileges are required to initialize the virtual TUN adapter."
        )

    logging.info(f"[STAGE 1] Triggering Hybrid Handshake with Gateway {payload.gateway_ip}:{payload.gateway_port}...")
    
    try:
        # 1. Instantiate the Hybrid Cryptography Keys (X25519 + Kyber-1024)
        hybrid_handshake = HybridKeyExchange()
        client_keys = hybrid_handshake.export_handshake_payload()
        
        # Log the generated keys on the local core terminal for verification
        logging.info(f"[STAGE 1] Generated Classical X25519 Public Key: {client_keys['classical_public_key'][:25]}... (Base64)")
        logging.info(f"[STAGE 1] Generated Post-Quantum ML-KEM-1024 Public Key: {client_keys['pqc_public_key'][:25]}... (Base64)")

        # 2. Return response payload to Electron GUI to confirm success
        return {
            "status": "success",
            "target_ip": "10.8.0.5",
            "encryption_matrix": "ML-KEM-1024 + X25519 (Hybrid)", # Matches architecture flow[cite: 3]
            "client_public_keys": client_keys
        }

    except Exception as e:
        logging.error(f"[STAGE 1 ERROR] Hybrid Key Generation failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Stage 1 Hybrid Key Generation Failed: {str(e)}"
        )

# =====================================================================
# CORE BOOTSTRAP
# =====================================================================
if __name__ == "__main__":
    # Log privilege status directly onto command terminal startup
    if is_running_as_admin():
        logging.info("[+] SUCCESS: API running with elevated (Root/Admin) privileges. Ready to control network layers!")
    else:
        logging.warning("[-] WARNING: Running as non-root user. Network adapter operations will be locked.")

    import uvicorn
    logging.info("Starting local backend server on http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)
