/**
 * Certify Intel Desktop Application
 * Main Electron Process
 */

const { app, BrowserWindow, Tray, Menu, dialog, shell } = require('electron');
const { autoUpdater } = require('electron-updater');
const log = require('electron-log');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Configure logging
log.transports.file.level = 'info';
autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = 'info';

// Auto-updater configuration
autoUpdater.autoDownload = false;  // Ask user before downloading
autoUpdater.autoInstallOnAppQuit = true;  // Install when app closes

// Keep references to prevent garbage collection
let mainWindow = null;
let tray = null;
let backendProcess = null;

// Path configurations
const isDev = process.env.NODE_ENV === 'development';
const isVersionA = process.env.BUILD_VERSION !== 'B';

function getResourcePath(relativePath) {
    if (isDev) {
        return path.join(__dirname, '..', relativePath);
    }
    return path.join(process.resourcesPath, relativePath);
}

// Backend server management
function startBackend() {
    const backendPath = isDev
        ? path.join(__dirname, '..', '..', 'backend', 'main.py')
        : path.join(getResourcePath('backend-bundle'), process.platform === 'win32' ? 'certify_backend.exe' : 'certify_backend');

    log.info('Starting backend from:', backendPath);

    if (isDev) {
        // Development: run Python directly
        backendProcess = spawn('python', ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'], {
            cwd: path.join(__dirname, '..', '..', 'backend'),
            env: { ...process.env }
        });
    } else {
        // Production: run bundled executable
        backendProcess = spawn(backendPath, [], {
            cwd: path.dirname(backendPath),
            env: { ...process.env, DATA_PATH: getResourcePath('data') }
        });
    }

    backendProcess.stdout.on('data', (data) => {
        log.info(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        log.error(`Backend Error: ${data}`);
    });

    backendProcess.on('close', (code) => {
        log.info(`Backend exited with code ${code}`);
    });
}

function stopBackend() {
    if (backendProcess) {
        log.info('Stopping backend...');
        if (process.platform === 'win32') {
            spawn('taskkill', ['/pid', backendProcess.pid, '/f', '/t']);
        } else {
            backendProcess.kill('SIGTERM');
        }
        backendProcess = null;
    }
}

// Wait for backend to be ready
async function waitForBackend(maxRetries = 30) {
    const http = require('http');

    for (let i = 0; i < maxRetries; i++) {
        try {
            await new Promise((resolve, reject) => {
                const req = http.get('http://127.0.0.1:8000/api/health', (res) => {
                    if (res.statusCode === 200) resolve();
                    else reject();
                });
                req.on('error', reject);
                req.setTimeout(1000, reject);
            });
            log.info('Backend is ready!');
            return true;
        } catch {
            log.info(`Waiting for backend... (${i + 1}/${maxRetries})`);
            await new Promise(r => setTimeout(r, 1000));
        }
    }
    return false;
}

// Create main window
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1024,
        minHeight: 768,
        title: isVersionA ? 'Certify Intel' : 'CompetitorIQ',
        icon: path.join(__dirname, '..', 'resources', 'icons', 'icon.png'),
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true
        },
        show: false // Show after ready
    });

    // Load the app
    mainWindow.loadURL('http://127.0.0.1:8000/app');

    // Show when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        mainWindow.focus();
    });

    // Handle external links
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    // Cleanup on close
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// System tray
function createTray() {
    const iconPath = path.join(__dirname, '..', 'resources', 'icons', 'icon.png');

    if (fs.existsSync(iconPath)) {
        tray = new Tray(iconPath);

        const contextMenu = Menu.buildFromTemplate([
            { label: 'Open Certify Intel', click: () => mainWindow?.show() },
            { type: 'separator' },
            { label: 'Check for Updates', click: () => autoUpdater.checkForUpdates() },
            { type: 'separator' },
            { label: 'Quit', click: () => app.quit() }
        ]);

        tray.setToolTip(isVersionA ? 'Certify Intel' : 'CompetitorIQ');
        tray.setContextMenu(contextMenu);

        tray.on('double-click', () => mainWindow?.show());
    }
}

// Auto-updater events
autoUpdater.on('checking-for-update', () => {
    log.info('Checking for updates...');
});

autoUpdater.on('update-available', (info) => {
    log.info('Update available:', info.version);

    dialog.showMessageBox({
        type: 'info',
        title: 'Update Available',
        message: `A new version (${info.version}) is available!`,
        detail: 'Would you like to download and install it now?',
        buttons: ['Download Now', 'Later'],
        defaultId: 0
    }).then((result) => {
        if (result.response === 0) {
            autoUpdater.downloadUpdate();
        }
    });
});

autoUpdater.on('update-not-available', () => {
    log.info('No updates available - app is up to date');
});

autoUpdater.on('download-progress', (progress) => {
    log.info(`Download progress: ${Math.round(progress.percent)}%`);

    // Show progress in taskbar/dock
    if (mainWindow) {
        mainWindow.setProgressBar(progress.percent / 100);
    }
});

autoUpdater.on('update-downloaded', (info) => {
    log.info('Update downloaded:', info.version);

    // Clear progress bar
    if (mainWindow) {
        mainWindow.setProgressBar(-1);
    }

    // Check if this is a critical update
    const isCritical = info.releaseNotes?.includes('[CRITICAL]') ||
                       info.releaseNotes?.includes('[SECURITY]');

    if (isCritical) {
        dialog.showMessageBox({
            type: 'warning',
            title: 'Critical Security Update',
            message: 'A critical security update must be installed now.',
            detail: `Version ${info.version} contains important security fixes.`,
            buttons: ['Install Now'],
            defaultId: 0
        }).then(() => {
            autoUpdater.quitAndInstall(true, true);
        });
    } else {
        dialog.showMessageBox({
            type: 'info',
            title: 'Update Ready',
            message: 'Update downloaded!',
            detail: 'The update will be installed when you close the app. Restart now?',
            buttons: ['Restart Now', 'Later'],
            defaultId: 0
        }).then((result) => {
            if (result.response === 0) {
                autoUpdater.quitAndInstall(false, true);
            }
        });
    }
});

autoUpdater.on('error', (err) => {
    log.error('AutoUpdater error:', err);

    // Don't show error dialog for network issues during background checks
    if (err.message && !err.message.includes('net::ERR')) {
        dialog.showMessageBox({
            type: 'error',
            title: 'Update Error',
            message: 'Failed to check for updates',
            detail: 'Please check your internet connection and try again.',
            buttons: ['OK']
        });
    }
});

// App lifecycle
app.whenReady().then(async () => {
    log.info('App starting...');
    log.info('Version:', app.getVersion());
    log.info('Build type:', isVersionA ? 'Certify Health Edition' : 'White-Label Template');

    // Show loading splash
    const splash = new BrowserWindow({
        width: 400,
        height: 300,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        webPreferences: { nodeIntegration: false }
    });

    splash.loadFile(path.join(__dirname, 'splash.html'));
    splash.center();

    // Start backend server
    startBackend();

    // Wait for backend to be ready
    const backendReady = await waitForBackend();

    if (!backendReady) {
        splash.close();
        dialog.showErrorBox('Startup Error', 'Failed to start the backend server. Please try again.');
        app.quit();
        return;
    }

    // Create main window
    createWindow();
    createTray();

    // Close splash
    splash.close();

    // Check for updates (production only)
    if (!isDev) {
        // Initial check 10 seconds after startup
        setTimeout(() => {
            log.info('Performing initial update check...');
            autoUpdater.checkForUpdates();
        }, 10000);

        // Check every 4 hours while app is running
        setInterval(() => {
            log.info('Performing periodic update check...');
            autoUpdater.checkForUpdates();
        }, 4 * 60 * 60 * 1000);
    }
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('before-quit', () => {
    stopBackend();
});

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        if (mainWindow) {
            if (mainWindow.isMinimized()) mainWindow.restore();
            mainWindow.focus();
        }
    });
}
