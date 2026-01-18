"""
Certify Intel - Extended Models and Features
User Authentication, Win/Loss Database, SimilarWeb, Social Media, Caching
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import lru_cache
import json

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from jose import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# Use hashlib for password hashing (Python 3.14 compatible)
# bcrypt/passlib has compatibility issues with Python 3.14
AUTH_AVAILABLE = True


# ============== User Authentication ==============

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


class User:
    """User model for authentication."""
    def __init__(
        self,
        id: int,
        email: str,
        hashed_password: str,
        full_name: str = "",
        role: str = "viewer",  # viewer, analyst, admin
        is_active: bool = True,
        created_at: datetime = None
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()


class AuthManager:
    """Handles user authentication."""
    
    def __init__(self):
        # In-memory user store for demo (use DB in production)
        self.users: Dict[str, User] = {}
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user."""
        admin_email = os.getenv("ADMIN_EMAIL", "admin@certifyhealth.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "certifyintel2024")
        
        self.create_user(
            email=admin_email,
            password=admin_password,
            full_name="System Admin",
            role="admin"
        )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash."""
        # Use hashlib for Python 3.14 compatibility
        return self.hash_password(plain_password) == hashed_password
    
    def hash_password(self, password: str) -> str:
        """Hash a password using hashlib (Python 3.14 compatible)."""
        # Use SHA256 with salt for simple hashing
        salted = f"{SECRET_KEY}{password}"
        return hashlib.sha256(salted.encode()).hexdigest()
    
    def create_user(self, email: str, password: str, full_name: str = "", role: str = "viewer") -> User:
        """Create a new user."""
        user = User(
            id=len(self.users) + 1,
            email=email,
            hashed_password=self.hash_password(password),
            full_name=full_name,
            role=role
        )
        self.users[email] = user
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        user = self.users.get(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        
        if AUTH_AVAILABLE:
            return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        else:
            # Simple token for demo
            return hashlib.sha256(json.dumps(to_encode).encode()).hexdigest()
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token."""
        try:
            if AUTH_AVAILABLE:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                return payload
        except:
            pass
        return None


# ============== Win/Loss Database ==============

class WinLossRecord:
    """Record of a competitive deal."""
    def __init__(
        self,
        id: int,
        competitor_id: Optional[int],
        competitor_name: str,
        outcome: str,  # "win" or "loss"
        deal_value: Optional[float] = None,
        deal_date: datetime = None,
        customer_name: Optional[str] = None,
        customer_size: Optional[str] = None,
        loss_reason: Optional[str] = None,
        win_factor: Optional[str] = None,
        sales_rep: Optional[str] = None,
        notes: Optional[str] = None
    ):
        self.id = id
        self.competitor_id = competitor_id
        self.competitor_name = competitor_name
        self.outcome = outcome
        self.deal_value = deal_value
        self.deal_date = deal_date or datetime.utcnow()
        self.customer_name = customer_name
        self.customer_size = customer_size
        self.loss_reason = loss_reason
        self.win_factor = win_factor
        self.sales_rep = sales_rep
        self.notes = notes


class WinLossTracker:
    """Tracks competitive win/loss data."""
    
    def __init__(self):
        self.records: List[WinLossRecord] = []
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample win/loss data."""
        sample = [
            WinLossRecord(1, 1, "Phreesia", "loss", 50000, 
                         loss_reason="Feature gap - lacked telehealth",
                         customer_size="Large (50+)"),
            WinLossRecord(2, 2, "Clearwave", "win", 35000,
                         win_factor="Faster implementation",
                         customer_size="Medium (15-50)"),
            WinLossRecord(3, 1, "Phreesia", "win", 45000,
                         win_factor="Better EHR integration",
                         customer_size="Medium (15-50)"),
            WinLossRecord(4, 5, "Kareo", "loss", 15000,
                         loss_reason="Price too high",
                         customer_size="Small (1-15)"),
            WinLossRecord(5, 3, "Epion Health", "win", 60000,
                         win_factor="Customer support",
                         customer_size="Large (50+)"),
        ]
        self.records = sample
    
    def add_record(self, record: WinLossRecord):
        """Add a new win/loss record."""
        record.id = len(self.records) + 1
        self.records.append(record)
    
    def get_records(self, competitor_name: Optional[str] = None, outcome: Optional[str] = None) -> List[WinLossRecord]:
        """Get filtered records."""
        result = self.records
        if competitor_name:
            result = [r for r in result if r.competitor_name.lower() == competitor_name.lower()]
        if outcome:
            result = [r for r in result if r.outcome == outcome]
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get win/loss statistics."""
        wins = [r for r in self.records if r.outcome == "win"]
        losses = [r for r in self.records if r.outcome == "loss"]
        
        win_rate = len(wins) / len(self.records) * 100 if self.records else 0
        
        # By competitor
        by_competitor = {}
        for r in self.records:
            if r.competitor_name not in by_competitor:
                by_competitor[r.competitor_name] = {"wins": 0, "losses": 0}
            by_competitor[r.competitor_name][f"{r.outcome}s" if r.outcome == "win" else "losses"] += 1
        
        # Calculate win rates per competitor
        for comp, data in by_competitor.items():
            total = data["wins"] + data["losses"]
            data["win_rate"] = round(data["wins"] / total * 100, 1) if total > 0 else 0
        
        # Common loss reasons
        loss_reasons = {}
        for r in losses:
            if r.loss_reason:
                loss_reasons[r.loss_reason] = loss_reasons.get(r.loss_reason, 0) + 1
        
        # Common win factors
        win_factors = {}
        for r in wins:
            if r.win_factor:
                win_factors[r.win_factor] = win_factors.get(r.win_factor, 0) + 1
        
        return {
            "total_deals": len(self.records),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 1),
            "total_value_won": sum(r.deal_value or 0 for r in wins),
            "total_value_lost": sum(r.deal_value or 0 for r in losses),
            "by_competitor": by_competitor,
            "top_loss_reasons": dict(sorted(loss_reasons.items(), key=lambda x: -x[1])[:5]),
            "top_win_factors": dict(sorted(win_factors.items(), key=lambda x: -x[1])[:5]),
        }


# ============== SimilarWeb Integration ==============

class SimilarWebData:
    """SimilarWeb traffic data."""
    def __init__(
        self,
        domain: str,
        total_visits: int = 0,
        avg_visit_duration: str = "0:00",
        pages_per_visit: float = 0,
        bounce_rate: float = 0,
        traffic_sources: Dict[str, float] = None,
        top_countries: Dict[str, float] = None,
        scraped_at: datetime = None
    ):
        self.domain = domain
        self.total_visits = total_visits
        self.avg_visit_duration = avg_visit_duration
        self.pages_per_visit = pages_per_visit
        self.bounce_rate = bounce_rate
        self.traffic_sources = traffic_sources or {}
        self.top_countries = top_countries or {}
        self.scraped_at = scraped_at or datetime.utcnow()


class SimilarWebScraper:
    """Fetches traffic data from SimilarWeb."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SIMILARWEB_API_KEY")
    
    async def get_traffic_data(self, domain: str) -> SimilarWebData:
        """Get traffic data for a domain."""
        # Note: SimilarWeb requires paid API access
        # Using mock data for demo
        
        mock_data = {
            "phreesia.com": SimilarWebData(
                domain="phreesia.com",
                total_visits=520000,
                avg_visit_duration="3:45",
                pages_per_visit=4.2,
                bounce_rate=38.5,
                traffic_sources={"Direct": 45, "Search": 35, "Referral": 12, "Social": 8},
                top_countries={"US": 85, "CA": 5, "UK": 3}
            ),
            "clearwaveinc.com": SimilarWebData(
                domain="clearwaveinc.com",
                total_visits=48000,
                avg_visit_duration="2:30",
                pages_per_visit=3.5,
                bounce_rate=45.2,
                traffic_sources={"Direct": 40, "Search": 40, "Referral": 15, "Social": 5},
                top_countries={"US": 92, "CA": 3, "UK": 2}
            ),
        }
        
        # Extract domain from URL
        clean_domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        
        return mock_data.get(clean_domain, SimilarWebData(domain=clean_domain, total_visits=10000))


# ============== Social Media Monitoring ==============

class SocialPost:
    """Social media post/mention."""
    def __init__(
        self,
        platform: str,  # twitter, linkedin, facebook
        content: str,
        url: str,
        author: Optional[str] = None,
        posted_at: datetime = None,
        engagement: int = 0,
        sentiment: Optional[str] = None  # positive, negative, neutral
    ):
        self.platform = platform
        self.content = content
        self.url = url
        self.author = author
        self.posted_at = posted_at or datetime.utcnow()
        self.engagement = engagement
        self.sentiment = sentiment


class SocialMediaMonitor:
    """Monitors social media for competitor mentions."""
    
    def __init__(self):
        self.twitter_api_key = os.getenv("TWITTER_API_KEY")
        self.linkedin_api_key = os.getenv("LINKEDIN_API_KEY")
    
    async def search_mentions(self, company_name: str, days: int = 7) -> List[SocialPost]:
        """Search for company mentions across social platforms."""
        # Note: Requires API access to social platforms
        # Using mock data for demo
        
        mock_posts = [
            SocialPost(
                platform="twitter",
                content=f"Just implemented {company_name} for our practice - great experience so far!",
                url="https://twitter.com/...",
                author="@healthcareIT",
                engagement=45,
                sentiment="positive"
            ),
            SocialPost(
                platform="linkedin",
                content=f"{company_name} announces new AI-powered intake features",
                url="https://linkedin.com/...",
                author="Healthcare IT News",
                engagement=230,
                sentiment="neutral"
            ),
            SocialPost(
                platform="twitter",
                content=f"Having issues with {company_name} integration today. Anyone else?",
                url="https://twitter.com/...",
                author="@practiceadmin",
                engagement=12,
                sentiment="negative"
            ),
        ]
        
        return mock_posts
    
    def analyze_sentiment(self, posts: List[SocialPost]) -> Dict[str, Any]:
        """Analyze sentiment across posts."""
        if not posts:
            return {"total": 0, "positive": 0, "negative": 0, "neutral": 0}
        
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        for post in posts:
            if post.sentiment:
                sentiments[post.sentiment] += 1
        
        total = len(posts)
        return {
            "total": total,
            "positive": sentiments["positive"],
            "negative": sentiments["negative"],
            "neutral": sentiments["neutral"],
            "sentiment_score": round((sentiments["positive"] - sentiments["negative"]) / total * 100, 1)
        }


# ============== API Rate Limiting & Caching ==============

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self.requests: Dict[str, List[datetime]] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                t for t in self.requests[client_id] 
                if t > minute_ago
            ]
        else:
            self.requests[client_id] = []
        
        # Check limit
        if len(self.requests[client_id]) >= self.limit:
            return False
        
        self.requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for this minute."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        if client_id not in self.requests:
            return self.limit
        
        recent = [t for t in self.requests[client_id] if t > minute_ago]
        return max(0, self.limit - len(recent))


class CacheManager:
    """Manages API response caching."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self.cache: Dict[str, tuple] = {}  # key -> (value, expiry)
        self.redis_client = None
        
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    decode_responses=True
                )
                self.redis_client.ping()
            except:
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            except:
                pass
        
        # Fallback to in-memory
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.utcnow() < expiry:
                return value
            del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set cached value."""
        ttl = ttl or self.ttl
        
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
                return
            except:
                pass
        
        # Fallback to in-memory
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
    
    def invalidate(self, key: str):
        """Invalidate cached value."""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except:
                pass
        
        if key in self.cache:
            del self.cache[key]
    
    def clear_all(self):
        """Clear all cached values."""
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except:
                pass
        self.cache.clear()


# Decorator for caching function results
def cached(ttl_seconds: int = 300):
    """Decorator for caching function results."""
    cache_manager = CacheManager(ttl_seconds)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_value = cache_manager.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache_manager.set(key, result)
            
            return result
        return wrapper
    return decorator


# ============== Singleton Instances ==============

auth_manager = AuthManager()
win_loss_tracker = WinLossTracker()
rate_limiter = RateLimiter()
cache_manager = CacheManager()
similarweb_scraper = SimilarWebScraper()
social_monitor = SocialMediaMonitor()


if __name__ == "__main__":
    # Test
    print("Win/Loss Stats:")
    print(json.dumps(win_loss_tracker.get_stats(), indent=2))
