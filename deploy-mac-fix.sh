#!/bin/bash
# Deployment script for Mac installation fixes
# Run this to push changes and get instructions for triggering the build

set -e  # Exit on error

echo "=========================================="
echo " Mac Installation Fix - Deployment"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "MAC_INSTALL_FIX_SUMMARY.md" ]; then
    echo "❌ ERROR: Please run this script from the repository root"
    exit 1
fi

# Show what will be pushed
echo "📋 Commits to be pushed:"
echo ""
git log --oneline origin/master..HEAD
echo ""

# Confirm
read -p "Push these 5 commits to GitHub? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
if git push origin master; then
    echo "✅ Successfully pushed to GitHub!"
    echo ""

    # Show next steps
    echo "=========================================="
    echo " ✅ PUSH COMPLETE - Next Steps"
    echo "=========================================="
    echo ""
    echo "1️⃣ Trigger GitHub Actions Build:"
    echo "   URL: https://github.com/hicklax13/Certify_Intel_v5.1.2/actions"
    echo ""
    echo "   Steps:"
    echo "   - Click 'Actions' tab"
    echo "   - Click 'Build Mac Installer' workflow"
    echo "   - Click 'Run workflow' button"
    echo "   - Select branch: master"
    echo "   - Click 'Run workflow'"
    echo "   - Wait ~10-15 minutes for build"
    echo ""
    echo "2️⃣ Monitor Build Progress:"
    echo "   Watch for these steps to complete:"
    echo "   ✓ Create Mac icon from PNG"
    echo "   ✓ Build macOS installer"
    echo "   ✓ Upload to existing v5.1.2 release"
    echo ""
    echo "3️⃣ Test New DMG:"
    echo "   After build completes, run:"
    echo "   ./test-mac-dmg.sh"
    echo ""
    echo "=========================================="
    echo ""

    # Open browser to Actions page
    if command -v open &> /dev/null; then
        read -p "Open GitHub Actions in browser? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "https://github.com/hicklax13/Certify_Intel_v5.1.2/actions"
            echo "✅ Opened browser"
        fi
    fi

else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "Possible issues:"
    echo "  - GitHub credentials not configured"
    echo "  - No network connection"
    echo "  - Permission denied"
    echo ""
    echo "Try:"
    echo "  git push origin master"
    echo ""
    exit 1
fi

echo ""
echo "📖 For detailed instructions, see: NEXT_STEPS.md"
echo ""
