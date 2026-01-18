"""
Certify Intel - PitchBook/CB Insights Scraper
Fetches valuation estimates, market intelligence, and M&A predictions.
"""
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Valuation:
    """Company valuation data."""
    estimated_value: float
    valuation_date: str
    valuation_basis: str  # Last round, Revenue multiple, etc.
    confidence: str  # High, Medium, Low


@dataclass
class MarketTrend:
    """Market trend data."""
    trend_name: str
    description: str
    impact_score: float
    affected_companies: List[str]


@dataclass
class MAPrediction:
    """M&A prediction."""
    prediction_type: str  # Acquirer, Target, IPO
    confidence: str
    potential_partners: List[str]
    estimated_timeline: str
    rationale: str


@dataclass
class PitchBookData:
    """Data from PitchBook/CB Insights."""
    company_name: str
    valuation: Valuation
    valuation_history: List[Dict[str, Any]]
    revenue_estimate: Optional[float]
    revenue_growth_rate: Optional[float]
    comparable_companies: List[str]
    market_position: str
    market_size_estimate: str
    industry_trends: List[MarketTrend]
    ma_predictions: List[MAPrediction]
    exit_scenarios: List[str]
    investor_sentiment: str
    last_updated: str


class PitchBookScraper:
    """Scrapes market intelligence from PitchBook/CB Insights."""
    
    # Known market data (simulated - real PitchBook requires subscription)
    KNOWN_COMPANIES = {
        "phreesia": {
            "valuation": {"estimated_value": 1200000000, "valuation_date": "2024-01-15", "valuation_basis": "Public Market Cap", "confidence": "High"},
            "valuation_history": [
                {"date": "2024-01-01", "value": 1200000000},
                {"date": "2023-01-01", "value": 1800000000},
                {"date": "2022-01-01", "value": 3200000000},
                {"date": "2021-01-01", "value": 4500000000},
            ],
            "revenue_estimate": 397000000,
            "revenue_growth_rate": 23.5,
            "comparable_companies": ["Clearwave", "Solutionreach", "Luma Health", "Relatient"],
            "market_position": "Market Leader - Patient Intake",
            "market_size_estimate": "$2.8B (Patient Engagement Software)",
            "industry_trends": [
                {"trend_name": "Digital Front Door", "description": "Healthcare orgs prioritizing patient experience", "impact_score": 9.2, "affected_companies": ["Phreesia", "Clearwave", "Luma Health"]},
                {"trend_name": "Price Transparency", "description": "Regulation driving patient payment solutions", "impact_score": 8.5, "affected_companies": ["Phreesia", "Cedar", "Waystar"]},
            ],
            "ma_predictions": [
                {"prediction_type": "Acquirer", "confidence": "Medium", "potential_partners": ["Practice Fusion customers", "Smaller patient intake vendors"], "estimated_timeline": "12-24 months", "rationale": "Strong balance sheet, growth through acquisition history"},
            ],
            "exit_scenarios": ["Continue public growth", "PE take-private", "Strategic acquisition by EHR vendor"],
            "investor_sentiment": "Neutral - Recovering from valuation correction"
        },
        "cedar": {
            "valuation": {"estimated_value": 3200000000, "valuation_date": "2023-06-01", "valuation_basis": "Last Funding Round", "confidence": "High"},
            "valuation_history": [
                {"date": "2023-06-01", "value": 3200000000},
                {"date": "2021-03-01", "value": 3200000000},
                {"date": "2020-03-01", "value": 900000000},
                {"date": "2019-02-01", "value": 200000000},
            ],
            "revenue_estimate": 150000000,
            "revenue_growth_rate": 45.0,
            "comparable_companies": ["Phreesia (Payments)", "Waystar", "AKASA", "Collectly"],
            "market_position": "Disruptor - Patient Financial Experience",
            "market_size_estimate": "$6.5B (Healthcare RCM Software)",
            "industry_trends": [
                {"trend_name": "Patient Financial Responsibility", "description": "Rising out-of-pocket costs driving payment solutions", "impact_score": 9.5, "affected_companies": ["Cedar", "Phreesia", "Waystar"]},
                {"trend_name": "AI in RCM", "description": "Automation of revenue cycle processes", "impact_score": 8.8, "affected_companies": ["Cedar", "AKASA", "Olive AI"]},
            ],
            "ma_predictions": [
                {"prediction_type": "IPO Candidate", "confidence": "High", "potential_partners": [], "estimated_timeline": "12-18 months", "rationale": "Strong growth, well-capitalized, category leader"},
                {"prediction_type": "Acquisition Target", "confidence": "Low", "potential_partners": ["Waystar", "R1 RCM"], "estimated_timeline": "N/A", "rationale": "High valuation may deter buyers"},
            ],
            "exit_scenarios": ["IPO in 2025", "Continue private growth", "Strategic merger"],
            "investor_sentiment": "Positive - Strong growth trajectory"
        },
        "luma health": {
            "valuation": {"estimated_value": 700000000, "valuation_date": "2021-08-01", "valuation_basis": "Last Funding Round", "confidence": "Medium"},
            "valuation_history": [
                {"date": "2021-08-01", "value": 700000000},
                {"date": "2019-03-01", "value": 80000000},
                {"date": "2017-11-01", "value": 35000000},
            ],
            "revenue_estimate": 50000000,
            "revenue_growth_rate": 35.0,
            "comparable_companies": ["Phreesia", "Solutionreach", "Relatient", "Clearwave"],
            "market_position": "Challenger - Patient Success Platform",
            "market_size_estimate": "$2.8B (Patient Engagement Software)",
            "industry_trends": [
                {"trend_name": "No-Show Reduction", "description": "Focus on patient appointment adherence", "impact_score": 7.5, "affected_companies": ["Luma Health", "Solutionreach", "Relatient"]},
            ],
            "ma_predictions": [
                {"prediction_type": "Acquisition Target", "confidence": "Medium", "potential_partners": ["Phreesia", "athenahealth", "eClinicalWorks"], "estimated_timeline": "18-36 months", "rationale": "Strategic fit for larger patient engagement players"},
            ],
            "exit_scenarios": ["Acquired by larger vendor", "Series D and continued growth", "Merge with competitor"],
            "investor_sentiment": "Cautious - Needs to show path to profitability"
        },
        "waystar": {
            "valuation": {"estimated_value": 5000000000, "valuation_date": "2024-01-01", "valuation_basis": "PE Valuation", "confidence": "Medium"},
            "valuation_history": [
                {"date": "2024-01-01", "value": 5000000000},
                {"date": "2019-10-01", "value": 2700000000},
            ],
            "revenue_estimate": 700000000,
            "revenue_growth_rate": 12.0,
            "comparable_companies": ["Change Healthcare", "R1 RCM", "Availity", "Inovalon"],
            "market_position": "Market Leader - Healthcare RCM",
            "market_size_estimate": "$18B (Revenue Cycle Management)",
            "industry_trends": [
                {"trend_name": "RCM Consolidation", "description": "Large players acquiring smaller vendors", "impact_score": 9.0, "affected_companies": ["Waystar", "R1 RCM", "Change Healthcare"]},
                {"trend_name": "AI-Powered RCM", "description": "Machine learning for claims optimization", "impact_score": 8.5, "affected_companies": ["Waystar", "AKASA", "Olive AI"]},
            ],
            "ma_predictions": [
                {"prediction_type": "IPO Candidate", "confidence": "High", "potential_partners": [], "estimated_timeline": "6-12 months", "rationale": "PE exit timeline, market recovery"},
                {"prediction_type": "Acquirer", "confidence": "High", "potential_partners": ["Point-of-service vendors", "AI startups"], "estimated_timeline": "Ongoing", "rationale": "PE playbook for growth through acquisition"},
            ],
            "exit_scenarios": ["IPO in 2024", "Secondary PE sale", "Strategic acquisition"],
            "investor_sentiment": "Positive - IPO preparation underway"
        },
        "athenahealth": {
            "valuation": {"estimated_value": 17000000000, "valuation_date": "2022-02-01", "valuation_basis": "PE Acquisition", "confidence": "High"},
            "valuation_history": [
                {"date": "2022-02-01", "value": 17000000000},
                {"date": "2019-02-01", "value": 5700000000},
                {"date": "2018-01-01", "value": 6500000000},
            ],
            "revenue_estimate": 1500000000,
            "revenue_growth_rate": 8.0,
            "comparable_companies": ["eClinicalWorks", "NextGen Healthcare", "Veradigm", "Greenway Health"],
            "market_position": "Established Leader - Cloud EHR/PM",
            "market_size_estimate": "$40B (Ambulatory EHR Market)",
            "industry_trends": [
                {"trend_name": "EHR Cloud Migration", "description": "On-prem to cloud transition", "impact_score": 8.0, "affected_companies": ["athenahealth", "eClinicalWorks", "NextGen"]},
                {"trend_name": "Value-Based Care", "description": "Shift from fee-for-service", "impact_score": 7.5, "affected_companies": ["athenahealth", "Epic", "Cerner"]},
            ],
            "ma_predictions": [
                {"prediction_type": "Acquirer", "confidence": "High", "potential_partners": ["Point solutions", "Telehealth vendors", "Patient engagement tools"], "estimated_timeline": "Ongoing", "rationale": "PE-backed expansion strategy"},
                {"prediction_type": "IPO Candidate", "confidence": "Medium", "potential_partners": [], "estimated_timeline": "24-36 months", "rationale": "PE exit timeline"},
            ],
            "exit_scenarios": ["IPO", "Strategic sale to PE consortium", "Merger with competitor"],
            "investor_sentiment": "Neutral - Integration challenges post-acquisition"
        }
    }
    
    def __init__(self):
        pass
    
    def get_market_data(self, company_name: str) -> PitchBookData:
        """Get market intelligence for a company."""
        name_lower = company_name.lower()
        
        if name_lower in self.KNOWN_COMPANIES:
            return self._build_from_known(company_name, self.KNOWN_COMPANIES[name_lower])
        
        return self._build_placeholder(company_name)
    
    def _build_from_known(self, company_name: str, data: Dict) -> PitchBookData:
        """Build PitchBookData from known data."""
        val_data = data.get("valuation", {})
        valuation = Valuation(
            estimated_value=val_data.get("estimated_value", 0),
            valuation_date=val_data.get("valuation_date", ""),
            valuation_basis=val_data.get("valuation_basis", ""),
            confidence=val_data.get("confidence", "Low")
        )
        
        trends = [
            MarketTrend(
                trend_name=t["trend_name"],
                description=t["description"],
                impact_score=t["impact_score"],
                affected_companies=t.get("affected_companies", [])
            )
            for t in data.get("industry_trends", [])
        ]
        
        predictions = [
            MAPrediction(
                prediction_type=p["prediction_type"],
                confidence=p["confidence"],
                potential_partners=p.get("potential_partners", []),
                estimated_timeline=p.get("estimated_timeline", ""),
                rationale=p.get("rationale", "")
            )
            for p in data.get("ma_predictions", [])
        ]
        
        return PitchBookData(
            company_name=company_name,
            valuation=valuation,
            valuation_history=data.get("valuation_history", []),
            revenue_estimate=data.get("revenue_estimate"),
            revenue_growth_rate=data.get("revenue_growth_rate"),
            comparable_companies=data.get("comparable_companies", []),
            market_position=data.get("market_position", ""),
            market_size_estimate=data.get("market_size_estimate", ""),
            industry_trends=trends,
            ma_predictions=predictions,
            exit_scenarios=data.get("exit_scenarios", []),
            investor_sentiment=data.get("investor_sentiment", ""),
            last_updated=datetime.utcnow().isoformat()
        )
    
    def _build_placeholder(self, company_name: str) -> PitchBookData:
        """Build placeholder PitchBookData."""
        return PitchBookData(
            company_name=company_name,
            valuation=Valuation(0, "", "", "Low"),
            valuation_history=[],
            revenue_estimate=None,
            revenue_growth_rate=None,
            comparable_companies=[],
            market_position="Unknown",
            market_size_estimate="",
            industry_trends=[],
            ma_predictions=[],
            exit_scenarios=[],
            investor_sentiment="Unknown",
            last_updated=datetime.utcnow().isoformat()
        )
    
    def analyze_competitive_dynamics(self, company_name: str) -> Dict[str, Any]:
        """Analyze competitive dynamics from market data."""
        data = self.get_market_data(company_name)
        
        # Format valuation
        val = data.valuation.estimated_value
        if val >= 1000000000:
            val_str = f"${val/1000000000:.1f}B"
        elif val >= 1000000:
            val_str = f"${val/1000000:.0f}M"
        else:
            val_str = "Unknown"
        
        return {
            "company": company_name,
            "valuation": val_str,
            "valuation_confidence": data.valuation.confidence,
            "revenue_estimate": f"${data.revenue_estimate/1000000:.0f}M" if data.revenue_estimate else "Unknown",
            "growth_rate": f"{data.revenue_growth_rate}%" if data.revenue_growth_rate else "Unknown",
            "market_position": data.market_position,
            "market_size": data.market_size_estimate,
            "comparable_companies": data.comparable_companies[:5],
            "key_trends": [{"name": t.trend_name, "impact": t.impact_score} for t in data.industry_trends],
            "ma_outlook": [asdict(p) for p in data.ma_predictions],
            "investor_sentiment": data.investor_sentiment,
            "competitive_implications": self._generate_implications(data)
        }
    
    def _generate_implications(self, data: PitchBookData) -> List[str]:
        """Generate competitive implications from market data."""
        implications = []
        
        # Valuation trends
        if len(data.valuation_history) >= 2:
            latest = data.valuation_history[0]["value"]
            previous = data.valuation_history[1]["value"]
            if latest < previous * 0.7:
                implications.append("Valuation decline - potential acquisition target")
            elif latest > previous * 1.3:
                implications.append("Valuation growth - strengthening market position")
        
        # M&A predictions
        for pred in data.ma_predictions:
            if pred.prediction_type == "Acquisition Target" and pred.confidence in ["High", "Medium"]:
                implications.append(f"Potential acquisition target - {pred.rationale}")
            if pred.prediction_type == "IPO Candidate" and pred.confidence == "High":
                implications.append("IPO likely - expect increased marketing spend")
        
        # Growth analysis
        if data.revenue_growth_rate:
            if data.revenue_growth_rate > 30:
                implications.append("High growth - aggressive market capture")
            elif data.revenue_growth_rate < 10:
                implications.append("Slow growth - may be focused on profitability")
        
        return implications
    
    def compare_valuations(self, company_names: List[str]) -> Dict[str, Any]:
        """Compare valuations across companies."""
        comparison = []
        
        for name in company_names:
            data = self.get_market_data(name)
            val = data.valuation.estimated_value
            comparison.append({
                "name": name,
                "valuation": val,
                "valuation_formatted": f"${val/1000000000:.1f}B" if val >= 1000000000 else f"${val/1000000:.0f}M" if val else "Unknown",
                "revenue": data.revenue_estimate,
                "growth_rate": data.revenue_growth_rate,
                "position": data.market_position,
                "sentiment": data.investor_sentiment
            })
        
        comparison.sort(key=lambda x: x["valuation"] or 0, reverse=True)
        
        return {
            "companies": comparison,
            "highest_valuation": comparison[0]["name"] if comparison and comparison[0]["valuation"] else None,
            "fastest_growing": max(comparison, key=lambda x: x["growth_rate"] or 0)["name"] if comparison else None
        }


def get_pitchbook_data(company_name: str) -> Dict[str, Any]:
    """Get PitchBook/CB Insights data for a company."""
    scraper = PitchBookScraper()
    data = scraper.get_market_data(company_name)
    
    result = asdict(data)
    result["valuation"] = asdict(data.valuation)
    result["industry_trends"] = [asdict(t) for t in data.industry_trends]
    result["ma_predictions"] = [asdict(p) for p in data.ma_predictions]
    
    return result


if __name__ == "__main__":
    scraper = PitchBookScraper()
    
    print("=" * 60)
    print("PitchBook Market Intelligence")
    print("=" * 60)
    
    for company in ["Phreesia", "Cedar", "Waystar", "athenahealth"]:
        data = scraper.get_market_data(company)
        val = data.valuation.estimated_value
        val_str = f"${val/1000000000:.1f}B" if val >= 1000000000 else f"${val/1000000:.0f}M"
        print(f"\n{company}:")
        print(f"  Valuation: {val_str} ({data.valuation.confidence})")
        print(f"  Position: {data.market_position}")
        print(f"  Sentiment: {data.investor_sentiment}")
        if data.ma_predictions:
            print(f"  M&A: {data.ma_predictions[0].prediction_type} ({data.ma_predictions[0].confidence})")
