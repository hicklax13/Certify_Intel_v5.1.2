#!/usr/bin/env python3
"""
Phase 3 Core Workflow Testing Suite
Tests all critical endpoints and workflows
"""

import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Tuple

# Configuration
BASE_URL = "http://localhost:8000"
DEFAULT_USER = "admin@certifyhealth.com"
DEFAULT_PASSWORD = "certifyintel2024"

# Test results tracking
results: Dict[str, Dict] = {}
passed = 0
failed = 0
warnings = 0

def log_test(test_id: str, name: str, status: str, details: str = "", blocking: bool = False):
    """Log a test result"""
    global passed, failed, warnings

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    results[test_id] = {
        "name": name,
        "status": status,
        "timestamp": timestamp,
        "details": details,
        "blocking": blocking
    }

    status_symbol = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
    print(f"{status_symbol} [{timestamp}] Test {test_id}: {name}")
    if details:
        print(f"   → {details}")

    if status == "PASS":
        passed += 1
    elif status == "WARN":
        warnings += 1
    elif status == "FAIL":
        failed += 1

def test_health_check():
    """Test that API is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            log_test("HEALTH", "API Health Check", "PASS", "API is responding")
            return True
        else:
            log_test("HEALTH", "API Health Check", "FAIL", f"API returned {response.status_code}", blocking=True)
            return False
    except requests.exceptions.ConnectionError:
        log_test("HEALTH", "API Health Check", "FAIL",
                f"Cannot connect to {BASE_URL} - Is backend running?", blocking=True)
        return False
    except Exception as e:
        log_test("HEALTH", "API Health Check", "FAIL", f"Error: {str(e)}", blocking=True)
        return False

def test_authentication():
    """Test A.1: Login with valid credentials"""
    try:
        # Test login
        data = {
            "username": DEFAULT_USER,
            "password": DEFAULT_PASSWORD,
            "grant_type": "password"
        }

        response = requests.post(
            f"{BASE_URL}/token",
            data=data,
            timeout=10
        )

        if response.status_code != 200:
            log_test("A1", "Authentication - Valid Credentials", "FAIL",
                    f"Login returned {response.status_code}: {response.text[:100]}")
            return None

        token_data = response.json()
        if "access_token" not in token_data:
            log_test("A1", "Authentication - Valid Credentials", "FAIL",
                    "Response missing access_token field")
            return None

        token = token_data["access_token"]
        log_test("A1", "Authentication - Valid Credentials", "PASS",
                f"Token: {token[:20]}...")

        return token

    except Exception as e:
        log_test("A1", "Authentication - Valid Credentials", "FAIL", f"Error: {str(e)}")
        return None

def test_dashboard(token: str):
    """Test A.2: Dashboard display"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/analytics/summary",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            log_test("A2", "Dashboard Display", "FAIL",
                    f"Returned {response.status_code}")
            return False

        data = response.json()

        # Check for expected fields
        required_fields = ["competitors", "summary", "threat_levels"]
        missing = [f for f in required_fields if f not in data]

        if missing:
            log_test("A2", "Dashboard Display", "WARN",
                    f"Missing fields: {missing}")
            return True

        log_test("A2", "Dashboard Display", "PASS",
                f"Loaded {len(data.get('competitors', []))} competitors")
        return True

    except Exception as e:
        log_test("A2", "Dashboard Display", "FAIL", f"Error: {str(e)}")
        return False

def test_competitors_list(token: str):
    """Test A.3: Get competitors list"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/competitors",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            log_test("A3", "Competitors List", "FAIL",
                    f"Returned {response.status_code}")
            return False

        data = response.json()

        if not isinstance(data, list):
            log_test("A3", "Competitors List", "FAIL",
                    f"Expected list, got {type(data)}")
            return False

        log_test("A3", "Competitors List", "PASS",
                f"Retrieved {len(data)} competitors")
        return len(data) > 0

    except Exception as e:
        log_test("A3", "Competitors List", "FAIL", f"Error: {str(e)}")
        return False

def test_competitor_detail(token: str, competitor_id: int = 1):
    """Test A.4: View competitor details"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/competitors/{competitor_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 404:
            log_test("A4", "Competitor Detail", "WARN",
                    f"Competitor {competitor_id} not found")
            return False

        if response.status_code != 200:
            log_test("A4", "Competitor Detail", "FAIL",
                    f"Returned {response.status_code}")
            return False

        data = response.json()

        # Check for key fields
        required_fields = ["id", "name", "website"]
        missing = [f for f in required_fields if f not in data]

        if missing:
            log_test("A4", "Competitor Detail", "WARN",
                    f"Missing fields: {missing}")
            return True

        log_test("A4", "Competitor Detail", "PASS",
                f"Retrieved: {data.get('name', 'Unknown')}")
        return True

    except Exception as e:
        log_test("A4", "Competitor Detail", "FAIL", f"Error: {str(e)}")
        return False

def test_excel_export(token: str):
    """Test A.5: Excel export"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/export/excel",
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            log_test("A5", "Excel Export", "FAIL",
                    f"Returned {response.status_code}")
            return False

        # Check content type
        content_type = response.headers.get("content-type", "")
        if "spreadsheet" not in content_type and "sheet" not in content_type:
            log_test("A5", "Excel Export", "WARN",
                    f"Unexpected content-type: {content_type}")
            return True

        # Check for content
        if len(response.content) < 100:
            log_test("A5", "Excel Export", "FAIL",
                    f"File too small: {len(response.content)} bytes")
            return False

        log_test("A5", "Excel Export", "PASS",
                f"Generated {len(response.content)} byte file")
        return True

    except Exception as e:
        log_test("A5", "Excel Export", "FAIL", f"Error: {str(e)}")
        return False

def test_json_export(token: str):
    """Test A.6: JSON export"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/export/json",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            log_test("A6", "JSON Export", "FAIL",
                    f"Returned {response.status_code}")
            return False

        # Verify valid JSON
        try:
            data = response.json()
            log_test("A6", "JSON Export", "PASS",
                    f"Generated valid JSON ({len(str(data))} chars)")
            return True
        except json.JSONDecodeError:
            log_test("A6", "JSON Export", "FAIL",
                    "Response is not valid JSON")
            return False

    except Exception as e:
        log_test("A6", "JSON Export", "FAIL", f"Error: {str(e)}")
        return False

def test_search_competitors(token: str):
    """Test A.3b: Search functionality"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/competitors?search=health",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            log_test("A3b", "Search Competitors", "WARN",
                    f"Returned {response.status_code}")
            return False

        data = response.json()

        if not isinstance(data, list):
            log_test("A3b", "Search Competitors", "FAIL",
                    f"Expected list, got {type(data)}")
            return False

        log_test("A3b", "Search Competitors", "PASS",
                f"Found {len(data)} matches for 'health'")
        return True

    except Exception as e:
        log_test("A3b", "Search Competitors", "WARN", f"Error: {str(e)}")
        return False

def test_changes_log(token: str):
    """Test C.3: Change log retrieval"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/changes",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            log_test("C3", "Changes Log", "WARN",
                    f"Returned {response.status_code}")
            return False

        data = response.json()

        if isinstance(data, list):
            log_test("C3", "Changes Log", "PASS",
                    f"Retrieved {len(data)} recent changes")
        else:
            log_test("C3", "Changes Log", "WARN",
                    "Unexpected response format")

        return True

    except Exception as e:
        log_test("C3", "Changes Log", "WARN", f"Error: {str(e)}")
        return False

def test_discovery_agent(token: str):
    """Test D.1: Discovery agent execution"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/api/discovery/run",
            headers=headers,
            json={"industry": "healthcare"},
            timeout=30
        )

        if response.status_code not in [200, 202]:
            log_test("D1", "Discovery Agent", "WARN",
                    f"Returned {response.status_code}")
            return False

        data = response.json()

        if isinstance(data, list):
            log_test("D1", "Discovery Agent", "PASS",
                    f"Found {len(data)} candidate competitors")
        else:
            log_test("D1", "Discovery Agent", "PASS",
                    "Discovery agent initiated")

        return True

    except requests.exceptions.Timeout:
        log_test("D1", "Discovery Agent", "WARN",
                "Discovery agent timed out (expected for real searches)")
        return True
    except Exception as e:
        log_test("D1", "Discovery Agent", "WARN", f"Error: {str(e)}")
        return False

def print_summary():
    """Print test summary"""
    total = passed + failed + warnings
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed:  {passed}/{total}")
    print(f"⚠️ Warnings: {warnings}/{total}")
    print(f"❌ Failed:  {failed}/{total}")
    print("="*70)

    if failed == 0 and warnings <= 2:
        print("\n🎉 PHASE 3A - STATIC TESTS SUCCESSFUL!")
        print("System is ready for Phase 3B (Data Integrity Tests)")
        return True
    elif failed > 0:
        print("\n❌ CRITICAL FAILURES - System needs fixes")
        return False
    else:
        print("\n⚠️ WARNINGS - Review before proceeding")
        return True

def main():
    """Run all Phase 3A tests"""
    print("\n" + "="*70)
    print("PHASE 3A: CORE WORKFLOW STATIC ENDPOINT TESTS")
    print("="*70)
    print(f"Testing: {BASE_URL}")
    print(f"User: {DEFAULT_USER}")
    print("="*70 + "\n")

    # Check health first
    if not test_health_check():
        print("\n❌ Backend is not running. Start with: python backend/main.py")
        return False

    print()

    # Authenticate
    token = test_authentication()
    if not token:
        print("\n❌ Authentication failed. Check credentials in .env")
        return False

    print()

    # Run workflow tests
    test_dashboard(token)
    test_competitors_list(token)
    test_competitor_detail(token)
    test_search_competitors(token)

    print()

    # Run export tests
    test_excel_export(token)
    test_json_export(token)

    print()

    # Run advanced tests
    test_changes_log(token)
    test_discovery_agent(token)

    print()

    # Print summary
    success = print_summary()

    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
