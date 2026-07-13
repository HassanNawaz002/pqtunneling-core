// client_agent/main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        resizable: false, // UI standard constraint layout
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    // Load our premium dashboard html file
    mainWindow.loadFile(path.join(__dirname, 'index.html'));
    
    // Developer tool integration line (agar inspection karni ho)
    // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});
