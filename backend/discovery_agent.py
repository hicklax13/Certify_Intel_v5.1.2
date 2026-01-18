"""
Certify Intel - Autonomous Competitor Discovery Agent
Uses DuckDuckGo search + Playwright scraping + AI qualification to discover new competitors.
"""
import asyncio
import re
import time
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime

# DuckDuckGo Search - Zero Cost
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    print("Warning: duckduckgo-search not installed. Run: pip install duckduckgo-search")

# Playwright for scraping
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: playwright not installed. Run: pip install playwright && playwright install chromium")

# OpenAI for advanced qualification (optional)
try:
    import openai
    OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False


class DiscoveryAgent:
    """
    Autonomous Competitor Discovery Agent using Zero-Cost tools (DuckDuckGo + Heuristics).
    Optional: Use OpenAI GPT for advanced qualification.
    """

    def __init__(self, use_live_search: bool = True, use_openai: bool = False):
        """
        Initialize the Discovery Agent.
        
        Args:
            use_live_search: If True, use real DuckDuckGo search. If False, use seed list.
            use_openai: If True and available, use GPT for advanced qualification.
        """
        self.use_live_search = use_live_search and DDGS_AVAILABLE
        self.use_openai = use_openai and OPENAI_AVAILABLE
        
        # Certify Health DNA Profile
        self.profile = {
            "core_keywords": [
                "patient intake", "digital check-in", "revenue cycle management", 
                "biometric authentication", "patient engagement", "healthcare it",
                "eligibility verification", "patient registration", "medical billing"
            ],
            "required_context": ["healthcare", "medical", "hospital", "practice", "patient", "clinical"],
            "negative_keywords": [
                "top 10", "best", "review", "blog", "news", "article", 
                "job", "career", "salary", "investor", "stock", "press release"
            ],
            "known_competitors": [
                "phreesia", "clearwave", "kareo", "athenahealth", "kyruus",
                "notable", "klara", "mend", "relatient", "modmed"
            ]
        }
        
        # Rate limiting
        self.search_delay = 2.0  # seconds between searches
        self.last_search_time = 0
        
    async def run_discovery_loop(self, max_candidates: int = 10) -> List[Dict[str, Any]]:
        """
        Run the full discovery loop.
        
        Args:
            max_candidates: Maximum number of candidates to return.
            
        Returns:
            List of discovered competitor candidates with scores.
        """
        print("=" * 60)
        print("🔍 CERTIFY SCOUT - Autonomous Discovery Loop")
        print("=" * 60)
        print(f"Mode: {'LIVE SEARCH' if self.use_live_search else 'SEED LIST'}")
        print(f"OpenAI: {'ENABLED' if self.use_openai else 'DISABLED'}")
        print("-" * 60)
        
        candidates = []
        
        # 1. Generate Search Queries - Healthcare IT specific
        queries = [
            "Phreesia competitors patient intake 2025",
            "best patient check-in software healthcare",
            "healthcare revenue cycle management companies",
            "patient engagement platform providers",
            "digital front door healthcare solutions",
            "patient self-scheduling software medical",
            "healthcare eligibility verification companies",
            "patient payment platform healthcare",
            "patient self-service kiosk companies",
            "EHR patient portal software",
            "medical practice management software"
        ]
        
        found_urls = set()
        raw_results = []
        
        # 2. Execute Search
        if self.use_live_search:
            print("📡 Executing LIVE DuckDuckGo searches...")
            raw_results = await self._execute_live_search(queries, found_urls)
        else:
            print("📦 Using SEED LIST (fallback mode)...")
            raw_results = self._get_seed_list(found_urls)
        
        print(f"\n📊 Found {len(raw_results)} unique candidate URLs\n")
        
        # 3. Qualify Candidates (Scrape & Score)
        print("🔬 Qualifying candidates...")
        qualified = 0
        for idx, res in enumerate(raw_results[:max_candidates * 2]):  # Process extra to ensure we get enough
            if qualified >= max_candidates:
                break
                
            print(f"  [{idx+1}/{len(raw_results)}] Analyzing {res['href'][:50]}...")
            
            score, data = await self._qualify_candidate(res['href'])
            
            if score >= 50:  # Qualification threshold
                candidates.append({
                    "name": self._extract_name_from_url(res['href']),
                    "url": res['href'],
                    "title": res.get('title', 'Unknown'),
                    "snippet": res.get('body', ''),
                    "relevance_score": score,
                    "reasoning": data.get("reasoning", "Matched keywords"),
                    "status": "Discovered",
                    "discovered_at": datetime.utcnow().isoformat()
                })
                print(f"    ✅ QUALIFIED ({score}%) - {data.get('reasoning', '')[:50]}")
                qualified += 1
            else:
                reason = data.get("reasoning") or data.get("error", "Low score")
                print(f"    ❌ REJECTED ({score}%) - {reason[:50]}")
        
        print("\n" + "=" * 60)
        print(f"🏆 Discovery Complete: {len(candidates)} qualified candidates")
        print("=" * 60)
        
        return candidates
    
    async def _execute_live_search(self, queries: List[str], found_urls: set) -> List[Dict]:
        """Execute real DuckDuckGo searches with rate limiting."""
        results = []
        
        for query in queries:
            # Rate limiting
            elapsed = time.time() - self.last_search_time
            if elapsed < self.search_delay:
                await asyncio.sleep(self.search_delay - elapsed)
            
            try:
                print(f"  🔎 Searching: '{query}'")
                with DDGS() as ddgs:
                    search_results = list(ddgs.text(query, max_results=5))
                    
                    for r in search_results:
                        url = r.get('href', r.get('link', ''))
                        if url and url not in found_urls and not self._is_ignored(url):
                            found_urls.add(url)
                            results.append({
                                "href": url,
                                "title": r.get('title', ''),
                                "body": r.get('body', r.get('snippet', ''))
                            })
                    
                    print(f"     Found {len(search_results)} results, {len(results)} unique so far")
                    
                self.last_search_time = time.time()
                
            except Exception as e:
                print(f"     ⚠️ Search failed: {e}")
                continue
        
        return results
    
    def _get_seed_list(self, found_urls: set) -> List[Dict]:
        """Return seed list for MVP/fallback mode."""
        seed_candidates = [
            {"href": "https://www.klara.com", "title": "Klara", "body": "Patient communication platform"},
            {"href": "https://www.mend.com", "title": "Mend", "body": "Telehealth and patient engagement"},
            {"href": "https://www.notablehealth.com", "title": "Notable Health", "body": "AI-powered intake automation"},
            {"href": "https://www.qure4u.com", "title": "Qure4u", "body": "Virtual care and patient engagement"},
            {"href": "https://www.yosi.health", "title": "Yosi Health", "body": "Digital patient intake"},
            {"href": "https://www.healow.com", "title": "Healow", "body": "Patient portal and telehealth"},
            {"href": "https://www.solutionreach.com", "title": "Solutionreach", "body": "Patient communication"},
            {"href": "https://www.lumahealth.io", "title": "Luma Health", "body": "Patient access platform"},
        ]
        
        results = []
        for seed in seed_candidates:
            if seed['href'] not in found_urls and not self._is_ignored(seed['href']):
                found_urls.add(seed['href'])
                results.append(seed)
        
        return results

    def _is_ignored(self, url: str) -> bool:
        """Filter out non-company pages (reviews, news, social)."""
        ignored_domains = [
            "g2.com", "capterra.com", "linkedin.com", "facebook.com", 
            "twitter.com", "wikipedia.org", "youtube.com", "indeed.com",
            "glassdoor.com", "softwareadvice.com", "getapp.com", "reddit.com",
            "crunchbase.com", "bloomberg.com", "forbes.com", "techcrunch.com",
            "prnewswire.com", "businesswire.com", "globenewswire.com"
        ]
        url_lower = url.lower()
        for domain in ignored_domains:
            if domain in url_lower:
                return True
        return False

    async def _qualify_candidate(self, url: str) -> Tuple[int, Dict]:
        """Scrape URL and calculate relevance score (0-100)."""
        
        # First try OpenAI qualification if enabled
        if self.use_openai:
            return await self._qualify_with_openai(url)
        
        # Otherwise use heuristic scoring
        return await self._qualify_with_heuristics(url)
    
    async def _qualify_with_heuristics(self, url: str) -> Tuple[int, Dict]:
        """Use Playwright + keyword matching for qualification."""
        if not PLAYWRIGHT_AVAILABLE:
            # Basic URL-based scoring if Playwright not available
            return self._basic_url_score(url)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                try:
                    await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                    text_content = await page.evaluate("document.body.innerText")
                    text_lower = text_content.lower()[:5000]  # Analyze first 5k chars
                    
                    score = 0
                    matches = []
                    
                    # 1. Context Check (Must have healthcare context)
                    if not any(k in text_lower for k in self.profile["required_context"]):
                        await browser.close()
                        return 0, {"reasoning": "Missing healthcare context"}
                    score += 20
                    
                    # 2. Core Keywords (15 points each, up to 60)
                    for kw in self.profile["core_keywords"]:
                        if kw in text_lower:
                            score += 15
                            matches.append(kw)
                            if score >= 80:  # Cap keyword score
                                break
                    
                    # 3. Known competitor mention (10 points)
                    for comp in self.profile["known_competitors"]:
                        if comp in text_lower:
                            score += 10
                            break
                    
                    # 4. Negative Check (punish review/list sites)
                    title = await page.title()
                    title_lower = title.lower()
                    for neg in self.profile["negative_keywords"]:
                        if neg in title_lower or neg in text_lower[:500]:
                            score -= 20
                            break
                    
                    reasoning = f"Matched: {', '.join(matches[:3])}" if matches else "Healthcare context only"
                    await browser.close()
                    return max(0, min(score, 100)), {"reasoning": reasoning}
                    
                except Exception as e:
                    await browser.close()
                    return 0, {"error": str(e)[:50]}
                    
        except Exception as e:
            return 0, {"error": str(e)[:50]}
    
    def _basic_url_score(self, url: str) -> Tuple[int, Dict]:
        """Basic scoring based on URL patterns only."""
        url_lower = url.lower()
        score = 40  # Base score
        
        # Healthcare-related TLD/keywords in URL
        if any(kw in url_lower for kw in ["health", "medical", "patient", "care", "clinic"]):
            score += 20
        
        # .com domains get slight boost
        if ".com" in url_lower:
            score += 10
        
        return score, {"reasoning": "URL pattern matching (no scraping)"}
    
    async def _qualify_with_openai(self, url: str) -> Tuple[int, Dict]:
        """Use GPT to analyze and qualify a competitor."""
        # First scrape the page
        text_content = ""
        if PLAYWRIGHT_AVAILABLE:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                    text_content = await page.evaluate("document.body.innerText")
                    text_content = text_content[:3000]  # Limit tokens
                    await browser.close()
            except Exception:
                pass
        
        if not text_content:
            return 0, {"error": "Could not scrape page"}
        
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a competitive intelligence analyst for Certify Health, 
                        a healthcare IT company focused on patient intake, digital check-in, 
                        and revenue cycle management. Analyze the website content and determine 
                        if this company is a potential competitor."""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze this website content and determine:
1. Is this a healthcare IT company? (yes/no)
2. Does it compete in patient intake, RCM, or patient engagement? (yes/no)
3. Threat score (0-100)
4. Brief reasoning (one sentence)

Website URL: {url}
Content: {text_content}

Respond in JSON format: {{"is_healthcare_it": bool, "is_competitor": bool, "score": int, "reasoning": string}}"""
                    }
                ],
                max_tokens=200
            )
            
            result = response.choices[0].message.content
            import json
            data = json.loads(result)
            
            score = data.get("score", 0)
            if not data.get("is_healthcare_it"):
                score = 0
            
            return score, {"reasoning": data.get("reasoning", "GPT analysis")}
            
        except Exception as e:
            # Fall back to heuristics
            return await self._qualify_with_heuristics(url)

    def _extract_name_from_url(self, url: str) -> str:
        """Extract company name from URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            name = domain.replace("www.", "").split(".")[0]
            return name.title()
        except Exception:
            return "Unknown"


# Entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Certify Scout - Competitor Discovery Agent")
    parser.add_argument("--live", action="store_true", help="Use live DuckDuckGo search")
    parser.add_argument("--openai", action="store_true", help="Use OpenAI for qualification")
    parser.add_argument("--max", type=int, default=10, help="Maximum candidates to return")
    args = parser.parse_args()
    
    agent = DiscoveryAgent(use_live_search=args.live, use_openai=args.openai)
    results = asyncio.run(agent.run_discovery_loop(max_candidates=args.max))
    
    print("\n📋 Final Results:")
    for r in results:
        print(f"  - {r['name']} ({r['relevance_score']}%): {r['url']}")
