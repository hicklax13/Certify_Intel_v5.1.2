"""
Web scraper using Playwright for JavaScript-rendered pages.
"""
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class WebScraper:
    """
    Web scraper for collecting evidence from competitor websites.
    Uses Playwright for JavaScript-rendered content.
    """
    
    def __init__(self):
        self.timeout = settings.scrape_timeout_ms
        self.user_agent = settings.scrape_user_agent
        self._browser: Optional[Browser] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        playwright = await async_playwright().start()
        self._browser = await playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._browser:
            await self._browser.close()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def scrape_page(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single webpage.
        
        Args:
            url: URL to scrape
        
        Returns:
            Dict with content, status, metadata
        """
        if not self._browser:
            raise RuntimeError("Scraper not initialized. Use async context manager.")
        
        context = await self._browser.new_context(
            user_agent=self.user_agent,
            viewport={"width": 1920, "height": 1080},
        )
        
        page = await context.new_page()
        
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=self.timeout)
            
            # Wait for dynamic content
            await page.wait_for_load_state("domcontentloaded")
            
            # Get page content
            content_html = await page.content()
            content_text = await page.evaluate("() => document.body.innerText")
            title = await page.title()
            
            # Calculate content hash
            content_hash = hashlib.sha256(content_text.encode()).hexdigest()
            
            # Extract metadata
            metadata = await self._extract_metadata(page)
            
            return {
                "url": url,
                "title": title,
                "content_text": content_text,
                "content_html": content_html,
                "content_hash": content_hash,
                "http_status": response.status if response else 0,
                "metadata": metadata,
                "fetched_at": datetime.utcnow().isoformat(),
                "success": True,
            }
        
        except Exception as e:
            return {
                "url": url,
                "title": None,
                "content_text": None,
                "content_html": None,
                "content_hash": None,
                "http_status": 0,
                "metadata": {"error": str(e)},
                "fetched_at": datetime.utcnow().isoformat(),
                "success": False,
                "error": str(e),
            }
        
        finally:
            await context.close()
    
    async def scrape_pricing_page(self, base_url: str) -> Dict[str, Any]:
        """
        Attempt to find and scrape the pricing page.
        
        Args:
            base_url: Company's base URL
        
        Returns:
            Scraped pricing page or indication that it wasn't found
        """
        # Common pricing page patterns
        pricing_paths = [
            "/pricing",
            "/plans",
            "/price",
            "/pricing-plans",
            "/plans-pricing",
            "/products/pricing",
            "/pricing.html",
        ]
        
        for path in pricing_paths:
            url = base_url.rstrip("/") + path
            result = await self.scrape_page(url)
            
            if result["success"] and result["http_status"] == 200:
                # Verify it's actually a pricing page
                content = result.get("content_text", "").lower()
                pricing_indicators = ["per month", "per user", "pricing", "free trial", "enterprise", "contact sales"]
                
                if any(indicator in content for indicator in pricing_indicators):
                    result["page_type"] = "pricing"
                    return result
        
        # Pricing page not found
        return {
            "url": base_url,
            "success": False,
            "error": "Pricing page not found",
            "attempted_paths": pricing_paths,
        }
    
    async def scrape_multiple_pages(self, base_url: str) -> Dict[str, Dict[str, Any]]:
        """
        Scrape multiple pages from a competitor site.
        
        Args:
            base_url: Company's base URL
        
        Returns:
            Dict mapping page type to scraped content
        """
        pages = {
            "homepage": base_url,
            "about": base_url.rstrip("/") + "/about",
            "product": base_url.rstrip("/") + "/product",
            "features": base_url.rstrip("/") + "/features",
            "integrations": base_url.rstrip("/") + "/integrations",
        }
        
        results = {}
        for page_type, url in pages.items():
            result = await self.scrape_page(url)
            if result["success"]:
                result["page_type"] = page_type
                results[page_type] = result
        
        # Also try to get pricing
        pricing = await self.scrape_pricing_page(base_url)
        if pricing.get("success"):
            results["pricing"] = pricing
        
        return results
    
    async def _extract_metadata(self, page: Page) -> Dict[str, Any]:
        """Extract metadata from page."""
        metadata = {}
        
        try:
            # Meta description
            meta_desc = await page.query_selector('meta[name="description"]')
            if meta_desc:
                metadata["description"] = await meta_desc.get_attribute("content")
            
            # Open Graph data
            og_title = await page.query_selector('meta[property="og:title"]')
            if og_title:
                metadata["og_title"] = await og_title.get_attribute("content")
            
            og_desc = await page.query_selector('meta[property="og:description"]')
            if og_desc:
                metadata["og_description"] = await og_desc.get_attribute("content")
            
            # Count links
            links = await page.query_selector_all("a[href]")
            metadata["link_count"] = len(links)
            
            # Count images
            images = await page.query_selector_all("img")
            metadata["image_count"] = len(images)
            
        except Exception:
            pass
        
        return metadata


async def scrape_competitor_site(domain: str) -> Dict[str, Any]:
    """
    Convenience function to scrape a competitor site.
    
    Args:
        domain: Competitor's domain (e.g., "example.com")
    
    Returns:
        Scraped content from multiple pages
    """
    base_url = f"https://{domain}"
    
    async with WebScraper() as scraper:
        return await scraper.scrape_multiple_pages(base_url)
