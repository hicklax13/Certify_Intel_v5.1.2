"""
Certify Intel - System Health Master Verification
Runs unit tests, api checks, and component smoke tests.
"""
import sys
import os
import asyncio
import requests
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def check_backend_api():
    print("\n[1/4] Checking Backend API (FastAPI)...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   - API is ONLINE (200 OK)")
            print(f"   - Response: {response.json()}")
            return True
        else:
            print(f"   - API returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   - API Connection Refused. Is 'uvicorn main:app' running?")
        return False

def check_database():
    print("\n[2/4] Checking Database Connectivity...")
    try:
        from database import SessionLocal
        db = SessionLocal()
        # Simple query
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        print("   - Database Connection: PASS")
        return True
    except Exception as e:
        print(f"   - Database Connection: FAIL ({str(e)})")
        return False

def check_ai_config():
    print("\n[3/4] Checking AI Configuration...")
    key = os.getenv("OPENAI_API_KEY")
    if key and key.startswith("sk-"):
        print("   - OpenAI Key: PRESENT")
        return True
    else:
        print("   - OpenAI Key: MISSING or Invalid format")
        return False

async def run_scraper_check():
    print("\n[4/4] Running Scraper Verification Script...")
    from verify_scrapers import verify_scrapers
    await verify_scrapers()

def main():
    print("="*60)
    print(f"CERTIFY INTEL SYSTEM HEALTH CHECK - {datetime.now()}")
    print("="*60)
    
    # 1. DB
    check_database()
    
    # 2. AI
    check_ai_config()
    
    # 3. API
    api_ok = check_backend_api()
    if not api_ok:
        print("   ! WARNING: Live API check failed. Start the server with `uvicorn main:app` to fix.")

    # 4. Scrapers
    asyncio.run(run_scraper_check())
    
    print("\nHealth Check Complete.")

if __name__ == "__main__":
    main()
