#!/bin/bash

# Trigger Mac Build via GitHub Actions
# This script triggers the "Build Mac Installer" workflow

echo "🚀 Triggering Mac build on GitHub Actions..."
echo ""
echo "Opening GitHub Actions page in your browser..."
echo ""
echo "Manual steps:"
echo "1. Click 'Build Mac Installer (Add to Existing Release)' workflow"
echo "2. Click 'Run workflow' button (top right)"
echo "3. Select branch: master"
echo "4. Click green 'Run workflow' button"
echo ""
echo "The new build will include debugging to show if GitHub Secrets are accessible."
echo ""

# Open GitHub Actions page in default browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "https://github.com/hicklax13/Certify_Intel_v5.1.2/actions/workflows/build-mac-only.yml"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "https://github.com/hicklax13/Certify_Intel_v5.1.2/actions/workflows/build-mac-only.yml"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows Git Bash
    start "https://github.com/hicklax13/Certify_Intel_v5.1.2/actions/workflows/build-mac-only.yml"
fi

echo ""
echo "✅ GitHub Actions page should open in your browser"
echo ""
