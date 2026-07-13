// client_agent/preload.js
const { contextBridge } = require('electron');

// Expose secure utility endpoints to frontend execution context safely
contextBridge.exposeInMainWorld('electronAPI', {
    triggerLocalTunnel: async () => {
        try {
            const response = await fetch('http://127.0.0.1:8001/v1/client/connect', { method: 'POST' });
            return await response.json();
        } catch (error) {
            return { status: "ERROR", message: error.message };
        }
    },
    checkLocalStatus: async () => {
        try {
            const response = await fetch('http://127.0.0.1:8001/v1/client/status');
            return await response.json();
        } catch (error) {
            return { agent_status: "OFFLINE", error: error.message };
        }
    }
});

