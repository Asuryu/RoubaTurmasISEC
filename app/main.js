const {app, BrowserWindow} = require('electron');
const path = require('path');

function createWindow () {
    mainWindow = new BrowserWindow({
        width: 680,
        height: 420,
        transparent: false,
        frame: true,
        resizable: false,
        fullscreen: false,
        fullscreenable: false,
        backgroundColor: '#181818',
        webPreferences: {
            contextIsolation: true,
            nodeIntegration: true,
            enableRemoteModule: false,
            preload: path.join(__dirname, '/js/preload.js')
        },
        icon: __dirname + "/assets/favicon.ico"
    });
  
    // and load the index.html of the app.
    mainWindow.loadFile('html/index.html');
    
    // Emitted when the window is closed.
    mainWindow.on('closed', function () {
      app.quit();
    });

};

app.whenReady().then(createWindow);