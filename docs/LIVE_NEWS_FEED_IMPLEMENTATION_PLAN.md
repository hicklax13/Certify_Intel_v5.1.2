# Live News Feed Implementation Plan

## Overview
Add a dedicated "News Feed" page to Certify Intel that displays an aggregated, filterable table of news articles mentioning tracked competitors.

---

## Complete Data Sources Table (3 Existing + 10 New)

### EXISTING SOURCES (Currently in Codebase)

| # | Source | API Key Required | Account Required | Free Tier Limit | Status | Data Provided |
|---|--------|------------------|------------------|-----------------|--------|---------------|
| 1 | [Google News RSS](https://news.google.com/rss) | ❌ No | ❌ No | **Unlimited** | ✅ Active | News articles by company name search |
| 2 | [NewsAPI.org](https://newsapi.org/) | ✅ Yes (`NEWSAPI_KEY`) | ✅ Yes | 100 req/day | ⚠️ Inactive | 80,000+ sources, historical news |
| 3 | [Bing News API](https://www.microsoft.com/en-us/bing/apis/bing-news-search-api) | ✅ Yes (`BING_NEWS_KEY`) | ✅ Yes | 1,000 req/mo | ⚠️ Inactive | Real-time news, trending topics |

---

### NEW SOURCES TO ADD

#### Category A: Free News APIs (No Cost)

| # | Source | API Key Required | Account Required | Free Tier Limit | Data Provided | Why Add It |
|---|--------|------------------|------------------|-----------------|---------------|------------|
| 4 | [GNews API](https://gnews.io/) | ✅ Yes | ✅ Yes (free) | 100 req/day | 60,000+ sources, historical to 6 years | Lightweight, fast response, good for breaking news |
| 5 | [MediaStack](https://mediastack.com/) | ✅ Yes | ✅ Yes (free) | 500 req/mo | 7,500+ sources in 50 countries, 13 languages | Broad international coverage for global competitors |
| 6 | [TheNewsAPI](https://www.thenewsapi.com/) | ✅ Yes | ✅ Yes (no credit card) | Free tier | 40,000+ sources, 50 countries, 30 languages | 1M+ articles indexed weekly, advanced filtering |
| 7 | [NewsData.io](https://newsdata.io/) | ✅ Yes | ✅ Yes (free) | 200 req/day | 89 languages, crypto/tech news specialty | Best for tech/healthcare news categorization |

#### Category B: Government Open Data (100% Free, No Limits)

| # | Source | API Key Required | Account Required | Free Tier Limit | Data Provided | Why Add It |
|---|--------|------------------|------------------|-----------------|---------------|------------|
| 8 | [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | ❌ No | ❌ No | **Unlimited** (10 req/sec) | Company filings (10-K, 10-Q, 8-K), financials, ownership | Track public competitor SEC filings, M&A, leadership changes |
| 9 | [USPTO PatentsView API](https://patentsview.org/apis/purpose) | ❌ No | ❌ No | **Unlimited** | Patent filings, inventor data, innovation trends | Track competitor R&D activity, product launches, IP |

#### Category C: Open Source Tools (GitHub)

| # | Source | API Key Required | Account Required | Free Tier Limit | Data Provided | Why Add It |
|---|--------|------------------|------------------|-----------------|---------------|------------|
| 10 | [pygooglenews](https://github.com/kotartemiy/pygooglenews) | ❌ No | ❌ No | **Unlimited** | Enhanced Google News with geo, topic, date filters | Better filtering than raw RSS, Python native |
| 11 | [Universal-News-Scraper](https://github.com/Ilias1988/Universal-News-Scraper) | ❌ No | ❌ No | **Unlimited** | Multi-source aggregation, anti-blocking, CSV export | Backup scraper with Bing RSS auto-discovery |

#### Category D: AI Subscription Tools (Included in Your Plans)

| # | Source | API Key Required | Account Required | Free Tier Limit | Data Provided | Why Add It |
|---|--------|------------------|------------------|-----------------|---------------|------------|
| 12 | [ChatGPT Deep Research + Operator](https://openai.com/index/introducing-deep-research/) (ChatGPT Plus $20/mo) | ❌ Included | ✅ ChatGPT Plus | 25 queries/mo (Plus), 40 agent actions/mo | Multi-source synthesis, web browsing, competitor reports | Automated competitive analysis reports on demand |
| 13 | [Gemini Deep Research](https://gemini.google/overview/deep-research/) (Google AI Pro $20/mo) | ❌ Included | ✅ Gemini Pro | Included in subscription | Web grounding, cited research reports | Google Search integration, Workspace export |

#### Category E: AI Enhancement Tools

| # | Source | API Key Required | Account Required | Free Tier Limit | Data Provided | Why Add It |
|---|--------|------------------|------------------|-----------------|---------------|------------|
| 14 | [Firecrawl MCP Server](https://github.com/firecrawl/firecrawl-mcp-server) (Claude Max $200/mo) | ✅ Yes (free tier) | ✅ Firecrawl account | 500 credits free | Web scraping, structured data extraction | Scrape competitor websites, pricing pages, job boards |
| 15 | [Hugging Face Sentiment Models](https://huggingface.co/models?other=sentiment-analysis) | ❌ No | ❌ No | **Unlimited** | Sentiment classification (positive/negative/neutral) | Enhance existing keyword sentiment with ML models |

#### Category F: Company Intelligence (Free Tiers)

| # | Source | API Key Required | Account Required | Free Tier Limit | Data Provided | Why Add It |
|---|--------|------------------|------------------|-----------------|---------------|------------|
| 16 | [Growjo API](https://growjo.com/) | ❌ No | ❌ No | **Unlimited** | 200K+ startups, revenue estimates, growth signals | Track competitor growth, hiring trends, funding signals |

---

## Summary Table: All 16 Sources

| # | Source | Cost | Key Needed | Limit | Best For |
|---|--------|------|------------|-------|----------|
| 1 | Google News RSS | FREE | ❌ | Unlimited | Primary news source |
| 2 | NewsAPI.org | FREE | ✅ | 100/day | Historical articles |
| 3 | Bing News API | FREE | ✅ | 1000/mo | Trending news |
| 4 | GNews API | FREE | ✅ | 100/day | Breaking news |
| 5 | MediaStack | FREE | ✅ | 500/mo | International coverage |
| 6 | TheNewsAPI | FREE | ✅ | Free tier | Volume (1M+/week) |
| 7 | NewsData.io | FREE | ✅ | 200/day | Tech/healthcare news |
| 8 | SEC EDGAR | FREE | ❌ | Unlimited | Financial filings |
| 9 | USPTO Patents | FREE | ❌ | Unlimited | R&D/innovation tracking |
| 10 | pygooglenews | FREE | ❌ | Unlimited | Enhanced RSS parsing |
| 11 | Universal-News-Scraper | FREE | ❌ | Unlimited | Backup scraper |
| 12 | ChatGPT Deep Research | $20/mo | ❌ | 25/mo | AI research reports |
| 13 | Gemini Deep Research | $20/mo | ❌ | Included | Google-powered research |
| 14 | Firecrawl MCP | $200/mo* | ✅ | 500 free | Website scraping |
| 15 | Hugging Face Models | FREE | ❌ | Unlimited | ML sentiment analysis |
| 16 | Growjo | FREE | ❌ | Unlimited | Company growth data |

*Included with Claude Max subscription

---

## What Each Source Enhances

| Source | Enhances | New Data Added |
|--------|----------|----------------|
| GNews, MediaStack, TheNewsAPI, NewsData.io | News Feed | More sources, languages, better coverage |
| SEC EDGAR | Change Log, Analytics | 8-K filings (M&A, leadership), 10-K financials |
| USPTO Patents | Analytics, Battlecards | Patent counts, innovation scores, R&D focus |
| pygooglenews | News Feed | Better date/geo filtering on Google News |
| ChatGPT/Gemini Deep Research | Battlecards, Analytics | AI-generated competitive reports |
| Firecrawl MCP | Competitors, Data Quality | Live website scraping for pricing, features |
| Hugging Face | News Feed, Analytics | ML-based sentiment (replaces keyword matching) |
| Growjo | Competitors, Dashboard | Revenue estimates, growth rates, hiring data |

---

## Implementation Priority

### Phase 1: Quick Wins (No API Keys Needed)
1. **SEC EDGAR** - Add endpoint for 8-K filings (leadership changes, M&A)
2. **USPTO PatentsView** - Already partially implemented, enhance for news feed
3. **pygooglenews** - Replace raw RSS parsing with library
4. **Hugging Face** - Upgrade sentiment from keywords to ML model

### Phase 2: API Key Sources (Free Registration)
5. **GNews API** - Add as secondary news source
6. **NewsData.io** - Add for tech/healthcare specialty
7. **MediaStack** - Add for international coverage

### Phase 3: AI Subscription Integration
8. **ChatGPT Deep Research** - Add "Generate Report" button on Battlecards
9. **Gemini Deep Research** - Add as alternative research option
10. **Firecrawl MCP** - Add website scraping for competitor profiles

---

## Files to Modify

| File | Changes |
|------|---------|
| `backend/main.py` | Add `/api/news-feed` endpoint |
| `backend/news_monitor.py` | Add new source integrations |
| `frontend/index.html` | Add sidebar item + page section |
| `frontend/app_v2.js` | Add `loadNewsFeed()` and dropdown population |
| `frontend/styles.css` | Badge styles for sentiment (if not exists) |
| `backend/requirements.txt` | Add `pygooglenews`, `transformers` |

---

## Required User Inputs (News Feed Page)

| Field | Required | Validation |
|-------|----------|------------|
| Competitor | ✅ Yes | Must select from dropdown |
| From Date | ✅ Yes | Valid date, not future |
| To Date | ✅ Yes | Valid date, >= From Date |
| Sentiment | ❌ No | Optional filter |
| Source | ❌ No | Optional: filter by data source |

---

## Estimated Effort

| Task | Time |
|------|------|
| Backend endpoint | 15 min |
| Frontend HTML | 10 min |
| Frontend JS | 15 min |
| CSS styling | 5 min |
| Add pygooglenews | 10 min |
| Add Hugging Face sentiment | 20 min |
| Testing | 15 min |
| **Total** | **~1.5 hours** |

---

## Research Sources

- [NewsData.io - Free News APIs 2026](https://newsdata.io/blog/best-free-news-api/)
- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [USPTO PatentsView](https://patentsview.org/apis/purpose)
- [OpenAI Deep Research](https://openai.com/index/introducing-deep-research/)
- [Gemini Deep Research](https://gemini.google/overview/deep-research/)
- [Firecrawl MCP Server](https://github.com/firecrawl/firecrawl-mcp-server)
- [Hugging Face Sentiment Models](https://huggingface.co/models?other=sentiment-analysis)
- [Growjo Company API](https://growjo.com/)
- [GitHub News Aggregator Topic](https://github.com/topics/news-aggregator)
