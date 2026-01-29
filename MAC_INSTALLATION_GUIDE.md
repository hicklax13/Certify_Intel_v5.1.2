# Certify Intel Desktop App: Mac Installation Guide

## Step 1: Download

1. Go to: https://github.com/hicklax13/Certify_Intel_v5.1.2/releases
2. Click the green "v5.1.2" release (or "Latest")
3. Scroll down to "Assets" and click the correct file for your Mac:

| Mac Type | File to Download |
|----------|------------------|
| **Apple Silicon** (M1, M2, M3, M4) | `20260127_Certify_Intel_v5.5.0_arm64.dmg` |
| **Intel Mac** (older Macs) | `20260127_Certify_Intel_v5.5.0_x64.dmg` |

**Not sure which Mac you have?**
- Click the Apple menu () in the top-left corner
- Click "About This Mac"
- Look for "Chip" - if it says "Apple M1/M2/M3/M4", download arm64
- If it says "Intel", download x64

4. Wait for download to complete (~280 MB)

## Step 2: Install

1. Open your Downloads folder
2. Double-click the downloaded `.dmg` file
3. A window will appear with Certify Intel and an Applications folder
4. Drag the Certify Intel icon to the Applications folder
5. Wait for the copy to complete
6. Close the DMG window
7. (Optional) Right-click the DMG on desktop and select "Eject"

## Step 3: Launch (First Time - Important)

### Option A: Right-Click Method (Easiest)

1. Open your Applications folder (Finder > Go > Applications)
2. Find "Certify Intel"
3. **Right-click** (or Control-click) on Certify Intel
4. Select "Open" from the menu
5. Click "Open" again in the security dialog
6. Wait for the app to start (may take 10-15 seconds first time)

**Note:** You only need to right-click "Open" the first time. After that, you can double-click normally.

### Option B: Terminal Method (If Option A Fails)

If you see "App is damaged" or can't open the app at all, use Terminal:

1. Open Terminal (Applications > Utilities > Terminal)
2. Paste this command and press Enter:
   ```bash
   xattr -cr "/Applications/Certify Intel.app"
   ```
3. Try opening the app again from Applications folder

## Step 4: Login

The desktop app comes pre-configured with default admin credentials:

**Email**: `admin@certifyintel.com`
**Password**: `MSFWINTERCLINIC2026`

> **Security Note**: These are default credentials shared by all installations.
> For production use with sensitive data:
> 1. Login with default credentials
> 2. Go to Settings → User Management
> 3. Create a new admin user with your own password
> 4. Delete or disable the default admin account

Click "Sign In"

## Step 5: Use the App

> **First Launch**: The app initializes its database on first startup (takes 5-10 seconds).
> You'll see "Starting backend..." - this is normal.

You're now on the Dashboard. Use the menu on the left to navigate:

| Menu Item | What It Does |
|-----------|--------------|
| Dashboard | Overview and quick stats |
| Competitors | View all 82 competitors |
| Sales & Marketing | Battlecards and comparisons |
| News Feed | Latest competitor news |
| Reports | Generate PDF reports |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "App is damaged and can't be opened" | Open Terminal, run: `xattr -cr /Applications/Certify\ Intel.app` |
| "Developer cannot be verified" | Right-click the app, select "Open", then click "Open" |
| App closes immediately | Make sure you downloaded the correct version (arm64 vs x64) |
| App won't start | Wait 30 seconds, try again. Restart Mac if needed |
| Login fails | Check caps lock, retype password |
| Blank screen | Close and reopen the app |
| Backend server failed | Make sure no other app is using port 8000 |

---

## Uninstalling

1. Open Applications folder
2. Drag "Certify Intel" to the Trash
3. Empty the Trash

---

**Version:** 5.1.2
**Last Updated:** January 28, 2026
