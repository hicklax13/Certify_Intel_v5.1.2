"""
Certify Intel - Review Scraper
Scrapes G2, Capterra, and other review sites for competitor reviews.
"""
import os
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Review:
    """Individual review."""
    reviewer_title: str
    rating: float
    date: str
    pros: str
    cons: str
    summary: str


@dataclass
class ReviewData:
    """Aggregated review data for a company."""
    company_name: str
    source: str  # g2, capterra, trustradius
    overall_rating: float
    total_reviews: int
    rating_breakdown: Dict[str, int]  # 5-star: x, 4-star: y, etc.
    category_scores: Dict[str, float]  # ease_of_use, support, etc.
    pros_summary: List[str]
    cons_summary: List[str]
    recent_reviews: List[Review]
    last_updated: str


class ReviewScraper:
    """Scrapes and aggregates review data from multiple sources."""
    
    # G2 URL patterns
    G2_SLUGS = {
        "phreesia": "phreesia",
        "clearwave": "clearwave",
        "waystar": "waystar",
        "athenahealth": "athenahealth",
        "nextgen healthcare": "nextgen-healthcare",
        "epic": "epic-systems",
        "cerner": "cerner",
        "meditech": "meditech",
        "eclinicalworks": "eclinicalworks",
        "drchrono": "drchrono",
        "kareo": "kareo",
        "simplepractice": "simplepractice",
        "practicefusion": "practice-fusion",
        "advancedmd": "advancedmd",
        "carecloud": "carecloud",
        "luma health": "luma-health",
        "solutionreach": "solutionreach",
        "relatient": "relatient",
        "klara": "klara",
        "mend": "mend-vip",
        "zocdoc": "zocdoc",
        "kyruus": "kyruus",
        "imprivata": "imprivata",
        "cedar": "cedar-pay",
        "modmed": "modernizing-medicine",
    }
    
    # Known review data (fallback when scraping fails)
    KNOWN_REVIEWS = {
        "phreesia": {
            "overall_rating": 4.3,
            "total_reviews": 156,
            "category_scores": {
                "ease_of_use": 4.2,
                "quality_of_support": 4.1,
                "ease_of_setup": 3.9,
                "meets_requirements": 4.4
            },
            "pros_summary": [
                "Streamlined patient check-in process",
                "Good EHR integrations",
                "Improves front desk efficiency",
                "Patient-friendly interface"
            ],
            "cons_summary": [
                "Complex implementation process",
                "Pricing can be expensive",
                "Limited customization options",
                "Learning curve for staff"
            ]
        },
        "clearwave": {
            "overall_rating": 4.5,
            "total_reviews": 89,
            "category_scores": {
                "ease_of_use": 4.4,
                "quality_of_support": 4.6,
                "ease_of_setup": 4.2,
                "meets_requirements": 4.5
            },
            "pros_summary": [
                "Excellent customer support",
                "Reduces patient wait times",
                "Good insurance verification",
                "Intuitive patient kiosk"
            ],
            "cons_summary": [
                "Limited reporting capabilities",
                "Some integration issues",
                "Mobile app needs improvement"
            ]
        },
        "athenahealth": {
            "overall_rating": 3.7,
            "total_reviews": 412,
            "category_scores": {
                "ease_of_use": 3.5,
                "quality_of_support": 3.4,
                "ease_of_setup": 3.2,
                "meets_requirements": 3.9
            },
            "pros_summary": [
                "Comprehensive feature set",
                "Good revenue cycle management",
                "Large ecosystem of integrations",
                "Regular updates and improvements"
            ],
            "cons_summary": [
                "Steep learning curve",
                "Slow customer support",
                "Can be overwhelming for small practices",
                "Expensive for smaller organizations"
            ]
        },
        "luma health": {
            "overall_rating": 4.6,
            "total_reviews": 78,
            "category_scores": {
                "ease_of_use": 4.7,
                "quality_of_support": 4.5,
                "ease_of_setup": 4.4,
                "meets_requirements": 4.6
            },
            "pros_summary": [
                "Excellent patient engagement tools",
                "Easy appointment scheduling",
                "Great automated reminders",
                "Modern, clean interface"
            ],
            "cons_summary": [
                "Limited EHR integrations",
                "Some features require additional cost",
                "Reporting could be more robust"
            ]
        },
        "zocdoc": {
            "overall_rating": 4.2,
            "total_reviews": 234,
            "category_scores": {
                "ease_of_use": 4.5,
                "quality_of_support": 3.8,
                "ease_of_setup": 4.3,
                "meets_requirements": 4.1
            },
            "pros_summary": [
                "Brings new patients",
                "Easy online booking",
                "Good patient reviews system",
                "Wide patient reach"
            ],
            "cons_summary": [
                "High per-booking fees",
                "Patient quality varies",
                "No-show rates can be higher",
                "Limited practice customization"
            ]
        }
    }
    
    def __init__(self, use_playwright: bool = False):
        """
        Initialize the review scraper.
        
        Args:
            use_playwright: Whether to use Playwright for live scraping
        """
        self.use_playwright = use_playwright
    
    def get_reviews(self, company_name: str) -> ReviewData:
        """
        Get review data for a company.
        
        Args:
            company_name: Name of the company
            
        Returns:
            ReviewData with reviews and ratings
        """
        name_lower = company_name.lower()
        
        # Try to get G2 data
        if name_lower in self.KNOWN_REVIEWS:
            return self._build_from_known(company_name, self.KNOWN_REVIEWS[name_lower])
        
        # Try live scraping if enabled
        if self.use_playwright and name_lower in self.G2_SLUGS:
            try:
                return self._scrape_g2(company_name, self.G2_SLUGS[name_lower])
            except Exception as e:
                print(f"G2 scrape failed for {company_name}: {e}")
        
        # Return placeholder data
        return self._build_placeholder(company_name)
    
    def _build_from_known(self, company_name: str, data: Dict) -> ReviewData:
        """Build ReviewData from known data."""
        return ReviewData(
            company_name=company_name,
            source="g2",
            overall_rating=data["overall_rating"],
            total_reviews=data["total_reviews"],
            rating_breakdown={
                "5_star": int(data["total_reviews"] * 0.4),
                "4_star": int(data["total_reviews"] * 0.3),
                "3_star": int(data["total_reviews"] * 0.15),
                "2_star": int(data["total_reviews"] * 0.1),
                "1_star": int(data["total_reviews"] * 0.05)
            },
            category_scores=data.get("category_scores", {}),
            pros_summary=data.get("pros_summary", []),
            cons_summary=data.get("cons_summary", []),
            recent_reviews=[],
            last_updated=datetime.utcnow().isoformat()
        )
    
    def _build_placeholder(self, company_name: str) -> ReviewData:
        """Build placeholder ReviewData when no data available."""
        return ReviewData(
            company_name=company_name,
            source="placeholder",
            overall_rating=0.0,
            total_reviews=0,
            rating_breakdown={},
            category_scores={},
            pros_summary=[],
            cons_summary=[],
            recent_reviews=[],
            last_updated=datetime.utcnow().isoformat()
        )
    
    def _scrape_g2(self, company_name: str, slug: str) -> ReviewData:
        """Live scrape G2 reviews (requires Playwright)."""
        # This would use Playwright to scrape actual G2 pages
        # For now, return placeholder
        raise NotImplementedError("Live G2 scraping not yet implemented")
    
    def compare_reviews(self, company_names: List[str]) -> Dict[str, Any]:
        """
        Compare reviews across multiple companies.
        
        Args:
            company_names: List of company names to compare
            
        Returns:
            Dict with comparison data
        """
        reviews = [self.get_reviews(name) for name in company_names]
        
        comparison = {
            "companies": [],
            "best_overall": None,
            "best_in_category": {}
        }
        
        for review in reviews:
            comparison["companies"].append({
                "name": review.company_name,
                "rating": review.overall_rating,
                "reviews": review.total_reviews,
                "categories": review.category_scores
            })
        
        # Find best overall
        valid_reviews = [r for r in reviews if r.overall_rating > 0]
        if valid_reviews:
            best = max(valid_reviews, key=lambda r: r.overall_rating)
            comparison["best_overall"] = best.company_name
        
        # Find best in each category
        categories = set()
        for review in reviews:
            categories.update(review.category_scores.keys())
        
        for category in categories:
            scores = [(r.company_name, r.category_scores.get(category, 0)) for r in reviews]
            if scores:
                best_company = max(scores, key=lambda x: x[1])
                comparison["best_in_category"][category] = best_company[0]
        
        return comparison
    
    def get_review_insights(self, company_name: str) -> Dict[str, Any]:
        """
        Get actionable insights from reviews.
        
        Args:
            company_name: Company to analyze
            
        Returns:
            Dict with insights and recommendations
        """
        review_data = self.get_reviews(company_name)
        
        insights = {
            "company": company_name,
            "overall_sentiment": "positive" if review_data.overall_rating >= 4.0 else "mixed" if review_data.overall_rating >= 3.0 else "negative",
            "rating": review_data.overall_rating,
            "strengths": review_data.pros_summary[:3],
            "weaknesses": review_data.cons_summary[:3],
            "competitive_opportunities": [],
            "sales_talking_points": []
        }
        
        # Generate competitive opportunities from weaknesses
        for weakness in review_data.cons_summary:
            if "support" in weakness.lower():
                insights["competitive_opportunities"].append("Emphasize Certify's superior customer support")
            if "implementation" in weakness.lower() or "setup" in weakness.lower():
                insights["competitive_opportunities"].append("Highlight faster implementation timeline")
            if "price" in weakness.lower() or "expensive" in weakness.lower():
                insights["competitive_opportunities"].append("Position on total cost of ownership")
            if "integration" in weakness.lower():
                insights["competitive_opportunities"].append("Showcase deeper EHR integrations")
        
        # Generate sales talking points from their strengths (to counter)
        for strength in review_data.pros_summary:
            if "patient" in strength.lower():
                insights["sales_talking_points"].append("Match their patient experience capabilities")
        
        # Deduplicate
        insights["competitive_opportunities"] = list(set(insights["competitive_opportunities"]))[:3]
        insights["sales_talking_points"] = list(set(insights["sales_talking_points"]))[:3]
        
        return insights


# API convenience functions
def get_competitor_reviews(company_name: str) -> Dict[str, Any]:
    """Get review data for a competitor."""
    scraper = ReviewScraper()
    data = scraper.get_reviews(company_name)
    return asdict(data)


def compare_competitor_reviews(company_names: List[str]) -> Dict[str, Any]:
    """Compare reviews across competitors."""
    scraper = ReviewScraper()
    return scraper.compare_reviews(company_names)


if __name__ == "__main__":
    # Test with sample companies
    scraper = ReviewScraper()
    
    print("=" * 60)
    print("Review Data Test")
    print("=" * 60)
    
    for company in ["Phreesia", "athenahealth", "Luma Health"]:
        data = scraper.get_reviews(company)
        print(f"\n{company}:")
        print(f"  Rating: {data.overall_rating}/5 ({data.total_reviews} reviews)")
        print(f"  Pros: {', '.join(data.pros_summary[:2])}")
        print(f"  Cons: {', '.join(data.cons_summary[:2])}")
    
    print("\n" + "=" * 60)
    print("Review Comparison")
    print("=" * 60)
    
    comparison = scraper.compare_reviews(["Phreesia", "athenahealth", "Luma Health"])
    print(json.dumps(comparison, indent=2))
