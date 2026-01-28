#!/bin/bash
# Pre-push validation script
# Runs checks before pushing Mac installation fixes

set -e

echo "=========================================="
echo " Pre-Push Validation Check"
echo "=========================================="
echo ""

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: icon.icns exists
echo -n "Checking icon.icns exists... "
if [ -f "desktop-app/resources/icons/icon.icns" ]; then
    SIZE=$(du -h "desktop-app/resources/icons/icon.icns" | cut -f1)
    echo -e "${GREEN}✓${NC} ($SIZE)"
else
    echo -e "${RED}✗ MISSING${NC}"
    ((ERRORS++))
fi

# Check 2: icon.icns is valid Mac icon
echo -n "Validating icon.icns format... "
FILE_TYPE=$(file "desktop-app/resources/icons/icon.icns" 2>/dev/null | grep -o "Mac OS X icon" || echo "")
if [ ! -z "$FILE_TYPE" ]; then
    echo -e "${GREEN}✓${NC} Valid Mac OS X icon"
else
    echo -e "${RED}✗ Invalid format${NC}"
    ((ERRORS++))
fi

# Check 3: package.json DMG config has "type": "file"
echo -n "Checking DMG config... "
if grep -q '"type": "file"' "desktop-app/package.json"; then
    echo -e "${GREEN}✓${NC} Has type: file"
else
    echo -e "${RED}✗ Missing type specification${NC}"
    ((ERRORS++))
fi

# Check 4: package.json has correct repo
echo -n "Checking repository reference... "
if grep -q '"repo": "Certify_Intel_v5.1.2"' "desktop-app/package.json"; then
    echo -e "${GREEN}✓${NC} Correct repo name"
else
    echo -e "${YELLOW}⚠${NC}  Old repo name"
    ((WARNINGS++))
fi

# Check 5: GitHub Actions workflow exists
echo -n "Checking GitHub Actions workflow... "
if [ -f ".github/workflows/build-mac-only.yml" ]; then
    echo -e "${GREEN}✓${NC} Workflow file exists"
else
    echo -e "${RED}✗ Workflow missing${NC}"
    ((ERRORS++))
fi

# Check 6: Deployment scripts are executable
echo -n "Checking deployment scripts... "
if [ -x "deploy-mac-fix.sh" ] && [ -x "test-mac-dmg.sh" ]; then
    echo -e "${GREEN}✓${NC} Scripts executable"
else
    echo -e "${YELLOW}⚠${NC}  Scripts not executable"
    ((WARNINGS++))
fi

# Check 7: Git status clean
echo -n "Checking git status... "
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✓${NC} Working tree clean"
else
    echo -e "${YELLOW}⚠${NC}  Uncommitted changes"
    git status --short
    ((WARNINGS++))
fi

# Check 8: Count commits ahead
echo -n "Checking commits to push... "
COMMITS_AHEAD=$(git rev-list --count origin/master..HEAD 2>/dev/null || echo "0")
if [ "$COMMITS_AHEAD" -gt "0" ]; then
    echo -e "${GREEN}✓${NC} $COMMITS_AHEAD commits ready"
else
    echo -e "${YELLOW}⚠${NC}  No commits to push"
    ((WARNINGS++))
fi

# Check 9: Documentation files exist
echo -n "Checking documentation... "
DOCS_OK=true
[ ! -f "MAC_INSTALL_FIX_SUMMARY.md" ] && DOCS_OK=false
[ ! -f "NEXT_STEPS.md" ] && DOCS_OK=false
[ ! -f "SESSION_21_COMPLETE.md" ] && DOCS_OK=false

if $DOCS_OK; then
    echo -e "${GREEN}✓${NC} All docs present"
else
    echo -e "${YELLOW}⚠${NC}  Some docs missing"
    ((WARNINGS++))
fi

# Check 10: Frontend files exist in desktop-app
echo -n "Checking frontend files... "
if [ -d "desktop-app/frontend" ] && [ -f "desktop-app/frontend/index.html" ]; then
    echo -e "${GREEN}✓${NC} Frontend files present"
else
    echo -e "${RED}✗ Frontend missing${NC}"
    ((ERRORS++))
fi

echo ""
echo "=========================================="
echo " Validation Results"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Ready to push!"
    echo ""
    echo "Next steps:"
    echo "  1. git push origin master"
    echo "  2. Trigger GitHub Actions build"
    echo "  3. Test new DMG installer"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  PASSED WITH WARNINGS${NC}"
    echo ""
    echo "Warnings: $WARNINGS"
    echo ""
    echo "You can proceed, but review warnings above."
    echo ""
    exit 0
else
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo ""
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "Fix errors before pushing."
    echo ""
    exit 1
fi
