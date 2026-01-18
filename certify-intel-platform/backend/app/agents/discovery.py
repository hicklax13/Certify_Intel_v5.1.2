"""
AI-powered competitor discovery agent.
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class DiscoveryAgent:
    """
    AI agent for discovering competitors through multiple signals.
    Uses LLM reasoning to identify and validate potential competitors.
    """
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.bing_api_key = settings.bing_api_key
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_search_taxonomy(self, company_profile: Dict[str, Any]) -> List[str]:
        """
        Generate a taxonomy of search queries to find competitors.
        
        Args:
            company_profile: Dict containing company name, description, products, segments
        
        Returns:
            List of search queries to execute
        """
        prompt = f"""
You are an expert competitive intelligence analyst. Given a company profile, generate comprehensive search queries to find competitors.

COMPANY PROFILE:
Name: {company_profile.get('name', 'Unknown')}
Description: {company_profile.get('description', 'Healthcare technology company')}
Products: {company_profile.get('products', ['patient intake', 'insurance verification', 'revenue cycle'])}
Target Segments: {company_profile.get('segments', ['ambulatory', 'dental', 'specialty practices'])}

Generate 20 diverse search queries that would find:
1. Direct product competitors (same product category)
2. Adjacent market entrants (related healthcare IT)
3. Enterprise alternatives (for larger customers)
4. SMB alternatives (for smaller customers)
5. Regional competitors
6. Emerging startups in the space
7. Companies with overlapping integrations (EHR integrations, etc.)

Return a JSON object with a "queries" array containing strings.
Be specific and varied - don't just add "competitor" to everything.
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("queries", [])
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def validate_competitor(
        self, 
        candidate: Dict[str, Any], 
        company_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate if a candidate company is actually a competitor.
        
        Args:
            candidate: Dict with name, domain, description of potential competitor
            company_profile: Profile of the company we're finding competitors for
        
        Returns:
            Validation result with relevance score and reasoning
        """
        prompt = f"""
You are an expert competitive intelligence analyst. Evaluate if a company is a competitor.

OUR COMPANY:
Name: {company_profile.get('name', 'Certify Health')}
Description: {company_profile.get('description', 'Patient intake, insurance verification, and revenue cycle solutions for healthcare providers')}
Target Segments: {company_profile.get('segments', ['ambulatory', 'dental', 'specialty practices'])}

CANDIDATE COMPANY:
Name: {candidate.get('name', 'Unknown')}
Domain: {candidate.get('domain', 'Unknown')}
Description: {candidate.get('description', 'No description available')}

Evaluate the competitive relevance on a scale of 1-10:
- 9-10: Direct head-to-head competitor (same products, same market)
- 7-8: Significant overlap (similar products or same market)
- 5-6: Adjacent competitor (related products, potential threat)
- 3-4: Peripheral (tangential relationship, watch list)
- 1-2: Not a competitor (different market entirely)

Return a JSON object with:
- relevance_score: number 1-10
- threat_level: "high" | "medium" | "low" | "watch" | "not_competitor"
- is_competitor: boolean (true if score >= 5)
- reasoning: string explaining your assessment
- overlap_areas: array of strings describing competitive overlap
- differentiation: array of strings describing how they differ
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        
        result = json.loads(response.choices[0].message.content)
        result["validated_at"] = datetime.utcnow().isoformat()
        result["validation_model"] = self.model
        
        return result
    
    async def search_bing(self, query: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Search Bing for potential competitors.
        
        Args:
            query: Search query string
            count: Number of results to return
        
        Returns:
            List of search results with name, url, snippet
        """
        import httpx
        
        if not self.bing_api_key:
            return []
        
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
        params = {"q": query, "count": count, "responseFilter": "Webpages"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                web_pages = data.get("webPages", {}).get("value", [])
                for page in web_pages:
                    results.append({
                        "name": page.get("name", ""),
                        "url": page.get("url", ""),
                        "snippet": page.get("snippet", ""),
                        "domain": self._extract_domain(page.get("url", "")),
                    })
                
                return results
        except Exception as e:
            print(f"Bing search error: {e}")
            return []
    
    async def discover_competitors(
        self, 
        company_profile: Dict[str, Any],
        max_candidates: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Full discovery pipeline: generate queries, search, validate.
        
        Args:
            company_profile: Profile of the company to find competitors for
            max_candidates: Maximum candidates to process
        
        Returns:
            List of validated competitors
        """
        # Step 1: Generate search taxonomy
        queries = await self.generate_search_taxonomy(company_profile)
        
        # Step 2: Search across all queries
        all_candidates = []
        seen_domains = set()
        
        for query in queries[:10]:  # Limit to first 10 queries
            results = await self.search_bing(query)
            for result in results:
                domain = result.get("domain", "")
                if domain and domain not in seen_domains:
                    seen_domains.add(domain)
                    all_candidates.append({
                        "name": result.get("name", ""),
                        "domain": domain,
                        "url": result.get("url", ""),
                        "description": result.get("snippet", ""),
                        "discovery_query": query,
                    })
        
        # Step 3: Validate candidates (limit to avoid rate limits)
        validated = []
        for candidate in all_candidates[:max_candidates]:
            validation = await self.validate_competitor(candidate, company_profile)
            if validation.get("is_competitor", False):
                competitor = {
                    **candidate,
                    **validation,
                    "discovered_at": datetime.utcnow().isoformat(),
                    "discovery_method": "ai_discovery",
                }
                validated.append(competitor)
        
        # Sort by relevance score
        validated.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return validated
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www prefix
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return ""
