// fyp_gateway/client_agent/main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process');

let mainWindow;
let pyBackendProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 700,
    minWidth: 1000,
    minHeight: 600,
    frame: false, // Custom framing capability mapped to your CSS layout
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile('index.html');
}

function startLocalBackend() {
  const isWindows = process.platform === "win32";
  let scriptPath = path.join(__dirname, 'backend_core', 'local_api.py');
  let command = isWindows ? `python "${scriptPath}"` : `python3 "${scriptPath}"`;

  console.log(`[*] Spawning Core Python Subprocess: ${command}`);
  
  pyBackendProcess = exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`[-] Python Kernel Initialization Error: ${error.message}`);
      return;
    }
  });

  pyBackendProcess.stdout.on('data', (data) => console.log(`[Python Core STDOUT]: ${data}`));
  pyBackendProcess.stderr.on('data', (data) => console.error(`[Python Core STDERR]: ${data}`));
}

// Custom Titlebar Frame Signal Mappings
ipcMain.on('window-minimize', () => mainWindow && mainWindow.minimize());
ipcMain.on('window-maximize', () => {
  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow.maximize();
  }
});
ipcMain.on('window-close', () => {
  if (pyBackendProcess) pyBackendProcess.kill();
  app.quit();
});

app.whenReady().then(() => {
  startLocalBackend(); 
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (pyBackendProcess) pyBackendProcess.kill();
    app.quit();
  }
});
