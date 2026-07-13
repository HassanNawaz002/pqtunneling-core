ls
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv python3-dev build-essential -y
mkdir fyp_gateway && cd fyp_gateway
python3 -m venv venv
source venv/bin/activate
pip install
pip list

python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn cryptography pydantic
pip list
nano test_api.py
cat test_api.py 
uvicorn test_api:app --host 0.0.0.0 --port 8000
ls
cd fyp_gateway/
ls
mkdir -p gateway_server client_agent/backend_core && touch requirements.txt gateway_server/server_schemas.py gateway_server/control_plane_api.py gateway_server/data_plane_udp.py client_agent/main.js client_agent/preload.js client_agent/index.html client_agent/renderer.js client_agent/backend_core/local_api.py client_agent/backend_core/hybrid_client_kdf.py client_agent/backend_core/packet_sniffer.py
ls
ls -R
ls
cd gateway_server/
ls
clear
ls
nano server_schemas.py 
cat server_schemas.py 
ls
nano control_plane_api.py 
cat control_plane_api.py 
ls
cd ..
ls
nano requirements.txt 
pip install -r requirements.txt
pip list
cat requirements.txt 
pip install scapy
pip install requests
pip list
python gateway_server/control_plane_api.py
ls
cd client_agent/
ls
nano renderer.js 
nano main.js 
nano preload.js 
nano index.html 
cd backend_core/
nano hybrid_client_kdf.py 
cat hybrid_client_kdf.py 
nano hybrid_client_kdf.py 
nano local_api.py 
la
ls
nano local_api.py 
rm -r local_api.py 
nano local_api.py
ls -F
ls
cd fyp_gateway/
ls
ls -F
ls -R
ls
tree -I 'venv|__pycache__|.git'
sudo apt update && sudo apt install tree -y
tree -I 'venv|__pycache__|.git'
ls
cd client_agent/
ls
nano index.html 
rm -r index.html 
nano index.html
nano renderer.js 
rm -r renderer.js 
nano renderer.js 
nano main.js 
ls
nano main.js 
rem -r main.js 
rm -r main.js 
nano main.js 
nano client_agent/package.json
nano package.json
ls
ssh -X ubuntu@107.21.77.85
python3 -m http.server 8080
ls
cd fyp_gateway/
ls
cd client_agent/
ls
rm -r index.html 
ls
nano index.html
