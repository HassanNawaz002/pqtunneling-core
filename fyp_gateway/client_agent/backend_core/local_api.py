import os
import sys
import ctypes
import logging
from typing import Optional
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Logging setup for easy debugging in terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = FastAPI(
    title="PQ Tunneling Client Core Local API",
    description="Local microservice driving the Electron GUI and managing the post-quantum secure tunnel client-side.",
    version="1.0.0"
)

# Enable CORS so Electron (running on custom protocols/localhost) can safely make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# PRIVILEGE DETECTION UTILITY
# ==========================================

def is_running_as_elevated() -> bool:
    """
    Checks if the backend API has root/administrator privileges.
    Required for virtual network interface (TUN/TAP) initialization.
    """
    try:
        if os.name == 'nt':
            # Windows Administrator Check
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # Linux/macOS Root Check (UID 0 is root)
            return os.getuid() == 0
    except Exception as e:
        logging.error(f"Error checking execution privileges: {e}")
        return False

# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class HandshakePayload(BaseModel):
    gateway_ip: str
    gateway_port: int
    force_tunnel: Optional[bool] = False

# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/")
def read_root():
    """Service health and identity endpoint."""
    return {
        "service": "PQ Tunneling Local Engine Core",
        "status": "online",
        "privilege_elevation_active": is_running_as_elevated()
    }


@app.get("/api/v1/system/privilege-check")
async def get_privilege_status():
    """
    Polled by Electron frontend during bootup to ensure the agent 
    has enough privileges to spin up virtual network cards.
    """
    has_root = is_running_as_elevated()
    os_type = "Windows (NT)" if os.name == "nt" else "Unix/Linux"
    
    logging.info(f"Privilege check invoked. Result: Elevated={has_root} (OS: {os_type})")
    
    return {
        "status": "success",
        "has_root_privileges": has_root,
        "os_type": os_type,
        "message": "Elevated context granted. TUN operations allowed." if has_root 
                   else "Access Denied. Virtual Interface deployment requires root/administrator privileges."
    }


@app.post("/api/v1/tunnel/initiate")
async def initiate_tunnel(payload: HandshakePayload):
    """
    Simulates checking context before triggering key exchange.
    Will refuse to proceed if root elevation is missing.
    """
    # Enforce root barrier at endpoint level
    if not is_running_as_elevated():
        logging.warning("Blocked attempt to initiate tunnel without root/admin privileges.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot provision virtual network adapter. Please launch local API with sudo/administrator permissions."
        )
    
    logging.info(f"Spinning up PQC handshake with Gateway {payload.gateway_ip}:{payload.gateway_port}...")
    
    # Mocking successful session setup (ML-KEM metrics mapping)
    return {
        "status": "tunnel_negotiation_started",
        "target_ip": "10.8.0.5",
        "encryption_matrix": "Secured (Kyber-1024 Hybrid Matrix)",
        "message": "Tunnel initialization sequence validated and triggered."
    }

# ==========================================
# ENGINE RUNNER
# ==========================================

if __name__ == "__main__":
    # Log current privileges status on boot
    elevated = is_running_as_elevated()
    if elevated:
        logging.info("[+] SUCCESS: API running with elevated (Root/Admin) privileges. Ready to control network layers!")
    else:
        logging.warning("[-] WARNING: Running as non-root user. Network adapter operations will be locked.")
        
    logging.info("Starting local backend server on http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
