# Desktop App Build & Distribution Plan

## Overview

This document provides a complete plan to package Certify Health Intel into production-ready desktop installers for **Windows** and **macOS**, and distribute them to your team via GitHub Releases.

**Current Status**: 🟡 63% Complete (solid foundation, needs finishing)
**Effort Required**: 3-5 days of focused work
**End Result**: Downloadable `.exe` (Windows) and `.dmg` (macOS) installers

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Implementation Plan (8 Phases)](#2-implementation-plan)
3. [How to Download from GitHub](#3-how-to-download-installers-from-github)
4. [How to Distribute to Teammates](#4-how-to-distribute-to-teammates)
5. [Live Auto-Updates (Push Updates to All Users)](#5-live-auto-updates-push-updates-to-all-users)
6. [Quick Reference Commands](#6-quick-reference-commands)

---

## 1. Current State Analysis

### What's Already Done ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Electron v28.1.0 | ✅ Complete | Modern, stable version |
| electron-builder v24.9.1 | ✅ Complete | Production-ready |
| Auto-updater setup | ✅ Complete | electron-updater integrated |
| Build scripts | ✅ Complete | `build-windows.bat`, `build-mac.sh` |
| App icons | ✅ Complete | .ico, .png, .svg formats |
| Splash screen | ✅ Complete | Professional loading UI |
| System tray | ✅ Complete | Background operation |
| Single instance lock | ✅ Complete | Prevents duplicate launches |

### What's Missing ❌

| Component | Priority | Impact |
|-----------|----------|--------|
| PyInstaller spec file | 🔴 Critical | Builds will fail without it |
| Backend `__main__.py` | 🔴 Critical | Backend won't bundle |
| GitHub Actions workflow | 🔴 Critical | No automated releases |
| GitHub publish config | 🟡 High | Auto-updates won't work |
| Code signing (Windows) | 🟡 High | SmartScreen warnings |
| Notarization (macOS) | 🟡 High | Gatekeeper blocks |

---

## 2. Implementation Plan (8 Phases)

### Phase 1: Create Backend Entry Point (30 minutes)

Create `backend/__main__.py` so PyInstaller can bundle the backend:

```python
# backend/__main__.py
"""Entry point for PyInstaller bundled backend."""
import sys
import os

# Ensure the backend directory is in the path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    bundle_dir = sys._MEIPASS
    os.chdir(bundle_dir)
else:
    # Running as script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Import and run the main application
from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

### Phase 2: Create PyInstaller Spec File (1 hour)

Create `backend/certify_backend.spec`:

```python
# backend/certify_backend.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('certify_intel.db', '.'),
        ('.env', '.'),
        ('templates', 'templates'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'sqlalchemy.sql.default_comparator',
        'passlib.handlers.bcrypt',
        'langchain',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='certify_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../desktop-app/resources/icons/icon.ico'
)
```

### Phase 3: Update GitHub Publish Config (15 minutes)

Update `desktop-app/package.json` with your GitHub details:

```json
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "hicklax13",
      "repo": "Project_Intel_v4",
      "releaseType": "release"
    }
  }
}
```

### Phase 4: Create GitHub Actions Workflow (1 hour)

Create `.github/workflows/build-release.yml`:

```yaml
name: Build and Release Desktop App

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version number (e.g., 1.0.0)'
        required: true

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Python dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build backend with PyInstaller
        run: |
          cd backend
          pyinstaller certify_backend.spec --clean --noconfirm

      - name: Prepare backend bundle
        run: |
          mkdir -p desktop-app/backend-bundle
          cp backend/dist/certify_backend.exe desktop-app/backend-bundle/
          cp backend/certify_intel.db desktop-app/backend-bundle/
          cp backend/.env.example desktop-app/backend-bundle/.env

      - name: Copy frontend files
        run: |
          cp -r frontend/* desktop-app/frontend/

      - name: Install Node dependencies
        run: |
          cd desktop-app
          npm install

      - name: Build Windows installer
        run: |
          cd desktop-app
          npm run build:win
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload Windows artifact
        uses: actions/upload-artifact@v4
        with:
          name: windows-installer
          path: desktop-app/dist/*.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Python dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build backend with PyInstaller
        run: |
          cd backend
          pyinstaller certify_backend.spec --clean --noconfirm

      - name: Prepare backend bundle
        run: |
          mkdir -p desktop-app/backend-bundle
          cp backend/dist/certify_backend desktop-app/backend-bundle/
          cp backend/certify_intel.db desktop-app/backend-bundle/
          cp backend/.env.example desktop-app/backend-bundle/.env

      - name: Copy frontend files
        run: |
          cp -r frontend/* desktop-app/frontend/

      - name: Install Node dependencies
        run: |
          cd desktop-app
          npm install

      - name: Build macOS installer
        run: |
          cd desktop-app
          npm run build:mac
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload macOS artifact
        uses: actions/upload-artifact@v4
        with:
          name: macos-installer
          path: desktop-app/dist/*.dmg

  create-release:
    needs: [build-windows, build-macos]
    runs-on: ubuntu-latest
    steps:
      - name: Download Windows artifact
        uses: actions/download-artifact@v4
        with:
          name: windows-installer
          path: ./installers

      - name: Download macOS artifact
        uses: actions/download-artifact@v4
        with:
          name: macos-installer
          path: ./installers

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: ./installers/*
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Phase 5: Test Local Build (2-3 hours)

**Windows Build Test:**
```bash
cd backend
pip install pyinstaller
pyinstaller certify_backend.spec --clean --noconfirm

cd ../desktop-app
npm install
npm run build:win
```

**macOS Build Test:**
```bash
cd backend
pip install pyinstaller
pyinstaller certify_backend.spec --clean --noconfirm

cd ../desktop-app
npm install
npm run build:mac
```

### Phase 6: Create First Release (30 minutes)

```bash
# Tag and push to trigger release
git tag -a v1.0.0 -m "First production release"
git push origin v1.0.0
```

Or manually trigger via GitHub Actions UI.

### Phase 7: (Optional) Code Signing

**Windows Code Signing:**
- Purchase certificate from DigiCert, Sectigo, or similar (~$200-500/year)
- Add to GitHub Secrets: `WIN_CSC_LINK`, `WIN_CSC_KEY_PASSWORD`

**macOS Notarization:**
- Requires Apple Developer account ($99/year)
- Add to GitHub Secrets: `APPLE_ID`, `APPLE_ID_PASSWORD`, `APPLE_TEAM_ID`

---

## 3. How to Download Installers from GitHub

### For You (Repository Owner)

Once the release is created, download the Windows installer:

1. **Go to your repository**: https://github.com/hicklax13/Project_Intel_v4

2. **Click "Releases"** (right sidebar or tab)

3. **Find the latest release** (e.g., v1.0.0)

4. **Under "Assets", click to download:**
   - `Certify-Health-Intel-Setup-1.0.0.exe` (Windows)
   - `Certify-Health-Intel-1.0.0.dmg` (macOS)

5. **Run the installer** on your Windows desktop

### Direct Download URL Pattern

Once released, direct links will be:
```
https://github.com/hicklax13/Project_Intel_v4/releases/download/v1.0.0/Certify-Health-Intel-Setup-1.0.0.exe
https://github.com/hicklax13/Project_Intel_v4/releases/download/v1.0.0/Certify-Health-Intel-1.0.0.dmg
```

### Windows SmartScreen Warning

Since the app isn't code-signed yet, Windows will show a warning:
1. Click "More info"
2. Click "Run anyway"

This warning goes away with code signing (Phase 7).

---

## 4. How to Distribute to Teammates

### Option A: GitHub Releases (Recommended) ⭐

**Best for**: Teams with GitHub access

1. **Add teammates as collaborators** (if private repo):
   - Go to: Settings → Collaborators → Add people
   - Enter their GitHub usernames/emails

2. **Share the Releases URL**:
   ```
   https://github.com/hicklax13/Project_Intel_v4/releases
   ```

3. **Each teammate can**:
   - Visit the URL
   - Download their platform's installer
   - Install and run

**Advantages**:
- Always latest version available
- Auto-updates work (once configured)
- Version history preserved
- No file size limits

---

### Option B: Direct Link Sharing

**Best for**: Quick distribution without GitHub accounts

1. **Get the direct download URLs** from the release page

2. **Send to teammates via email/Slack/Teams**:
   ```
   Hi team! Here are the installers for Certify Health Intel:

   Windows: [download link]
   macOS: [download link]

   Installation:
   1. Download the file for your OS
   2. Windows: Run the .exe, click "More info" → "Run anyway" if prompted
   3. macOS: Open the .dmg, drag app to Applications
   ```

---

### Option C: Shared Drive / Cloud Storage

**Best for**: Corporate environments without GitHub access

1. **Download both installers** to your computer

2. **Upload to shared location**:
   - Google Drive
   - OneDrive
   - SharePoint
   - Dropbox
   - Network share

3. **Share the folder/files** with teammates

4. **Create a README.txt** in the folder:
   ```
   Certify Health Intel - Desktop App
   ==================================

   Windows Users: Run "Certify-Health-Intel-Setup-1.0.0.exe"
   Mac Users: Open "Certify-Health-Intel-1.0.0.dmg"

   First-time Windows install may show SmartScreen warning:
   - Click "More info"
   - Click "Run anyway"

   Questions? Contact [your email]
   ```

---

### Option D: Email with Attachment

**Best for**: Small files or compressed versions

⚠️ **Note**: Installer files are typically 100-200MB, which exceeds most email limits.

**Workaround**: Use a file transfer service like:
- WeTransfer (free up to 2GB)
- Dropbox Transfer
- Google Drive sharing link

---

## 5. Live Auto-Updates (Push Updates to All Users)

This is the **most important feature** for maintaining your deployed apps. Once set up, you can push code changes to ALL installed apps with a single command.

### How Auto-Updates Work

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  You push new   │────▶│  GitHub Actions  │────▶│ GitHub Releases │
│  version tag    │     │  builds new app  │     │ hosts installer │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                    ┌─────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ALL INSTALLED APPS                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ User 1   │  │ User 2   │  │ User 3   │  │ User 4   │        │
│  │ Windows  │  │ Windows  │  │ macOS    │  │ macOS    │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │               │
│       └─────────────┴──────┬──────┴─────────────┘               │
│                            ▼                                    │
│              "Update Available!" popup                          │
│              User clicks "Install" → App restarts               │
└─────────────────────────────────────────────────────────────────┘
```

### What Gets Published with Each Release

When you create a release, GitHub Actions automatically publishes:

| File | Purpose |
|------|---------|
| `Certify-Health-Intel-Setup-1.0.1.exe` | Windows installer |
| `Certify-Health-Intel-1.0.1.dmg` | macOS installer |
| `latest.yml` | Windows update manifest (version, checksum, URL) |
| `latest-mac.yml` | macOS update manifest |

The `latest.yml` files tell installed apps where to download updates from.

### Phase 8: Configure Auto-Updater (NEW - 1 hour)

The existing `electron/main.js` already has electron-updater code, but we need to enhance it.

**Update `desktop-app/electron/main.js`** - Add this enhanced auto-update configuration:

```javascript
// Add near the top of main.js
const { autoUpdater } = require('electron-updater');
const log = require('electron-log');

// Configure logging for auto-updater
autoUpdater.logger = log;
autoUpdater.logger.transports.file.level = 'info';

// Auto-updater configuration
autoUpdater.autoDownload = false;  // Ask user before downloading
autoUpdater.autoInstallOnAppQuit = true;  // Install when app closes

// Check for updates on startup (after app is ready)
app.whenReady().then(() => {
    // Check for updates 10 seconds after startup
    setTimeout(() => {
        if (!isDev) {
            autoUpdater.checkForUpdates();
        }
    }, 10000);

    // Also check every 4 hours while app is running
    setInterval(() => {
        if (!isDev) {
            autoUpdater.checkForUpdates();
        }
    }, 4 * 60 * 60 * 1000);
});

// Auto-updater event handlers
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

    // Update splash screen or show progress in tray tooltip
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
});

autoUpdater.on('error', (error) => {
    log.error('Auto-updater error:', error);
});
```

### How to Push an Update to All Users

**Step 1: Make your code changes**
```bash
# Edit files, fix bugs, add features
git add .
git commit -m "Fix bug in analytics dashboard"
```

**Step 2: Update the version number**

Edit `desktop-app/package.json`:
```json
{
  "version": "1.0.1"  // Increment from 1.0.0
}
```

**Step 3: Commit and tag the release**
```bash
git add desktop-app/package.json
git commit -m "Bump version to 1.0.1"
git tag -a v1.0.1 -m "Version 1.0.1 - Bug fixes"
git push origin main --tags
```

**Step 4: Wait for GitHub Actions** (~15-20 minutes)
- GitHub automatically builds Windows and macOS installers
- Creates a new release with the installers
- Publishes `latest.yml` and `latest-mac.yml` update manifests

**Step 5: All installed apps auto-detect the update**
- Within 4 hours (or on next app launch), users see "Update Available!"
- They click "Download Now" → app downloads in background
- They click "Restart Now" → app installs and restarts

### Update Behavior Options

You can customize update behavior in `main.js`:

| Option | Behavior | Code |
|--------|----------|------|
| **Ask before download** (default) | User decides when to download | `autoUpdater.autoDownload = false` |
| **Silent download** | Downloads automatically, asks to install | `autoUpdater.autoDownload = true` |
| **Fully automatic** | Downloads and installs on quit | `autoDownload = true` + `autoInstallOnAppQuit = true` |
| **Force immediate update** | Quits and installs immediately | `autoUpdater.quitAndInstall(true, true)` |

### Forcing a Critical Update

For security patches or critical bugs, you can force immediate updates:

```javascript
// In main.js - for critical updates
autoUpdater.on('update-downloaded', (info) => {
    // Check if this is a critical update (you define the logic)
    const isCritical = info.version.includes('security') ||
                       info.releaseNotes?.includes('[CRITICAL]');

    if (isCritical) {
        dialog.showMessageBox({
            type: 'warning',
            title: 'Critical Security Update',
            message: 'A critical security update must be installed now.',
            buttons: ['Install Now'],
            defaultId: 0
        }).then(() => {
            autoUpdater.quitAndInstall(true, true);  // Force quit and install
        });
    } else {
        // Normal update flow - ask user
        // ... existing code
    }
});
```

### User Experience Timeline

| Event | What User Sees |
|-------|----------------|
| App starts | Nothing (update check happens in background) |
| Update found | Dialog: "A new version (1.0.1) is available!" |
| User clicks "Download" | Progress bar in taskbar/dock |
| Download complete | Dialog: "Update ready! Restart now?" |
| User clicks "Restart" | App closes, installs update, reopens |
| Next launch | Running new version |

### Testing Auto-Updates Locally

Before deploying, test the update flow:

```bash
# 1. Build version 1.0.0
cd desktop-app
npm version 1.0.0
npm run build:win  # or build:mac

# 2. Install it on your machine

# 3. Build version 1.0.1
npm version 1.0.1
npm run build:win

# 4. Manually place the new installer and latest.yml
#    in a local server or use electron-builder's
#    --publish=never and test with a local update server
```

### Monitoring Update Adoption

To see how many users have updated, you can:

1. **Check GitHub Release download counts**
   - Go to Releases → click on a release → see download count per asset

2. **Add analytics to the app** (optional)
   - Send anonymous version info to your analytics service
   - Track update success/failure rates

### Rollback Strategy

If an update has a critical bug:

1. **Create a new release immediately** with the fix (v1.0.2)
2. **Or** delete the bad release from GitHub Releases
   - Users who haven't updated yet won't get it
   - Users who already updated need v1.0.2

### Update Server Alternatives

GitHub Releases is free and works great, but alternatives exist:

| Option | Pros | Cons |
|--------|------|------|
| **GitHub Releases** (recommended) | Free, automatic, no setup | Public visibility (unless private repo) |
| **Amazon S3** | Private, scalable | Costs money, more setup |
| **Your own server** | Full control | Maintenance burden |
| **Electron Forge / Update Server** | Advanced features | Complex setup |

### Troubleshooting Auto-Updates

**Updates not working?**

1. **Check version numbers** - new version must be higher than installed
2. **Check `latest.yml` exists** in the GitHub Release assets
3. **Check GitHub publish config** in `package.json` matches your repo
4. **Check logs** - look in:
   - Windows: `%APPDATA%\certify-intel\logs\`
   - macOS: `~/Library/Logs/certify-intel/`

**Common issues:**

| Issue | Solution |
|-------|----------|
| "No update available" but there is one | Version in `package.json` not incremented |
| Download fails | Check internet, firewall, or GitHub rate limits |
| Install fails | Close all app windows, try manual install |
| Update loop | Clear app data folder and reinstall |

---

## 6. Quick Reference Commands

### Build Commands

```bash
# Install dependencies (one-time)
cd backend && pip install -r requirements.txt pyinstaller
cd ../desktop-app && npm install

# Build Windows installer
cd desktop-app && npm run build:win

# Build macOS installer
cd desktop-app && npm run build:mac

# Build both platforms
cd desktop-app && npm run build:all
```

### Release Commands

```bash
# Create a new release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# List all tags
git tag -l

# Delete a tag (if needed)
git tag -d v1.0.0
git push origin --delete v1.0.0
```

### Output Locations

After building, installers are in:
```
desktop-app/dist/Certify-Health-Intel-Setup-1.0.0.exe  (Windows)
desktop-app/dist/Certify-Health-Intel-1.0.0.dmg        (macOS)
```

---

## Summary Checklist

### Before First Release
- [ ] Create `backend/__main__.py`
- [ ] Create `backend/certify_backend.spec`
- [ ] Update `desktop-app/package.json` with GitHub owner/repo
- [ ] Create `.github/workflows/build-release.yml`
- [ ] Configure auto-updater in `electron/main.js`
- [ ] Test local build on Windows
- [ ] Test local build on macOS
- [ ] Push all changes to main branch

### Creating a Release
- [ ] Create and push git tag: `git tag -a v1.0.0 -m "message" && git push origin v1.0.0`
- [ ] Wait for GitHub Actions to complete (~15-20 minutes)
- [ ] Verify installers AND `latest.yml` files appear in release assets
- [ ] Download and test on both platforms

### Distributing to Team
- [ ] Add teammates as collaborators (if needed)
- [ ] Share releases URL or direct download links
- [ ] Include installation instructions
- [ ] Note SmartScreen warning workaround for Windows

### Pushing Updates to All Users
- [ ] Make code changes and commit
- [ ] Increment version in `desktop-app/package.json`
- [ ] Create and push new tag: `git tag -a v1.0.1 -m "message" && git push origin v1.0.1`
- [ ] Wait for GitHub Actions to build (~15-20 min)
- [ ] Verify `latest.yml` and `latest-mac.yml` in release assets
- [ ] Users receive update notification within 4 hours (or on next app launch)

---

## Timeline Summary

| Phase | Task | Time |
|-------|------|------|
| 1 | Create `__main__.py` | 30 min |
| 2 | Create PyInstaller spec | 1 hour |
| 3 | Update package.json | 15 min |
| 4 | Create GitHub Actions | 1 hour |
| 5 | Test local builds | 2-3 hours |
| 6 | Create first release | 30 min |
| 7 | Code signing (optional) | 2-4 hours |
| 8 | Configure auto-updater | 1 hour |
| **Total** | | **6-11 hours** |

---

*Document created: 2026-01-24*
*Last updated: 2026-01-24*
