"""
Certify Intel - Real-Time News Monitor
Fetches and analyzes competitor news from multiple sources.
"""
import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


@dataclass
class NewsArticle:
    """Represents a news article."""
    title: str
    url: str
    source: str
    published_date: str
    snippet: str
    sentiment: str  # positive, negative, neutral
    is_major_event: bool
    event_type: Optional[str]  # funding, acquisition, product_launch, partnership


@dataclass
class NewsDigest:
    """Collection of news articles with analysis."""
    company_name: str
    articles: List[NewsArticle]
    total_count: int
    sentiment_breakdown: Dict[str, int]
    major_events: List[NewsArticle]
    fetched_at: str


class NewsMonitor:
    """Multi-source news monitoring for competitors."""
    
    # Keywords indicating major events
    EVENT_KEYWORDS = {
        "funding": ["raises", "funding", "series", "investment", "million", "billion", "capital"],
        "acquisition": ["acquires", "acquisition", "acquired", "merger", "buys", "purchased"],
        "product_launch": ["launches", "announces", "introduces", "unveils", "new product", "release"],
        "partnership": ["partners", "partnership", "collaboration", "integrates", "alliance"],
        "leadership": ["ceo", "cto", "appoints", "hires", "joins", "executive"],
        "expansion": ["expands", "opens", "enters", "growth", "expansion"]
    }
    
    # Sentiment keywords
    POSITIVE_KEYWORDS = ["growth", "success", "award", "wins", "leading", "innovative", "raises", "expands"]
    NEGATIVE_KEYWORDS = ["layoffs", "lawsuit", "breach", "decline", "struggles", "loses", "cuts", "failed"]
    
    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.bing_news_key = os.getenv("BING_NEWS_KEY")
    
    def fetch_news(self, company_name: str, days: int = 7) -> NewsDigest:
        """
        Fetch news for a company from all available sources.
        
        Args:
            company_name: Name of the company
            days: Number of days to look back
            
        Returns:
            NewsDigest with articles and analysis
        """
        articles = []
        
        # Try Google News RSS (free, no API key needed)
        google_articles = self._fetch_google_news(company_name)
        articles.extend(google_articles)
        
        # Try NewsAPI if key available
        if self.newsapi_key:
            newsapi_articles = self._fetch_newsapi(company_name, days)
            articles.extend(newsapi_articles)
        
        # Try Bing News if key available
        if self.bing_news_key:
            bing_articles = self._fetch_bing_news(company_name)
            articles.extend(bing_articles)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        # Analyze articles
        for article in unique_articles:
            article.sentiment = self._analyze_sentiment(article.title + " " + article.snippet)
            article.event_type = self._detect_event_type(article.title + " " + article.snippet)
            article.is_major_event = article.event_type is not None
        
        # Build digest
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for article in unique_articles:
            sentiment_counts[article.sentiment] += 1
        
        major_events = [a for a in unique_articles if a.is_major_event]
        
        return NewsDigest(
            company_name=company_name,
            articles=unique_articles[:20],  # Limit to 20
            total_count=len(unique_articles),
            sentiment_breakdown=sentiment_counts,
            major_events=major_events[:5],
            fetched_at=datetime.utcnow().isoformat()
        )
    
    def _fetch_google_news(self, company_name: str) -> List[NewsArticle]:
        """Fetch news from Google News RSS."""
        articles = []
        
        try:
            # Healthcare-specific search
            query = urllib.parse.quote(f"{company_name} healthcare")
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                content = response.read()
            
            root = ET.fromstring(content)
            
            for item in root.findall(".//item")[:10]:
                title = item.find("title")
                link = item.find("link")
                pub_date = item.find("pubDate")
                source = item.find("source")
                
                if title is not None and link is not None:
                    # Extract source from title (Google News format: "Title - Source")
                    title_text = title.text or ""
                    source_name = source.text if source is not None else "Google News"
                    
                    if " - " in title_text:
                        parts = title_text.rsplit(" - ", 1)
                        title_text = parts[0]
                        if len(parts) > 1:
                            source_name = parts[1]
                    
                    articles.append(NewsArticle(
                        title=title_text,
                        url=link.text or "",
                        source=source_name,
                        published_date=pub_date.text if pub_date is not None else "",
                        snippet="",
                        sentiment="neutral",
                        is_major_event=False,
                        event_type=None
                    ))
                    
        except Exception as e:
            print(f"Google News fetch failed: {e}")
        
        return articles
    
    def _fetch_newsapi(self, company_name: str, days: int) -> List[NewsArticle]:
        """Fetch news from NewsAPI.org."""
        articles = []
        
        if not self.newsapi_key:
            return articles
        
        try:
            from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
            query = urllib.parse.quote(f'"{company_name}" healthcare')
            url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&sortBy=publishedAt&apiKey={self.newsapi_key}"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read())
            
            for item in data.get("articles", [])[:10]:
                articles.append(NewsArticle(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    source=item.get("source", {}).get("name", "NewsAPI"),
                    published_date=item.get("publishedAt", ""),
                    snippet=item.get("description", ""),
                    sentiment="neutral",
                    is_major_event=False,
                    event_type=None
                ))
                
        except Exception as e:
            print(f"NewsAPI fetch failed: {e}")
        
        return articles
    
    def _fetch_bing_news(self, company_name: str) -> List[NewsArticle]:
        """Fetch news from Bing News API."""
        articles = []
        
        if not self.bing_news_key:
            return articles
        
        try:
            query = urllib.parse.quote(f"{company_name} healthcare")
            url = f"https://api.bing.microsoft.com/v7.0/news/search?q={query}&count=10"
            
            req = urllib.request.Request(url)
            req.add_header("Ocp-Apim-Subscription-Key", self.bing_news_key)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read())
            
            for item in data.get("value", []):
                articles.append(NewsArticle(
                    title=item.get("name", ""),
                    url=item.get("url", ""),
                    source=item.get("provider", [{}])[0].get("name", "Bing News"),
                    published_date=item.get("datePublished", ""),
                    snippet=item.get("description", ""),
                    sentiment="neutral",
                    is_major_event=False,
                    event_type=None
                ))
                
        except Exception as e:
            print(f"Bing News fetch failed: {e}")
        
        return articles
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple keyword-based sentiment analysis."""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _detect_event_type(self, text: str) -> Optional[str]:
        """Detect if text indicates a major event."""
        text_lower = text.lower()
        
        for event_type, keywords in self.EVENT_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return event_type
        
        return None
    
    def get_news_summary(self, company_name: str) -> Dict[str, Any]:
        """Get a summary of news for a company."""
        digest = self.fetch_news(company_name)
        
        return {
            "company": company_name,
            "total_articles": digest.total_count,
            "sentiment": digest.sentiment_breakdown,
            "major_events": [
                {
                    "type": a.event_type,
                    "title": a.title,
                    "url": a.url,
                    "date": a.published_date
                }
                for a in digest.major_events
            ],
            "recent_headlines": [a.title for a in digest.articles[:5]],
            "fetched_at": digest.fetched_at
        }


# API convenience functions
def fetch_competitor_news(company_name: str, days: int = 7) -> Dict[str, Any]:
    """Fetch news for a competitor."""
    monitor = NewsMonitor()
    digest = monitor.fetch_news(company_name, days)
    
    return {
        "company": digest.company_name,
        "articles": [asdict(a) for a in digest.articles],
        "total_count": digest.total_count,
        "sentiment_breakdown": digest.sentiment_breakdown,
        "major_events": [asdict(a) for a in digest.major_events],
        "fetched_at": digest.fetched_at
    }


def check_for_alerts(company_name: str) -> List[Dict[str, Any]]:
    """Check for news that should trigger alerts."""
    monitor = NewsMonitor()
    digest = monitor.fetch_news(company_name, days=1)
    
    alerts = []
    for event in digest.major_events:
        alert_level = "High" if event.event_type in ["funding", "acquisition"] else "Medium"
        alerts.append({
            "company": company_name,
            "event_type": event.event_type,
            "title": event.title,
            "url": event.url,
            "alert_level": alert_level,
            "detected_at": datetime.utcnow().isoformat()
        })
    
    return alerts


if __name__ == "__main__":
    # Test with sample company
    print("Testing News Monitor...")
    result = fetch_competitor_news("Phreesia")
    print(json.dumps(result, indent=2, default=str))
