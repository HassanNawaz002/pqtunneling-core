// fyp_gateway/client_agent/preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  sendMinimize: () => ipcRenderer.send('window-minimize'),
  sendMaximize: () => ipcRenderer.send('window-maximize'),
  sendClose: () => ipcRenderer.send('window-close'),

  checkPrivileges: async () => {
    try {
      const response = await fetch('http://127.0.0.1:8001/v1/client/privileges');
      return await response.json();
    } catch (err) {
      return { is_privileged: false, diagnostic_msg: "Local Core Unreachable." };
    }
  },

  connectTunnel: async () => {
    const response = await fetch('http://127.0.0.1:8001/v1/tunnel/connect', { method: 'POST' });
    return await response.json();
  },

  disconnectTunnel: async () => {
    const response = await fetch('http://127.0.0.1:8001/v1/tunnel/disconnect', { method: 'POST' });
    return await response.json();
  }
});
