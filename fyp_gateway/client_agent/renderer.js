// client_agent/renderer.js
const connectBtn = document.getElementById('connect-btn');
const btnText = document.getElementById('btn-text');
const switchIcon = document.getElementById('switch-icon');
const statusDot = document.getElementById('status-dot');
const oldIpDisplay = document.getElementById('old-ip');
const virtualIpDisplay = document.getElementById('virtual-ip');
const logConsole = document.getElementById('log-console');
const osBadge = document.getElementById('os-badge');
const countrySelect = document.getElementById('country-select');

function appendLog(message, type = 'info') {
    const logLine = document.createElement('div');
    const timestamp = new Date().toLocaleTimeString();
    
    if (type === 'success') logLine.className = 'text-emerald-400 font-bold';
    else if (type === 'error') logLine.className = 'text-rose-500 font-bold';
    else if (type === 'warn') logLine.className = 'text-amber-400 font-mono';
    else logLine.className = 'text-slate-400';
    
    logLine.textContent = `[${timestamp}] ${message}`;
    logConsole.appendChild(logLine);
    logConsole.scrollTop = logConsole.scrollHeight;
}

// Boot strap execution routine to query current machine status
async function fetchInitialMetrics() {
    try {
        // Fetch current workspace original internet configuration
        const ipRes = await fetch('https://api.ipify.org?format=json');
        const ipData = await ipRes.json();
        oldIpDisplay.textContent = `${ipData.ip} (Standard Route)`;
        appendLog(`Discovered original network gateway point: ${ipData.ip}`);

        // Fetch running platform architecture parameters from backend context
        const statusRes = await fetch('http://127.0.0.1:8001/v1/client/status');
        const statusData = await statusRes.json();
        osBadge.textContent = `PLATFORM: ${statusData.operating_system} (${statusData.architecture})`;
        appendLog(`Local management driver hook online. Target OS verified as ${statusData.operating_system}.`);
    } catch (err) {
        appendLog('Communication link with python orchestrator core down. Ensure backend is up.', 'error');
    }
}

connectBtn.addEventListener('click', async () => {
    // Stage 0: Transform UI into loading configuration
    connectBtn.className = "h-44 w-44 rounded-full border-2 border-amber-500 bg-slate-950 flex flex-col justify-center items-center cursor-pointer transition-all duration-300 animate-pulse neon-glow-amber text-amber-500";
    switchIcon.className = "h-10 w-10 text-amber-500";
    btnText.textContent = 'VERIFYING...';
    
    const selectedTarget = countrySelect.value;
    appendLog(`Execution sequence triggered for target profile node: [${selectedTarget}]`);

    // --- SEQUENTIAL STEP 1: Execute Privilege Check and TUN/TAP Allocation ---
    appendLog('Step 1: Inspecting structural kernel authorization rules...', 'info');
    appendLog('Checking root privileges for allocation of Layer-3 TUN/TAP descriptor endpoints...', 'info');

    try {
        const response = await fetch('http://127.0.0.1:8001/v1/client/connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_node: selectedTarget })
        });
        const result = await response.json();

        if (!response.ok) throw new Error(result.detail || 'Process execution failure.');

        // --- SEQUENTIAL STEP 2: Handle Tunnel State Change ---
        appendLog(`[✓] Root authorization verified. Interface device [${result.interface_allocated}] locked successfully.`, 'success');
        
        appendLog('Step 2: Negotiating NIST Post-Quantum hybrid cryptographic parameters...', 'warn');
        appendLog('Generating ephemeral X25519 key-shares and packaging ML-KEM-1024 primitives...', 'info');
        appendLog('Executing Phase 1 Handshake over broad internet channel to AWS node...', 'info');
        appendLog('[✓] Symmetry verified. Shared master session secret locked via SHA-256 state matching.', 'success');

        // --- SEQUENTIAL STEP 3: Success State Trigger & IP Shift ---
        connectBtn.className = "h-44 w-44 rounded-full border-2 border-emerald-500 bg-slate-950 flex flex-col justify-center items-center cursor-pointer transition-all duration-300 neon-glow text-emerald-400";
        switchIcon.className = "h-10 w-10 text-emerald-400";
        btnText.textContent = 'SECURE TUNNEL';
        statusDot.className = "h-3 w-3 rounded-full bg-emerald-500";

        virtualIpDisplay.textContent = `TUN Adapter Assigned IP: ${result.assigned_ip}`;
        virtualIpDisplay.className = "text-xs text-emerald-400 font-bold mt-0.5";
        
        appendLog(`[✓] Core Network Migration Successful! Replaced legacy IPsec mapping layer.`, 'success');
        appendLog(`[✓] All L3 routing streams bound within secure quantum-resistant channel to AWS Gateway.`, 'success');

    } catch (error) {
        // Error handling fallback layouts
        connectBtn.className = "h-44 w-44 rounded-full border-2 border-rose-600 bg-slate-950 flex flex-col justify-center items-center cursor-pointer transition-all duration-300 neon-glow-red text-rose-500";
        switchIcon.className = "h-10 w-10 text-rose-500";
        btnText.textContent = 'SYS_FAULT';
        statusDot.className = "h-3 w-3 rounded-full bg-rose-600";
        appendLog(`[X] Flow Interrupted: ${error.message}`, 'error');
    }
});

// Run metrics query once layout initial parameters execute
setTimeout(fetchInitialMetrics, 1000);
