# Certify Intel - Mac Installation Guide
## Version 5.1.2

---

## Step 1: Download the Mac Installer

1. Go to **https://github.com/hicklax13/Certify_Intel_v5.1.2/releases/tag/v5.1.2**

2. Scroll down to the **Assets** section

3. Click the correct file for your Mac:
   - **Apple Silicon Mac** (M1, M2, M3, M4 chips): Download `20260127_Certify_Intel_v5.5.0_arm64.dmg`
   - **Intel Mac** (older Macs): Download `20260127_Certify_Intel_v5.5.0_x64.dmg`

   **Not sure which Mac you have?**
   - Click the Apple menu in the top-left corner
   - Click "About This Mac"
   - Look for "Chip" - if it says "Apple M1/M2/M3/M4", download the arm64 version
   - If it says "Intel", download the x64 version

4. Wait for the download to complete (file is approximately 280-290 MB)

---

## Step 2: Install the Application

1. Open your **Downloads** folder

2. Double-click the downloaded `.dmg` file to open it

3. A window will appear showing the Certify Intel app and an Applications folder shortcut

4. **Drag the Certify Intel icon** to the **Applications** folder

5. Wait for the copy to complete

6. Close the DMG window

7. (Optional) Right-click the DMG file on your desktop and select "Eject" to clean up

---

## Step 3: First Launch (Important - Security Step)

Because this app is not from the Mac App Store, macOS will ask for permission:

1. Open your **Applications** folder (in Finder, click Go > Applications)

2. Find **Certify Intel**

3. **Right-click** (or Control-click) on Certify Intel

4. Select **"Open"** from the menu

5. A security dialog will appear - click **"Open"** again to confirm

   **Note:** You only need to do this right-click "Open" the first time. After that, you can launch normally.

6. Wait for the app to start (a loading screen will appear briefly)

---

## Step 4: Log In to the Application

1. The login screen will appear

2. Enter your credentials:
   - **Email:** `admin@certifyintel.com`
   - **Password:** `MSFWINTERCLINIC2026`

3. Click **"Sign In"**

4. You're now in the Certify Intel dashboard!

---

## Troubleshooting

### "Certify Intel is damaged and can't be opened"

If you see this error:
1. Open **Terminal** (search for it in Spotlight)
2. Copy and paste this command, then press Enter:
   ```
   xattr -cr /Applications/Certify\ Intel.app
   ```
3. Try opening the app again

### "Cannot be opened because the developer cannot be verified"

1. Right-click the app and select "Open"
2. Click "Open" in the dialog that appears
3. The app will now open normally in the future

### App closes immediately after opening

1. Make sure you downloaded the correct version for your Mac (arm64 vs x64)
2. Try restarting your Mac
3. Re-download and reinstall the app

### Backend server failed to start

1. Make sure no other application is using port 8000
2. Check if you have another instance of Certify Intel running
3. Restart your Mac and try again

---

## Uninstalling

1. Open **Applications** folder
2. Drag **Certify Intel** to the Trash
3. Empty the Trash

---

## Support

For issues or questions:
- Visit: https://github.com/hicklax13/Certify_Intel_v5.1.2/issues
- Email: support@certifyhealth.com

---

**Version:** 5.1.2
**Last Updated:** January 27, 2026
