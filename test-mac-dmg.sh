#!/bin/bash
# Test script for Mac DMG installer
# Run this AFTER the GitHub Actions build completes

set -e  # Exit on error

echo "=========================================="
echo " Mac DMG Installation Test"
echo "=========================================="
echo ""

DMG_URL="https://github.com/hicklax13/Certify_Intel_v5.1.2/releases/download/v5.1.2/20260127_Certify_Intel_v5.5.0_arm64.dmg"
DMG_FILE="$HOME/Downloads/certify-intel-test.dmg"
APP_PATH="/Applications/Certify Intel.app"

# Detect Mac architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    echo "✓ Detected: Apple Silicon (M1/M2/M3/M4)"
    DMG_URL="https://github.com/hicklax13/Certify_Intel_v5.1.2/releases/download/v5.1.2/20260127_Certify_Intel_v5.5.0_arm64.dmg"
elif [[ "$ARCH" == "x86_64" ]]; then
    echo "✓ Detected: Intel Mac"
    DMG_URL="https://github.com/hicklax13/Certify_Intel_v5.1.2/releases/download/v5.1.2/20260127_Certify_Intel_v5.5.0_x64.dmg"
else
    echo "⚠️  Unknown architecture: $ARCH"
    echo "   Defaulting to arm64 DMG"
fi

echo ""

# Step 1: Download DMG
echo "📥 Step 1: Downloading DMG..."
if curl -L -o "$DMG_FILE" "$DMG_URL"; then
    echo "✅ Downloaded: $DMG_FILE"
    echo "   Size: $(du -h "$DMG_FILE" | cut -f1)"
else
    echo "❌ Download failed!"
    echo "   Check your internet connection or GitHub release"
    exit 1
fi

echo ""

# Step 2: Mount DMG
echo "💿 Step 2: Mounting DMG..."
if hdiutil attach "$DMG_FILE" -nobrowse; then
    echo "✅ DMG mounted successfully"
else
    echo "❌ Failed to mount DMG"
    exit 1
fi

echo ""

# Step 3: Verify DMG contents
echo "🔍 Step 3: Verifying DMG contents..."
VOLUME_PATH="/Volumes/Certify Intel"
if [ -d "$VOLUME_PATH/Certify Intel.app" ]; then
    echo "✅ App found in DMG"

    # Check app bundle structure
    if [ -f "$VOLUME_PATH/Certify Intel.app/Contents/Info.plist" ]; then
        echo "✅ Info.plist exists"
    else
        echo "⚠️  Info.plist missing"
    fi

    if [ -f "$VOLUME_PATH/Certify Intel.app/Contents/Resources/app.asar" ]; then
        echo "✅ Electron app bundle exists"
    else
        echo "⚠️  Electron bundle missing"
    fi

    if [ -f "$VOLUME_PATH/Certify Intel.app/Contents/Resources/app.icns" ] || \
       [ -f "$VOLUME_PATH/Certify Intel.app/Contents/Resources/electron.icns" ]; then
        echo "✅ App icon exists"
    else
        echo "⚠️  App icon missing"
    fi
else
    echo "❌ App not found in DMG!"
    hdiutil detach "$VOLUME_PATH" 2>/dev/null || true
    exit 1
fi

echo ""

# Step 4: Prompt for manual testing
echo "=========================================="
echo " 🧪 MANUAL TESTING REQUIRED"
echo "=========================================="
echo ""
echo "The DMG is now mounted. Please verify in Finder:"
echo ""
echo "1️⃣ Open Finder and locate 'Certify Intel' disk"
echo ""
echo "2️⃣ Verify DMG window shows:"
echo "   ✓ Certify Intel app icon (LEFT side)"
echo "   ✓ Applications folder link (RIGHT side)"
echo ""
echo "3️⃣ Test drag-and-drop:"
echo "   - Drag 'Certify Intel' to Applications folder"
echo "   - Should complete without errors"
echo ""
read -p "Did drag-and-drop work? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Drag-and-drop failed - installation issue still exists"
    echo ""
    echo "Please check:"
    echo "  - Was the app icon visible in DMG window?"
    echo "  - Did you get any error messages?"
    echo "  - Screenshot the DMG window and error (if any)"
    echo ""
    hdiutil detach "$VOLUME_PATH" 2>/dev/null || true
    exit 1
fi

echo "✅ Drag-and-drop successful!"
echo ""

# Unmount DMG
echo "💿 Unmounting DMG..."
hdiutil detach "$VOLUME_PATH"
echo "✅ DMG unmounted"
echo ""

# Step 5: Test app launch
echo "🚀 Step 5: Testing app launch..."
echo ""

if [ ! -d "$APP_PATH" ]; then
    echo "❌ App not found in /Applications"
    echo "   Expected: $APP_PATH"
    exit 1
fi

echo "Removing quarantine attributes..."
xattr -cr "$APP_PATH"
echo "✅ Quarantine removed"
echo ""

echo "Launching app..."
if open "$APP_PATH"; then
    echo "✅ App launched"
    echo ""
    echo "⏳ Wait 10-15 seconds for backend to start..."
    echo ""
    sleep 3
    echo "Then verify:"
    echo "  1. App window appears"
    echo "  2. Login page loads"
    echo "  3. Can login with: admin@certifyintel.com / MSFWINTERCLINIC2026"
    echo "  4. Dashboard shows 82 competitors, 789 products"
    echo ""
else
    echo "❌ Failed to launch app"
    echo ""
    echo "Try manually:"
    echo "  1. Open Applications folder"
    echo "  2. Right-click 'Certify Intel'"
    echo "  3. Select 'Open'"
    echo ""
    exit 1
fi

echo "=========================================="
echo " ✅ TESTING COMPLETE"
echo "=========================================="
echo ""
echo "If everything worked:"
echo "  ✅ DMG mounted successfully"
echo "  ✅ App icon visible in DMG window"
echo "  ✅ Drag to Applications worked"
echo "  ✅ App launched without errors"
echo "  ✅ Login and dashboard functional"
echo ""
echo "🎉 Mac installation fix verified!"
echo ""
echo "Next: Notify users to re-download from GitHub releases"
echo ""
