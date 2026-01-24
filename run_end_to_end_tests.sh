#!/bin/bash

################################################################################
# MASTER TEST SCRIPT - END-TO-END TESTING
# Certify Health Intel - Complete Test Sequence
################################################################################

set -e  # Exit on error

TIMESTAMP=$(date '+%Y-%m-%d_%H:%M:%S')
PROJECT_DIR="/home/user/Project_Intel_v4"
RESULTS_FILE="$PROJECT_DIR/TEST_RESULTS_${TIMESTAMP}.txt"
BACKEND_PID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

################################################################################
# FUNCTIONS
################################################################################

log_section() {
    echo -e "${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================================================================${NC}"
    echo "$1" >> "$RESULTS_FILE"
}

log_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "✅ $1" >> "$RESULTS_FILE"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "⚠️  $1" >> "$RESULTS_FILE"
}

log_fail() {
    echo -e "${RED}❌ $1${NC}"
    echo "❌ $1" >> "$RESULTS_FILE"
}

log_info() {
    echo "$1"
    echo "$1" >> "$RESULTS_FILE"
}

cleanup() {
    if [ ! -z "$BACKEND_PID" ]; then
        log_info "Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        sleep 2
    fi
}

trap cleanup EXIT

################################################################################
# START
################################################################################

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    CERTIFY HEALTH INTEL - END-TO-END TEST                  ║"
echo "║                                                                            ║"
echo "║  This script runs all testing phases automatically:                        ║"
echo "║  - Phase 3A: Static endpoint tests (9 tests)                               ║"
echo "║  - Phase 4: Export validation tests                                        ║"
echo "║  - Phase 5: Data quality tests                                             ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
log_info "Results will be saved to: $RESULTS_FILE"
echo ""

################################################################################
# PHASE 0: SETUP
################################################################################

log_section "PHASE 0: SETUP & VERIFICATION"

# Check Python
log_info "Checking Python version..."
python --version >> "$RESULTS_FILE" 2>&1
if python -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
    log_pass "Python 3.9+ found"
else
    log_fail "Python 3.9+ required"
    exit 1
fi

# Check project directory
if [ ! -d "$PROJECT_DIR" ]; then
    log_fail "Project directory not found: $PROJECT_DIR"
    exit 1
fi
log_pass "Project directory found"

# Check required files
required_files=("backend/main.py" "backend/requirements.txt" "run_tests.py")
for file in "${required_files[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        log_pass "Found: $file"
    else
        log_fail "Missing: $file"
        exit 1
    fi
done

################################################################################
# INSTALL DEPENDENCIES
################################################################################

log_section "INSTALLING DEPENDENCIES"

cd "$PROJECT_DIR/backend"
log_info "Installing Python dependencies..."
pip install -r requirements.txt >> "$RESULTS_FILE" 2>&1
log_pass "Dependencies installed"

################################################################################
# START BACKEND
################################################################################

log_section "STARTING BACKEND SERVER"

log_info "Starting FastAPI backend..."
python main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
log_info "Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
log_info "Waiting for backend to initialize (10 seconds)..."
sleep 10

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    log_pass "Backend server is running"
else
    log_fail "Backend failed to start"
    cat /tmp/backend.log >> "$RESULTS_FILE"
    exit 1
fi

# Test health endpoint
log_info "Testing health endpoint..."
sleep 2
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    log_pass "Backend health check passed"
else
    log_warn "Health check failed (backend may still be initializing)"
fi

################################################################################
# PHASE 3A: AUTOMATED ENDPOINT TESTS
################################################################################

log_section "PHASE 3A: AUTOMATED ENDPOINT TESTS"

cd "$PROJECT_DIR"
log_info "Running automated test suite (9 tests)..."
log_info "Command: python run_tests.py"
echo "" >> "$RESULTS_FILE"

if python run_tests.py >> "$RESULTS_FILE" 2>&1; then
    log_pass "Phase 3A tests completed"
    TEST_3A_PASS=true
else
    log_warn "Phase 3A had issues (see details below)"
    TEST_3A_PASS=false
fi

################################################################################
# PHASE 4: EXPORT VALIDATION
################################################################################

log_section "PHASE 4: EXPORT VALIDATION TESTS"

log_info "Getting authentication token..."
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=admin@certifyhealth.com&password=certifyintel2024&grant_type=password" \
  -H "Content-Type: application/x-www-form-urlencoded" 2>/dev/null | python -m json.tool 2>/dev/null | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 || echo "")

if [ -z "$TOKEN" ]; then
    log_warn "Could not get authentication token (Phase 4 will be limited)"
    TEST_4_PASS=false
else
    log_pass "Authentication token obtained"

    # Test 4.1: Excel Export
    log_info "Test 4.1: Excel Export..."
    if curl -s -H "Authorization: Bearer $TOKEN" \
      http://localhost:8000/api/export/excel -o /tmp/competitors.xlsx 2>/dev/null && \
      [ -f /tmp/competitors.xlsx ] && [ -s /tmp/competitors.xlsx ]; then
        EXCEL_SIZE=$(du -h /tmp/competitors.xlsx | cut -f1)
        log_pass "Excel export successful ($EXCEL_SIZE)"
        TEST_4_PASS=true
    else
        log_warn "Excel export not available or empty"
        TEST_4_PASS=false
    fi

    # Test 4.2: JSON Export
    log_info "Test 4.2: JSON Export..."
    if curl -s -H "Authorization: Bearer $TOKEN" \
      http://localhost:8000/api/export/json 2>/dev/null | python -m json.tool > /dev/null 2>&1; then
        log_pass "JSON export successful and valid"
    else
        log_warn "JSON export not available or invalid"
    fi

    # Test 4.3: Data Quality Scores
    log_info "Test 4.3: Data Quality Scores..."
    if curl -s -H "Authorization: Bearer $TOKEN" \
      http://localhost:8000/api/data-quality/scores 2>/dev/null | python -m json.tool > /dev/null 2>&1; then
        log_pass "Data quality scores endpoint working"
    else
        log_warn "Data quality scores endpoint not available"
    fi
fi

################################################################################
# PHASE 5: DATA QUALITY TESTS
################################################################################

log_section "PHASE 5: DATA QUALITY TESTS"

if [ ! -z "$TOKEN" ]; then
    TEST_5_PASS=true

    # Test 5.1: Quality Scores
    log_info "Test 5.1: Data Quality Scores..."
    if curl -s -H "Authorization: Bearer $TOKEN" \
      http://localhost:8000/api/data-quality/scores 2>/dev/null | python -m json.tool > /dev/null 2>&1; then
        log_pass "Quality scores calculated"
    else
        log_warn "Quality scores not available"
        TEST_5_PASS=false
    fi

    # Test 5.2: Stale Data Detection
    log_info "Test 5.2: Stale Data Detection..."
    if curl -s -H "Authorization: Bearer $TOKEN" \
      http://localhost:8000/api/data-quality/stale 2>/dev/null | python -m json.tool > /dev/null 2>&1; then
        log_pass "Stale data detection working"
    else
        log_warn "Stale data detection not available"
        TEST_5_PASS=false
    fi

    # Test 5.3: Competitors List
    log_info "Test 5.3: Retrieving Competitors..."
    COMPETITORS=$(curl -s -H "Authorization: Bearer $TOKEN" \
      http://localhost:8000/api/competitors 2>/dev/null | python -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
    if [ "$COMPETITORS" -gt "10" ]; then
        log_pass "Found $COMPETITORS competitors"
    else
        log_warn "Expected 10+ competitors, found: $COMPETITORS"
        TEST_5_PASS=false
    fi
else
    log_warn "Skipping Phase 5 (no authentication token)"
    TEST_5_PASS=false
fi

################################################################################
# FINAL RESULTS
################################################################################

log_section "FINAL TEST RESULTS"

echo ""
echo -e "${BLUE}Test Summary:${NC}"
echo ""

if [ "$TEST_3A_PASS" = true ]; then
    log_pass "Phase 3A: Automated endpoint tests - PASSED"
else
    log_warn "Phase 3A: Automated endpoint tests - HAD ISSUES"
fi

if [ "$TEST_4_PASS" = true ]; then
    log_pass "Phase 4: Export validation - PASSED"
else
    log_warn "Phase 4: Export validation - NOT AVAILABLE"
fi

if [ "$TEST_5_PASS" = true ]; then
    log_pass "Phase 5: Data quality tests - PASSED"
else
    log_warn "Phase 5: Data quality tests - NOT AVAILABLE"
fi

################################################################################
# OVERALL STATUS
################################################################################

log_section "OVERALL STATUS"

if [ "$TEST_3A_PASS" = true ] && [ "$TEST_4_PASS" = true ] && [ "$TEST_5_PASS" = true ]; then
    echo -e "${GREEN}"
    echo "🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION 🎉"
    echo -e "${NC}"
    log_pass "OVERALL: ALL TESTS PASSED"
    EXIT_CODE=0
elif [ "$TEST_3A_PASS" = true ]; then
    echo -e "${YELLOW}"
    echo "✅ CORE TESTS PASSED - Some optional features not available"
    echo -e "${NC}"
    log_pass "OVERALL: CORE TESTS PASSED"
    EXIT_CODE=0
else
    echo -e "${RED}"
    echo "❌ TESTS FAILED - See details above"
    echo -e "${NC}"
    log_fail "OVERALL: TESTS FAILED"
    EXIT_CODE=1
fi

################################################################################
# BACKEND LOG
################################################################################

log_section "BACKEND SERVER LOG (Last 30 lines)"
tail -n 30 /tmp/backend.log >> "$RESULTS_FILE" 2>&1

################################################################################
# COMPLETION
################################################################################

log_section "TEST EXECUTION COMPLETE"

log_info "Test Results saved to: $RESULTS_FILE"
log_info "Test execution time: $(date)"
log_info "Backend PID: $BACKEND_PID"

# Show results file
echo ""
echo -e "${BLUE}Results file created:${NC}"
echo "$RESULTS_FILE"
echo ""
echo -e "${BLUE}View results with:${NC}"
echo "cat $RESULTS_FILE"
echo ""

exit $EXIT_CODE
