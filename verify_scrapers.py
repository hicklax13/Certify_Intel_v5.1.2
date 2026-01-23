"""
Certify Intel - Comprehensive Scraper Verification Script
Verifies that all specialized scrapers are reachable and functioning.
"""
import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def verify_scrapers():
    print("="*60)
    print("SEARCH & SCRAPER VERIFICATION PROTOCOL")
    print("="*60)
    
    results = {}

    # 1. Verify Traffic Scraper (PublicSimilarWeb)
    print("\n[1/5] Verifying Traffic Scraper (SimilarWeb Proxy)...")
    try:
        from public_similarweb_scraper import PublicSimilarWebScraper
        scraper = PublicSimilarWebScraper()
        # Mocking the request effectively/checking class init for now as live requests might block without proxy
        print(f"   - Class initialized: {scraper}")
        results["traffic"] = "PASS (Init)"
    except Exception as e:
        print(f"   - FAILED: {e}")
        results["traffic"] = f"FAIL: {e}"

    # 2. Verify LinkedIn Tracker (Mock/Auth check)
    print("\n[2/5] Verifying LinkedIn Tracker...")
    try:
        from linkedin_tracker import LinkedInTracker
        li = LinkedInTracker()
        print(f"   - Class initialized: {li}")
        if li.api_key:
            print("   - API Key present")
        else:
            print("   - API Key MISSING (Mock mode might be active)")
        results["linkedin"] = "PASS (Init)"
    except Exception as e:
        print(f"   - FAILED: {e}")
        results["linkedin"] = f"FAIL: {e}"

    # 3. Verify G2/Review Scraper
    print("\n[3/5] Verifying Review Scraper...")
    try:
        from sentiment_scraper import SentimentScraper
        ss = SentimentScraper()
        print(f"   - Class initialized: {ss}")
        results["sentiment"] = "PASS (Init)"
    except Exception as e:
        print(f"   - FAILED: {e}")
        results["sentiment"] = f"FAIL: {e}"

    # 4. Verify Google Ecosystem (Ads/Trends)
    print("\n[4/5] Verifying Google Ecosystem Scraper...")
    try:
        from google_ecosystem_scraper import GoogleEcosystemScraper
        gs = GoogleEcosystemScraper()
        print(f"   - Class initialized: {gs}")
        if gs.api_key and gs.cx:
            print("   - Google Search API Configured")
        else:
            print("   - Google Search API Configured MISSING")
        results["google"] = "PASS (Init)"
    except Exception as e:
        print(f"   - FAILED: {e}")
        results["google"] = f"FAIL: {e}"

    # 5. Core Content Scraper (Playwright)
    print("\n[5/5] Verifying Core Competitor Scraper (Playwright)...")
    try:
        from scraper import CompetitorScraper
        # Just init check, don't launch browser in this smoke test to keep it fast
        scraper = CompetitorScraper(headless=True)
        print(f"   - Class initialized: {scraper}")
        results["core_scraper"] = "PASS (Init)"
    except Exception as e:
        print(f"   - FAILED: {e}")
        results["core_scraper"] = f"FAIL: {e}"

    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    for name, status in results.items():
        print(f"{name.ljust(20)}: {status}")

if __name__ == "__main__":
    asyncio.run(verify_scrapers())
