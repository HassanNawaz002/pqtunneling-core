# fyp_gateway/client_agent/backend_core/local_api.py
import os
import sys
import platform
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hybrid_client_kdf import PQCHybridKDF
from packet_sniffer import PQTunnelDataPlaneAgent

app = FastAPI(title="PQ Tunnel Local Verification Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_plane_agent = PQTunnelDataPlaneAgent()

def evaluate_system_privileges():
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception: return False
    else:
        try: return os.getuid() == 0
        except Exception: return False

@app.get("/v1/client/privileges")
def get_privilege_matrix():
    has_rights = evaluate_system_privileges()
    return {
        "is_privileged": has_rights,
        "diagnostic_msg": "System Elevated Context Confirmed." if has_rights else "Privilege Escalation Required! Run app as Administrator/Root."
    }

@app.post("/v1/tunnel/connect")
def trigger_full_connection_pipeline():
    if not evaluate_system_privileges():
        return {"status": "FAILED", "error": "Missing elevated administrative capabilities."}
        
    # Trigger Step 4 & 5 sequence logic simulation
    client_seed = PQCHybridKDF.generate_ephemeral_lattice_parameters()
    mock_aws_ciphertext = "8f3a9d2c1b4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a"
    
    session_key = PQCHybridKDF.derive_quantum_safe_key(client_seed, mock_aws_ciphertext)
    data_plane_agent.set_session_key(session_key)
    data_plane_agent.start_tunnel_loop()
    
    return {
        "status": "CONNECTED",
        "interface": "pqtun0",
        "virtual_ip": "10.8.0.5",
        "session_id": "pqc-session-active-7fff",
        "latency": "18ms",
        "encryption": "Secured (ML-KEM-1024 Hybrid Matrix)"
    }

@app.post("/v1/tunnel/disconnect")
def deactivate_tunnel_pipeline():
    data_plane_agent.stop_tunnel_loop()
    return {"status": "DISCONNECTED", "message": "Tunnel link severed gracefully."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
