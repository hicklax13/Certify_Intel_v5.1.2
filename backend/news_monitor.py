"""
Certify Intel - Real-Time News Monitor (v5.0.7)
Fetches and analyzes competitor news from multiple sources.

v5.0.3: Added SEC EDGAR and USPTO patent integration for government data sources.
v5.0.4: Added GNews, MediaStack, and NewsData.io API integrations (Phase 3).
v5.0.5: Added Hugging Face ML sentiment analysis (Phase 4).
v5.0.7: Added dimension tagging integration for Sales & Marketing module.
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

# Import government data scrapers (v5.0.3)
try:
    from sec_edgar_scraper import SECEdgarScraper, get_sec_news
    SEC_AVAILABLE = True
except ImportError:
    SEC_AVAILABLE = False
    print("SEC EDGAR scraper not available")

try:
    from uspto_scraper import USPTOScraper
    USPTO_AVAILABLE = True
except ImportError:
    USPTO_AVAILABLE = False
    print("USPTO patent scraper not available")

# Enhanced Google News library (v5.0.3)
try:
    from pygooglenews import GoogleNews
    PYGOOGLENEWS_AVAILABLE = True
except ImportError:
    PYGOOGLENEWS_AVAILABLE = False
    print("pygooglenews not available, using raw RSS")

# ML-powered sentiment analysis (v5.0.5)
try:
    from ml_sentiment import get_headline_analyzer, NewsHeadlineSentimentAnalyzer
    ML_SENTIMENT_AVAILABLE = True
except ImportError:
    ML_SENTIMENT_AVAILABLE = False
    print("ML sentiment not available, using keyword-based")

# Dimension tagging for Sales & Marketing module (v5.0.7)
try:
    from dimension_analyzer import DimensionAnalyzer
    DIMENSION_ANALYZER_AVAILABLE = True
except ImportError:
    DIMENSION_ANALYZER_AVAILABLE = False
    print("Dimension analyzer not available")


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
    dimension_tags: Optional[List[Dict[str, Any]]] = None  # v5.0.7: dimension classifications


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
    
    def __init__(
        self,
        include_sec: bool = True,
        include_patents: bool = True,
        use_pygooglenews: bool = True,
        use_ml_sentiment: bool = True,
        tag_dimensions: bool = True
    ):
        """
        Initialize NewsMonitor.

        Args:
            include_sec: Include SEC EDGAR filings as news (v5.0.3)
            include_patents: Include USPTO patents as news (v5.0.3)
            use_pygooglenews: Use enhanced pygooglenews library (v5.0.3)
            use_ml_sentiment: Use ML-based sentiment analysis (v5.0.5)
            tag_dimensions: Tag articles with competitive dimensions (v5.0.7)
        """
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.bing_news_key = os.getenv("BING_NEWS_KEY")

        # v5.0.4: Free news API keys (Phase 3)
        self.gnews_api_key = os.getenv("GNEWS_API_KEY")
        self.mediastack_api_key = os.getenv("MEDIASTACK_API_KEY")
        self.newsdata_api_key = os.getenv("NEWSDATA_API_KEY")

        # v5.0.3: Government data sources
        self.include_sec = include_sec and SEC_AVAILABLE
        self.include_patents = include_patents and USPTO_AVAILABLE

        # v5.0.3: Enhanced Google News with pygooglenews
        self.use_pygooglenews = use_pygooglenews and PYGOOGLENEWS_AVAILABLE
        self.google_news_client = GoogleNews(lang='en', country='US') if self.use_pygooglenews else None

        # v5.0.5: ML-powered sentiment analysis
        self.use_ml_sentiment = use_ml_sentiment and ML_SENTIMENT_AVAILABLE
        self.ml_sentiment_analyzer = get_headline_analyzer() if self.use_ml_sentiment else None

        # v5.0.7: Dimension tagging for Sales & Marketing module
        self.tag_dimensions = tag_dimensions and DIMENSION_ANALYZER_AVAILABLE
        self.dimension_analyzer = DimensionAnalyzer() if self.tag_dimensions else None

        # Initialize scrapers if available
        self.sec_scraper = SECEdgarScraper() if self.include_sec else None
        self.patent_scraper = USPTOScraper() if self.include_patents else None
    
    def fetch_news(self, company_name: str, days: int = 90) -> NewsDigest:
        """
        Fetch news for a company from all available sources.

        Args:
            company_name: Name of the company
            days: Number of days to look back (default: 90 days / 3 months)

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

        # v5.0.3: SEC EDGAR filings (free, no API key needed)
        if self.include_sec:
            sec_articles = self._fetch_sec_filings(company_name, days)
            articles.extend(sec_articles)

        # v5.0.3: USPTO patent news (free, no API key needed)
        if self.include_patents:
            patent_articles = self._fetch_patent_news(company_name)
            articles.extend(patent_articles)

        # v5.0.4: GNews API (100 req/day free)
        if self.gnews_api_key:
            gnews_articles = self._fetch_gnews(company_name)
            articles.extend(gnews_articles)

        # v5.0.4: MediaStack API (500 req/month free)
        if self.mediastack_api_key:
            mediastack_articles = self._fetch_mediastack(company_name)
            articles.extend(mediastack_articles)

        # v5.0.4: NewsData.io API (200 req/day free, tech/healthcare specialty)
        if self.newsdata_api_key:
            newsdata_articles = self._fetch_newsdata(company_name)
            articles.extend(newsdata_articles)

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        # Analyze articles (skip for gov sources which already have sentiment/event)
        # v5.0.5: Use batch processing for ML sentiment when available
        self._analyze_sentiment_batch(unique_articles)

        # Detect event types for articles that don't have them
        for article in unique_articles:
            if article.event_type is None:
                article.event_type = self._detect_event_type(article.title + " " + article.snippet)
            article.is_major_event = article.event_type is not None

        # v5.0.7: Tag articles with competitive dimensions
        if self.tag_dimensions:
            self._tag_dimensions_batch(unique_articles, company_name)

        # Build digest
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for article in unique_articles:
            sentiment_counts[article.sentiment] += 1

        major_events = [a for a in unique_articles if a.is_major_event]

        return NewsDigest(
            company_name=company_name,
            articles=unique_articles,  # Include ALL articles
            total_count=len(unique_articles),
            sentiment_breakdown=sentiment_counts,
            major_events=major_events,  # Include ALL major events
            fetched_at=datetime.utcnow().isoformat()
        )
    
    def _fetch_google_news(self, company_name: str) -> List[NewsArticle]:
        """
        Fetch news from Google News.

        v5.0.3: Uses pygooglenews library when available for enhanced features.
        Falls back to raw RSS parsing if pygooglenews not installed.
        """
        # Try enhanced pygooglenews first (v5.0.3)
        if self.use_pygooglenews and self.google_news_client:
            return self._fetch_google_news_enhanced(company_name)

        # Fallback to raw RSS parsing
        return self._fetch_google_news_rss(company_name)

    def _fetch_google_news_enhanced(self, company_name: str) -> List[NewsArticle]:
        """
        Fetch news using pygooglenews library.

        v5.0.3: Enhanced Google News with better date filtering, geo targeting, and parsing.
        """
        articles = []

        try:
            # Search for company news
            search_result = self.google_news_client.search(f'"{company_name}"')

            if search_result and 'entries' in search_result:
                for entry in search_result['entries']:
                    title_text = entry.get('title', '')
                    source_name = entry.get('source', {}).get('title', 'Google News')

                    # pygooglenews provides cleaner title without source suffix
                    articles.append(NewsArticle(
                        title=title_text,
                        url=entry.get('link', ''),
                        source=source_name,
                        published_date=entry.get('published', ''),
                        snippet=entry.get('summary', ''),
                        sentiment="neutral",
                        is_major_event=False,
                        event_type=None
                    ))

        except Exception as e:
            print(f"pygooglenews fetch failed: {e}, falling back to RSS")
            # Fallback to RSS if pygooglenews fails
            return self._fetch_google_news_rss(company_name)

        return articles

    def _fetch_google_news_rss(self, company_name: str) -> List[NewsArticle]:
        """Fetch news from Google News RSS (fallback method)."""
        articles = []

        try:
            # Search by company name only (most general)
            query = urllib.parse.quote(f'"{company_name}"')
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

            with urllib.request.urlopen(url, timeout=15) as response:
                content = response.read()

            root = ET.fromstring(content)

            # Get ALL matching articles (no limit)
            for item in root.findall(".//item"):
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
            print(f"Google News RSS fetch failed: {e}")

        return articles
    
    def _fetch_newsapi(self, company_name: str, days: int) -> List[NewsArticle]:
        """Fetch news from NewsAPI.org."""
        articles = []
        
        if not self.newsapi_key:
            return articles
        
        try:
            from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
            # Search by company name only (most general)
            query = urllib.parse.quote(f'"{company_name}"')
            url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&sortBy=publishedAt&pageSize=100&apiKey={self.newsapi_key}"
            
            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read())
            
            # Get ALL matching articles (up to 100 per source)
            for item in data.get("articles", []):
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
            # Search by company name only (most general)
            query = urllib.parse.quote(f'"{company_name}"')
            url = f"https://api.bing.microsoft.com/v7.0/news/search?q={query}&count=100"
            
            req = urllib.request.Request(url)
            req.add_header("Ocp-Apim-Subscription-Key", self.bing_news_key)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read())
            
            # Get ALL matching articles
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

    # ============== Government Data Sources (v5.0.3) ==============

    def _fetch_sec_filings(self, company_name: str, days: int = 90) -> List[NewsArticle]:
        """
        Fetch SEC EDGAR filings as news articles.

        v5.0.3: Government data source - free, no API key needed.
        """
        articles = []

        if not self.sec_scraper:
            return articles

        try:
            # Get SEC filings formatted as news articles
            sec_articles = self.sec_scraper.get_news_articles(company_name, days_back=days)

            for item in sec_articles:
                articles.append(NewsArticle(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    source="SEC EDGAR",
                    published_date=item.get("published_at", ""),
                    snippet=item.get("snippet", ""),
                    sentiment=item.get("sentiment", "neutral"),
                    is_major_event=item.get("is_major_event", False),
                    event_type=item.get("event_type")
                ))

        except Exception as e:
            print(f"SEC EDGAR fetch failed: {e}")

        return articles

    def _fetch_patent_news(self, company_name: str) -> List[NewsArticle]:
        """
        Fetch USPTO patent filings as news articles.

        v5.0.3: Government data source - free, no API key needed.
        """
        articles = []

        if not self.patent_scraper:
            return articles

        try:
            # Get patent data
            patent_data = self.patent_scraper.get_patent_data(company_name)

            # Convert recent patent filings to news articles
            for patent in patent_data.recent_filings[:5]:  # Limit to recent 5
                title = f"{company_name} Files Patent: {patent.title}"
                snippet = f"Patent #{patent.patent_number} - {patent.technology_area}"

                articles.append(NewsArticle(
                    title=title,
                    url=patent.url,
                    source="USPTO Patents",
                    published_date=patent.filing_date,
                    snippet=snippet,
                    sentiment="positive",  # Patents are generally positive news
                    is_major_event=True,
                    event_type="product_launch"  # Patents often indicate new products/features
                ))

            # Also include recently granted patents
            granted = [p for p in patent_data.patents if p.status == "Granted"][:3]
            for patent in granted:
                title = f"{company_name} Granted Patent: {patent.title}"
                snippet = f"Patent #{patent.patent_number} granted - {patent.technology_area}"

                articles.append(NewsArticle(
                    title=title,
                    url=patent.url,
                    source="USPTO Patents",
                    published_date=patent.grant_date,
                    snippet=snippet,
                    sentiment="positive",
                    is_major_event=True,
                    event_type="product_launch"
                ))

        except Exception as e:
            print(f"USPTO patent fetch failed: {e}")

        return articles

    # ============== Free News APIs (v5.0.4 - Phase 3) ==============

    def _fetch_gnews(self, company_name: str) -> List[NewsArticle]:
        """
        Fetch news from GNews API.

        v5.0.4: 100 requests/day free tier.
        API docs: https://gnews.io/docs/v4

        Features:
        - 60,000+ sources
        - Historical to 6 years
        - Fast response times
        - Good for breaking news
        """
        articles = []

        if not self.gnews_api_key:
            return articles

        try:
            # GNews API endpoint
            query = urllib.parse.quote(f'"{company_name}"')
            url = f"https://gnews.io/api/v4/search?q={query}&lang=en&country=us&max=50&apikey={self.gnews_api_key}"

            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read())

            for item in data.get("articles", []):
                articles.append(NewsArticle(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    source=item.get("source", {}).get("name", "GNews"),
                    published_date=item.get("publishedAt", ""),
                    snippet=item.get("description", ""),
                    sentiment="neutral",
                    is_major_event=False,
                    event_type=None
                ))

        except Exception as e:
            print(f"GNews API fetch failed: {e}")

        return articles

    def _fetch_mediastack(self, company_name: str) -> List[NewsArticle]:
        """
        Fetch news from MediaStack API.

        v5.0.4: 500 requests/month free tier.
        API docs: https://mediastack.com/documentation

        Features:
        - 7,500+ sources in 50 countries
        - 13 languages supported
        - Broad international coverage
        - Good for global competitor monitoring
        """
        articles = []

        if not self.mediastack_api_key:
            return articles

        try:
            # MediaStack API endpoint (note: free tier uses HTTP, not HTTPS)
            query = urllib.parse.quote(company_name)
            url = f"http://api.mediastack.com/v1/news?access_key={self.mediastack_api_key}&keywords={query}&languages=en&limit=50"

            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read())

            for item in data.get("data", []):
                articles.append(NewsArticle(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    source=item.get("source", "MediaStack"),
                    published_date=item.get("published_at", ""),
                    snippet=item.get("description", ""),
                    sentiment="neutral",
                    is_major_event=False,
                    event_type=None
                ))

        except Exception as e:
            print(f"MediaStack API fetch failed: {e}")

        return articles

    def _fetch_newsdata(self, company_name: str) -> List[NewsArticle]:
        """
        Fetch news from NewsData.io API.

        v5.0.4: 200 requests/day free tier.
        API docs: https://newsdata.io/docs

        Features:
        - 89 languages supported
        - Crypto/tech/healthcare news specialty
        - 1M+ articles indexed weekly
        - Best for tech/healthcare news categorization
        """
        articles = []

        if not self.newsdata_api_key:
            return articles

        try:
            # NewsData.io API endpoint
            query = urllib.parse.quote(company_name)
            # Use health and technology category filters for better relevance
            url = f"https://newsdata.io/api/1/news?apikey={self.newsdata_api_key}&q={query}&language=en"

            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read())

            for item in data.get("results", []):
                # NewsData.io provides category which we can use for event detection
                categories = item.get("category", [])
                event_type = None
                if "technology" in categories:
                    event_type = "product_launch"
                elif "business" in categories:
                    event_type = "financial"
                elif "health" in categories:
                    event_type = "expansion"

                articles.append(NewsArticle(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    source=item.get("source_id", "NewsData.io"),
                    published_date=item.get("pubDate", ""),
                    snippet=item.get("description", "") or item.get("content", "")[:200] if item.get("content") else "",
                    sentiment="neutral",
                    is_major_event=event_type is not None,
                    event_type=event_type
                ))

        except Exception as e:
            print(f"NewsData.io API fetch failed: {e}")

        return articles

    def _analyze_sentiment(self, text: str, snippet: str = "") -> str:
        """
        Analyze sentiment of text.

        v5.0.5: Uses ML-based sentiment when available, falls back to keywords.

        Args:
            text: Main text (usually headline)
            snippet: Optional snippet for additional context

        Returns:
            Sentiment label (positive, negative, neutral)
        """
        # Use ML sentiment if available (v5.0.5)
        if self.use_ml_sentiment and self.ml_sentiment_analyzer:
            try:
                result = self.ml_sentiment_analyzer.analyze_headline(text, snippet)
                return result.label
            except Exception as e:
                print(f"ML sentiment failed, using keywords: {e}")

        # Fallback to keyword-based
        return self._keyword_sentiment(text)

    def _keyword_sentiment(self, text: str) -> str:
        """Keyword-based sentiment analysis fallback."""
        text_lower = text.lower()

        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _analyze_sentiment_batch(self, articles: List[NewsArticle]) -> None:
        """
        Analyze sentiment for multiple articles efficiently.

        v5.0.5: Batch ML sentiment processing for better performance.

        Args:
            articles: List of NewsArticle objects to analyze (modified in place)
        """
        if not articles:
            return

        # Filter articles that need sentiment analysis
        needs_analysis = [
            a for a in articles
            if a.sentiment == "neutral" and a.source not in ["SEC EDGAR", "USPTO Patents"]
        ]

        if not needs_analysis:
            return

        # Use ML batch processing if available
        if self.use_ml_sentiment and self.ml_sentiment_analyzer:
            try:
                headlines = [(a.title, a.snippet) for a in needs_analysis]
                results = self.ml_sentiment_analyzer.analyze_headlines_batch(headlines)

                for article, result in zip(needs_analysis, results):
                    article.sentiment = result.label

                return
            except Exception as e:
                print(f"ML batch sentiment failed, using keywords: {e}")

        # Fallback to keyword-based
        for article in needs_analysis:
            article.sentiment = self._keyword_sentiment(article.title + " " + article.snippet)
    
    def _detect_event_type(self, text: str) -> Optional[str]:
        """Detect if text indicates a major event."""
        text_lower = text.lower()

        for event_type, keywords in self.EVENT_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return event_type

        return None

    def _tag_dimensions_batch(self, articles: List[NewsArticle], company_name: str) -> None:
        """
        Tag articles with competitive dimensions.

        v5.0.7: Uses DimensionAnalyzer to classify articles by dimension.

        Args:
            articles: List of NewsArticle objects to tag (modified in place)
            company_name: Name of the competitor
        """
        if not self.dimension_analyzer:
            return

        for article in articles:
            try:
                # Classify which dimensions this article relates to
                dimension_matches = self.dimension_analyzer.classify_article_dimension(
                    title=article.title,
                    snippet=article.snippet,
                    competitor_name=company_name
                )

                # Convert to list of dicts with dimension info
                if dimension_matches:
                    article.dimension_tags = [
                        {
                            "dimension_id": dim_id,
                            "confidence": confidence,
                            "sentiment": article.sentiment
                        }
                        for dim_id, confidence in dimension_matches
                    ]
                else:
                    article.dimension_tags = []

            except Exception as e:
                print(f"Dimension tagging failed for article: {e}")
                article.dimension_tags = []

    def store_dimension_tags(
        self,
        articles: List[NewsArticle],
        competitor_id: int,
        db_session
    ) -> int:
        """
        Store dimension tags for articles in the database.

        v5.0.7: Persists dimension tags to DimensionNewsTag table.

        Args:
            articles: List of NewsArticle objects with dimension_tags
            competitor_id: Database ID of the competitor
            db_session: SQLAlchemy database session

        Returns:
            Number of tags stored
        """
        from database import DimensionNewsTag
        from datetime import datetime

        tags_stored = 0

        for article in articles:
            if not article.dimension_tags:
                continue

            for tag in article.dimension_tags:
                try:
                    # Check if this article-dimension combo already exists
                    existing = db_session.query(DimensionNewsTag).filter(
                        DimensionNewsTag.news_url == article.url,
                        DimensionNewsTag.dimension_id == tag["dimension_id"]
                    ).first()

                    if existing:
                        # Update existing tag
                        existing.relevance_score = tag["confidence"]
                        existing.sentiment = tag.get("sentiment")
                        existing.tagged_at = datetime.utcnow()
                    else:
                        # Create new tag
                        new_tag = DimensionNewsTag(
                            news_url=article.url,
                            news_title=article.title[:500] if article.title else "",
                            news_snippet=article.snippet[:1000] if article.snippet else None,
                            competitor_id=competitor_id,
                            dimension_id=tag["dimension_id"],
                            relevance_score=tag["confidence"],
                            sentiment=tag.get("sentiment"),
                            tagged_at=datetime.utcnow(),
                            tagged_by="ai"
                        )
                        db_session.add(new_tag)
                        tags_stored += 1

                except Exception as e:
                    print(f"Error storing dimension tag: {e}")
                    continue

        try:
            db_session.commit()
        except Exception as e:
            print(f"Error committing dimension tags: {e}")
            db_session.rollback()

        return tags_stored

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
def fetch_competitor_news(
    company_name: str,
    days: int = 90,
    tag_dimensions: bool = True
) -> Dict[str, Any]:
    """
    Fetch news for a competitor.

    Args:
        company_name: Name of the company
        days: Number of days to look back
        tag_dimensions: Whether to tag articles with competitive dimensions (v5.0.7)

    Returns:
        Dict with articles, sentiment, and dimension tags
    """
    monitor = NewsMonitor(tag_dimensions=tag_dimensions)
    digest = monitor.fetch_news(company_name, days)

    # v5.0.7: Count dimension tags across articles
    dimension_counts = {}
    for article in digest.articles:
        if article.dimension_tags:
            for tag in article.dimension_tags:
                dim_id = tag["dimension_id"]
                dimension_counts[dim_id] = dimension_counts.get(dim_id, 0) + 1

    return {
        "company": digest.company_name,
        "articles": [asdict(a) for a in digest.articles],
        "total_count": digest.total_count,
        "sentiment_breakdown": digest.sentiment_breakdown,
        "major_events": [asdict(a) for a in digest.major_events],
        "dimension_breakdown": dimension_counts,  # v5.0.7
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
