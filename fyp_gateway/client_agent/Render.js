// =====================================================================
// PQ Tunneling — renderer process script
// STAGE 1 REVISION: Root/Sudo Checks Disabled for Direct Logic Verification
// Compatible with Windows & Ubuntu (File System Case-Insensitive Mapping)
// =====================================================================

// ---- Optional Electron window controls (safe no-op outside Electron) ----
let ipcRenderer = null;
try {
  // Use try-catch to ensure normal browser load doesn't crash on require
  ipcRenderer = require('electron').ipcRenderer;
} catch (e) {
  console.log("[PQ Render UI] Native Electron controls not available (normal browser load).");
}

const wcMin = document.getElementById('wcMin');
const wcMax = document.getElementById('wcMax');
const wcClose = document.getElementById('wcClose');

if (wcMin) wcMin.addEventListener('click', () => ipcRenderer && ipcRenderer.send('window-minimize'));
if (wcMax) wcMax.addEventListener('click', () => ipcRenderer && ipcRenderer.send('window-maximize'));
if (wcClose) wcClose.addEventListener('click', () => ipcRenderer && ipcRenderer.send('window-close'));

// =====================================================================
// DATA & STATE
// =====================================================================
const COUNTRIES = [
  { id: 'fastest', name: 'Fastest Node', flag: '⚡', servers: 'Auto-selected', tier: 'high', fastest: true, x: 505, y: 165 },
  { id: 'us', name: 'United States', flag: '🇺🇸', servers: '312 servers', tier: 'high', x: 210, y: 165 },
  { id: 'de', name: 'Germany', flag: '🇩🇪', servers: '184 servers', tier: 'high', x: 505, y: 130 },
  { id: 'jp', name: 'Japan', flag: '🇯🇵', servers: '96 servers', tier: 'high', x: 855, y: 175 },
  { id: 'br', name: 'Brazil', flag: '🇧🇷', servers: '52 servers', tier: 'med', x: 300, y: 340 },
  { id: 'gb', name: 'United Kingdom', flag: '🇬🇧', servers: '140 servers', tier: 'high', x: 480, y: 120 },
];

const FILTER_TAGS = {
  'secure-core': ['de', 'jp', 'us', 'gb'],
  'p2p': ['de', 'us', 'br'],
};

let state = {
  connection: 'disconnected', // disconnected | connecting | connected
  segment: 'recents',
  filter: 'all',
  search: '',
  selected: 'fastest',
};

// =====================================================================
// API INTEGRATION CONFIG
// =====================================================================
// Explicitly targeting port 8001 where local_api.py listens
const BACKEND_URL = 'http://127.0.0.1:8001';

// =====================================================================
// CONNECT / DISCONNECT FLOW (With Sudo/Privilege Lock Disabled)
// =====================================================================
const connectBtn = document.getElementById('connectBtn');
const connectBtnLabel = document.getElementById('connectBtnLabel');
const statusShelf = document.getElementById('statusShelf');
const statusLabel = document.getElementById('statusLabel');
const statusCaption = document.getElementById('statusCaption');
const metaVirtualIp = document.getElementById('metaVirtualIp');
const metaEncryption = document.getElementById('metaEncryption');
const metaLatency = document.getElementById('metaLatency');

/**
 * Main UI transition logic for the tunneling states.
 */
function setConnectionUI(mode, assignedIp = '10.8.0.5', encryptionMatrix = 'Secured (Kyber Hybrid Matrix)') {
  if (!connectBtn) return;
  state.connection = mode;
  connectBtn.classList.remove('connected', 'connecting');
  if (statusShelf) statusShelf.classList.remove('protected');
  if (statusCaption) statusCaption.style.color = "";

  if (mode === 'disconnected') {
    if (connectBtnLabel) connectBtnLabel.textContent = 'Connect';
    if (statusLabel) statusLabel.textContent = 'UNPROTECTED';
    if (statusCaption) statusCaption.textContent = 'Traffic is not passing through the PQ tunnel';
    if (metaVirtualIp) metaVirtualIp.textContent = '—';
    if (metaEncryption) metaEncryption.textContent = 'Inactive';
    if (metaLatency) metaLatency.textContent = '—';
  } else if (mode === 'connecting') {
    connectBtn.classList.add('connecting');
    if (connectBtnLabel) connectBtnLabel.textContent = 'Negotiating…';
    if (statusLabel) statusLabel.textContent = 'ESTABLISHING TUNNEL';
    if (statusCaption) statusCaption.textContent = 'Performing dynamic ML-KEM-1024 / X25519 key exchange...';
    if (metaVirtualIp) metaVirtualIp.textContent = 'Provisioning…';
    if (metaEncryption) metaEncryption.textContent = 'Handshake in progress';
    if (metaLatency) metaLatency.textContent = '—';
  } else if (mode === 'connected') {
    connectBtn.classList.add('connected');
    if (statusShelf) statusShelf.classList.add('protected');
    if (connectBtnLabel) connectBtnLabel.textContent = 'Disconnect';
    if (statusLabel) statusLabel.textContent = 'PROTECTED';
    if (statusCaption) statusCaption.textContent = 'Traffic is secured through the PQ tunnel';
    if (metaVirtualIp) metaVirtualIp.textContent = assignedIp;
    if (metaEncryption) metaEncryption.textContent = encryptionMatrix;
    // Latency generation for visual effect
    if (metaLatency) metaLatency.textContent = `${25 + Math.round(Math.random() * 8)}ms`;
  }
}

/**
 * Handle connection button logic directly, skipping privilege validation.
 */
if (connectBtn) {
  connectBtn.addEventListener('click', async () => {
    console.log("[DEBUG Click] Connect Button Clicked!");

    if (state.connection === 'disconnected') {
      console.log("[DEBUG Action] Attempting Connection flow (skipping sudo check stage)...");
      setConnectionUI('connecting');

      try {
        const payload = {
          gateway_ip: "198.51.100.1", // Mock target gateway IP
          gateway_port: 51820,
          force_tunnel: true
        };
        console.log(`[DEBUG Request] Fetching from ${BACKEND_URL}/api/v1/tunnel/initiate...`);

        // Fetch connection parameters directly from elevated local engine
        const response = await fetch(`${BACKEND_URL}/api/v1/tunnel/initiate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        console.log(`[DEBUG Response] Status received: ${response.status}`);

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "Server negotiation blocked by core engine.");
        }

        const data = await response.json();
        console.log("[DEBUG Response Data]", data);

        // Transition dynamically after negotiation completion simulation
        setTimeout(() => {
          setConnectionUI('connected', data.target_ip, data.encryption_matrix);
        }, 1100);

      } catch (error) {
        console.error("[PQC Tunnel Initiation Failed]", error);
        alert(`Verification Error (Check if backend_core is running on port 8001): ${error.message}`);
        setConnectionUI('disconnected');
      }

    } else if (state.connection === 'connected') {
      console.log("[DEBUG Action] Disconnecting...");
      // Reset back to normal safe state
      setConnectionUI('disconnected');
    }
  });
}

// =====================================================================
// COUNTRY LIST (Visual Render Engine)
// =====================================================================
function passesFilter(c) {
  if (state.filter === 'all') return true;
  const ids = FILTER_TAGS[state.filter] || [];
  return ids.includes(c.id);
}

function passesSearch(c) {
  if (!state.search) return true;
  return c.name.toLowerCase().includes(state.search.toLowerCase());
}

function renderCountryList() {
  const listEl = document.getElementById('countryList');
  if (!listEl) return;
  const items = COUNTRIES.filter(c => passesFilter(c) && passesSearch(c));
  listEl.innerHTML = '';

  items.forEach(c => {
    const row = document.createElement('div');
    row.className = `country-row ${c.tier}${state.selected === c.id ? ' selected' : ''}`;
    row.dataset.id = c.id;
    row.innerHTML = `
      <span class="country-flag">${c.flag}</span>
      <span class="country-name">${c.name}${c.fastest ? `<span class="badge-fastest" title="Fastest">
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 2 L4 14 H11 L10 22 L20 9 H13 Z"/></svg>
      </span>` : ''}</span>
      <span class="country-servers">${c.servers}</span>
      <span class="row-signal"><span></span><span></span><span></span></span>
    `;
    row.addEventListener('click', () => selectCountry(c.id));
    listEl.appendChild(row);
  });

  if (items.length === 0) {
    listEl.innerHTML = `<div style="padding:20px 8px; font-size:11px; color:var(--text-tertiary); text-align:center;">No locations match “${state.search}”</div>`;
  }
}

function selectCountry(id) {
  state.selected = id;
  const c = COUNTRIES.find(x => x.id === id);
  const titleEl = document.getElementById('fastestTitle');
  if (titleEl) {
    titleEl.textContent = c.fastest ? 'Fastest Node — Frankfurt, DE' : `Selected Node — ${c.name}`;
  }
  renderCountryList();
  moveLatticeAnchor(c.x, c.y);
}

// Visual Toggles & Search Bindings
const searchInput = document.getElementById('searchInput');
if (searchInput) {
  searchInput.addEventListener('input', (e) => {
    state.search = e.target.value;
    renderCountryList();
  });
}

document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.filter = chip.dataset.filter;
    renderCountryList();
  });
});

// =====================================================================
// WORLD MAP — Geometric Dot-Grid Layout
// =====================================================================
const svgNS = 'http://www.w3.org/2000/svg';
const worldSvg = document.getElementById('worldSvg');

if (worldSvg) {
  const GRID_GROUP = document.createElementNS(svgNS, 'g');
  for (let x = 20; x < 1000; x += 26) {
    for (let y = 20; y < 500; y += 26) {
      const dot = document.createElementNS(svgNS, 'circle');
      dot.setAttribute('cx', x);
      dot.setAttribute('cy', y);
      dot.setAttribute('r', 0.9);
      dot.setAttribute('class', 'world-grid-dot');
      GRID_GROUP.appendChild(dot);
    }
  }
  worldSvg.insertBefore(GRID_GROUP, worldSvg.firstChild);

  COUNTRIES.forEach(c => {
    const node = document.createElementNS(svgNS, 'circle');
    node.setAttribute('cx', c.x);
    node.setAttribute('cy', c.y);
    node.setAttribute('r', 2);
    node.setAttribute('class', 'server-node pulse');
    node.style.animationDelay = `${Math.random() * 2}s`;
    worldSvg.appendChild(node);
  });
}

// =====================================================================
// LATTICE RADAR INTEGRATION
// =====================================================================
function buildHexLattice() {
  const group = document.getElementById('latticeHex');
  if (!group) return;
  group.innerHTML = '';
  const cx = 150, cy = 150;
  const hexR = 22;

  const points = [{ x: cx, y: cy }];
  for (let ring = 1; ring <= 2; ring++) {
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i;
      const px = cx + Math.cos(angle) * hexR * ring * 1.6;
      const py = cy + Math.sin(angle) * hexR * ring * 1.6;
      points.push({ x: px, y: py });
    }
  }

  points.forEach((p, i) => {
    const dot = document.createElementNS(svgNS, 'circle');
    dot.setAttribute('cx', p.x); dot.setAttribute('cy', p.y);
    dot.setAttribute('r', i === 0 ? 0 : 1.5);
    dot.setAttribute('fill', 'rgba(41,240,255,0.5)');
    group.appendChild(dot);
  });
}
buildHexLattice();

function moveLatticeAnchor(mapX, mapY) {
  const radar = document.getElementById('latticeRadar');
  const canvas = document.getElementById('mapCanvas');
  if (!radar || !canvas) return;
  const canvasRect = canvas.getBoundingClientRect();
  const viewBoxW = 1000, viewBoxH = 520;
  const scale = Math.min(canvasRect.width / viewBoxW, canvasRect.height / viewBoxH);
  const offsetX = (canvasRect.width - viewBoxW * scale) / 2;
  const offsetY = (canvasRect.height - viewBoxH * scale) / 2;
  const px = offsetX + mapX * scale;
  const py = offsetY + mapY * scale;
  radar.style.left = `${px}px`;
  radar.style.top = `${py}px`;
}

// =====================================================================
// INIT
// =====================================================================
document.addEventListener("DOMContentLoaded", () => {
  console.log("[DEBUG Init] Render.js Loaded (Visual Logic Test Mode)!");
  renderCountryList();
  setConnectionUI('disconnected');

  requestAnimationFrame(() => {
    const c = COUNTRIES.find(x => x.id === state.selected);
    if (c) moveLatticeAnchor(c.x, c.y);
  });
});
