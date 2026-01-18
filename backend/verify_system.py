import httpx
import time
import os
import sys
import json

BASE_URL = "http://localhost:8000"
EXPORTS_DIR = "./exports"
os.makedirs(EXPORTS_DIR, exist_ok=True)

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}[{status}] {message}{colors['RESET']}")

def verify_system():
    print_status("Starting System Verification...", "INFO")
    
    # 1. API Health & Competitors
    try:
        r = httpx.get(f"{BASE_URL}/api/competitors")
        if r.status_code == 200:
            count = len(r.json())
            print_status(f"API Connection Successful. Loaded {count} competitors.", "SUCCESS")
        else:
            print_status(f"API Error: {r.status_code} - {r.text}", "ERROR")
            return
    except Exception as e:
        print_status(f"Connection Failed: {e}", "ERROR")
        return

    # 2. Stock Data API
    try:
        # Test known ticker
        r = httpx.get(f"{BASE_URL}/api/stock/Phreesia") 
        data = r.json()
        if data.get("is_public") and data.get("ticker") == "PHR":
             print_status("Stock API (Public) Verified: Phreesia -> PHR", "SUCCESS")
        else:
             print_status(f"Stock API (Public) Failed: {data}", "ERROR")
             
        # Test private company
        r = httpx.get(f"{BASE_URL}/api/stock/UnknownPrivateCo")
        data = r.json()
        if not data.get("is_public"):
            print_status("Stock API (Private) Verified: Correctly identified private company", "SUCCESS")
    except Exception as e:
        print_status(f"Stock API Failed: {e}", "ERROR")

    # 3. Excel Export
    try:
        print_status("Testing Excel Export...", "INFO")
        r = httpx.get(f"{BASE_URL}/api/export/excel", timeout=10.0)
        if r.status_code == 200:
            filename = os.path.join(EXPORTS_DIR, "test_export.xlsx")
            with open(filename, "wb") as f:
                f.write(r.content)
            size = os.path.getsize(filename)
            if size > 1000:
                print_status(f"Excel Export Successful: {filename} ({size/1024:.1f} KB)", "SUCCESS")
            else:
                print_status("Excel Export file too small (likely empty)", "WARNING")
        else:
            print_status(f"Excel Export Failed: {r.status_code}", "ERROR")
    except Exception as e:
        print_status(f"Excel Export Failed: {e}", "ERROR")

    # 4. JSON Export
    try:
         r = httpx.get(f"{BASE_URL}/api/export/json")
         if r.status_code == 200:
             print_status("JSON Export Successful", "SUCCESS")
         else:
             print_status(f"JSON Export Failed: {r.status_code}", "ERROR")
    except Exception as e:
        print_status(f"JSON Export Failed: {e}", "ERROR")

    # 5. Report Generation (PDF)
    try:
        print_status("Testing PDF Generation (Weekly Briefing)...", "INFO")
        r = httpx.get(f"{BASE_URL}/api/reports/weekly-briefing", timeout=15.0)
        if r.status_code == 200:
            if "application/pdf" in r.headers.get("content-type", ""):
                filename = os.path.join(EXPORTS_DIR, "test_briefing.pdf")
                with open(filename, "wb") as f:
                    f.write(r.content)
                size = os.path.getsize(filename)
                print_status(f"PDF Generation Successful: {filename} ({size/1024:.1f} KB)", "SUCCESS")
            else:
                 print_status(f"PDF Endpoint returned non-PDF content: {r.text[:100]}", "WARNING")
        else:
             print_status(f"PDF Generation Failed: {r.status_code}", "ERROR")
    except Exception as e:
        print_status(f"PDF Generation Error: {e}", "ERROR")

    # 6. Battlecard PDF
    try:
        print_status("Testing PDF Generation (Battlecard)...", "INFO")
        # Try ID 1 (assumed present)
        r = httpx.get(f"{BASE_URL}/api/reports/battlecard/1", timeout=15.0)
        if r.status_code == 200:
            if "application/pdf" in r.headers.get("content-type", ""):
                 filename = os.path.join(EXPORTS_DIR, "test_battlecard.pdf")
                 with open(filename, "wb") as f:
                     f.write(r.content)
                 size = os.path.getsize(filename)
                 print_status(f"Battlecard PDF Successful: {filename} ({size/1024:.1f} KB)", "SUCCESS")
            else:
                 print_status(f"Battlecard Endpoint returned non-PDF: {r.text[:100]}", "WARNING")
        else:
             print_status(f"Battlecard Failed: {r.status_code}", "ERROR")
    except Exception as e:
        print_status(f"Battlecard Error: {e}", "ERROR")

    # 7. Comparison Report
    try:
        print_status("Testing Comparison Report...", "INFO")
        r = httpx.get(f"{BASE_URL}/api/reports/comparison", timeout=15.0)
        if r.status_code == 200:
             if "application/pdf" in r.headers.get("content-type", ""):
                 filename = os.path.join(EXPORTS_DIR, "test_comparison.pdf")
                 with open(filename, "wb") as f:
                     f.write(r.content)
                 size = os.path.getsize(filename)
                 print_status(f"Comparison PDF Successful: {filename} ({size/1024:.1f} KB)", "SUCCESS")
             else:
                 print_status(f"Comparison Endpoint returned non-PDF: {r.text[:100]}", "WARNING")
        else:
             print_status(f"Comparison Failed: {r.status_code}", "ERROR")
    except Exception as e:
        print_status(f"Comparison Error: {e}", "ERROR")

    print_status("-" * 30, "INFO")
    print_status("SYSTEM VERIFICATION COMPLETE", "SUCCESS")

if __name__ == "__main__":
    verify_system()
