"""
Certify Intel - Web Scraper
Uses Playwright to scrape competitor websites and extract content.
"""
import asyncio
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Run: pip install playwright && playwright install chromium")


@dataclass
class ScrapedPage:
    url: str
    title: str
    content: str
    html: str
    scraped_at: datetime
    page_type: str  # homepage, pricing, about, features, etc.


@dataclass
class ScrapeResult:
    competitor_name: str
    website: str
    pages: List[ScrapedPage]
    success: bool
    error: Optional[str] = None


class CompetitorScraper:
    """Scrapes competitor websites to extract content for AI analysis."""
    
    def __init__(self, headless: bool = True, timeout_ms: int = 30000):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def scrape_competitor(self, name: str, website: str, pages_to_scrape: List[str] = None) -> ScrapeResult:
        """Scrape a competitor's website."""
        if pages_to_scrape is None:
            pages_to_scrape = ["homepage", "pricing", "about", "features"]
        
        if not self.browser:
            return ScrapeResult(
                competitor_name=name,
                website=website,
                pages=[],
                success=False,
                error="Browser not initialized"
            )
        
        scraped_pages = []
        
        try:
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            # Scrape each requested page type
            for page_type in pages_to_scrape:
                url = self._get_page_url(website, page_type)
                if url:
                    scraped = await self._scrape_page(page, url, page_type)
                    if scraped:
                        scraped_pages.append(scraped)
            
            await context.close()
            
            return ScrapeResult(
                competitor_name=name,
                website=website,
                pages=scraped_pages,
                success=len(scraped_pages) > 0
            )
            
        except Exception as e:
            return ScrapeResult(
                competitor_name=name,
                website=website,
                pages=scraped_pages,
                success=False,
                error=str(e)
            )
    
    async def scrape(self, url: str) -> dict:
        """Simple scrape method for compatibility with main.py calls.
        Returns dict with extracted content from the website."""
        try:
            if not self.browser:
                return {"error": "Browser not initialized"}
            
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            # Navigate to the URL
            if not url.startswith("http"):
                url = f"https://{url}"
            
            response = await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
            
            if not response or response.status >= 400:
                await context.close()
                return {"error": f"HTTP {response.status if response else 'No response'}"}
            
            await page.wait_for_timeout(2000)
            
            # Extract text content
            content = await page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script, style, noscript');
                    scripts.forEach(s => s.remove());
                    return document.body.innerText || '';
                }
            """)
            
            title = await page.title()
            await context.close()
            
            return {
                "content": content,
                "title": title,
                "url": url,
                "success": True
            }
        except Exception as e:
            return {"error": str(e)}

    
    def _get_page_url(self, website: str, page_type: str) -> Optional[str]:
        """Get the URL for a specific page type."""
        # Ensure website has protocol
        if not website.startswith("http"):
            website = f"https://{website}"
        
        # Common URL patterns for each page type
        patterns = {
            "homepage": "",
            "pricing": ["pricing", "plans", "price", "cost"],
            "about": ["about", "about-us", "company", "who-we-are"],
            "features": ["features", "product", "solutions", "platform"],
            "customers": ["customers", "case-studies", "clients", "success-stories"],
            "integrations": ["integrations", "partners", "marketplace", "apps"],
            "contact": ["contact", "contact-us", "get-in-touch"],
            "blog": ["blog", "news", "resources", "insights"],
        }
        
        if page_type == "homepage":
            return website
        
        if page_type in patterns:
            # Return first common pattern - actual page discovery would need more logic
            paths = patterns[page_type]
            if isinstance(paths, list) and paths:
                return urljoin(website + "/", paths[0])
        
        return None
    
    async def _scrape_page(self, page: Page, url: str, page_type: str) -> Optional[ScrapedPage]:
        """Scrape a single page."""
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
            
            if not response or response.status >= 400:
                return None
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
            # Get page title
            title = await page.title()
            
            # Get page content (text only)
            content = await page.evaluate("""
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style, noscript');
                    scripts.forEach(s => s.remove());
                    
                    // Get text content
                    return document.body.innerText || '';
                }
            """)
            
            # Get HTML for more detailed extraction
            html = await page.content()
            
            return ScrapedPage(
                url=url,
                title=title,
                content=content,
                html=html,
                scraped_at=datetime.utcnow(),
                page_type=page_type
            )
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    async def discover_pricing_page(self, page: Page, website: str) -> Optional[str]:
        """Try to discover the pricing page URL."""
        if not website.startswith("http"):
            website = f"https://{website}"
            
        try:
            await page.goto(website, wait_until="domcontentloaded", timeout=self.timeout_ms)
            
            # Look for pricing links
            pricing_link = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a'));
                    const pricingPatterns = ['pricing', 'price', 'plans', 'cost', 'packages'];
                    
                    for (const link of links) {
                        const href = link.getAttribute('href') || '';
                        const text = link.textContent?.toLowerCase() || '';
                        
                        for (const pattern of pricingPatterns) {
                            if (href.includes(pattern) || text.includes(pattern)) {
                                return link.href;
                            }
                        }
                    }
                    return null;
                }
            """)
            
            return pricing_link
            
        except Exception as e:
            print(f"Error discovering pricing page: {e}")
            return None


# Standalone scrape function for simple usage
async def scrape_competitor(name: str, website: str, pages: List[str] = None) -> ScrapeResult:
    """Convenience function to scrape a single competitor."""
    async with CompetitorScraper() as scraper:
        return await scraper.scrape_competitor(name, website, pages)


# Test function
async def test_scraper():
    """Test the scraper with a sample website."""
    print("Testing scraper...")
    async with CompetitorScraper(headless=True) as scraper:
        result = await scraper.scrape_competitor(
            name="Phreesia",
            website="https://www.phreesia.com",
            pages_to_scrape=["homepage", "pricing"]
        )
        
        print(f"Scraped {result.competitor_name}: {result.success}")
        for page in result.pages:
            print(f"  - {page.page_type}: {page.title} ({len(page.content)} chars)")
        
        if result.error:
            print(f"  Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(test_scraper())
