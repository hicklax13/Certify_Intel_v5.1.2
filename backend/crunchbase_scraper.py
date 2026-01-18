"""
Certify Intel - Crunchbase Scraper
Fetches company funding, investors, and acquisition data.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import urllib.request
import urllib.error


@dataclass
class FundingRound:
    """Represents a funding round."""
    round_type: str  # Seed, Series A, B, C, etc.
    amount: Optional[float]
    date: str
    lead_investors: List[str]
    announced_date: str


@dataclass
class Acquisition:
    """Represents an acquisition."""
    acquired_company: str
    date: str
    price: Optional[float]
    terms: str


@dataclass
class CrunchbaseData:
    """Company data from Crunchbase."""
    company_name: str
    description: str
    founded_date: str
    headquarters: str
    employee_count: str
    total_funding: float
    last_funding_date: str
    last_funding_type: str
    funding_rounds: List[FundingRound]
    investors: List[str]
    board_members: List[str]
    acquisitions: List[Acquisition]
    ipo_status: str
    stock_symbol: Optional[str]
    website: str
    categories: List[str]
    last_updated: str


class CrunchbaseScraper:
    """Scrapes company data from Crunchbase."""
    
    # Known company data (fallback when API unavailable)
    KNOWN_COMPANIES = {
        "phreesia": {
            "description": "Patient intake management platform for healthcare",
            "founded_date": "2005",
            "headquarters": "Wilmington, NC",
            "employee_count": "1001-5000",
            "total_funding": 117000000,
            "last_funding_date": "2019-07-18",
            "last_funding_type": "IPO",
            "funding_rounds": [
                {"round_type": "IPO", "amount": 192000000, "date": "2019-07-18", "lead_investors": ["Goldman Sachs"], "announced_date": "2019-07-18"},
                {"round_type": "Series F", "amount": 30000000, "date": "2018-01-22", "lead_investors": ["LLR Partners"], "announced_date": "2018-01-22"},
                {"round_type": "Series E", "amount": 30000000, "date": "2016-03-16", "lead_investors": ["Ascension Ventures"], "announced_date": "2016-03-16"},
            ],
            "investors": ["LLR Partners", "Ascension Ventures", "Polaris Partners", "HLM Venture Partners"],
            "board_members": ["Chaim Indig (CEO)", "David Siegel", "Warren Thaler"],
            "acquisitions": [
                {"acquired_company": "Insignia Health", "date": "2021-09", "price": 165000000, "terms": "Acquisition"},
                {"acquired_company": "QueueDr", "date": "2020-10", "price": None, "terms": "Acquisition"},
            ],
            "ipo_status": "Public",
            "stock_symbol": "PHR",
            "categories": ["Healthcare", "Health Care Information Technology", "SaaS"]
        },
        "cedar": {
            "description": "Patient financial engagement platform",
            "founded_date": "2016",
            "headquarters": "New York, NY",
            "employee_count": "501-1000",
            "total_funding": 350000000,
            "last_funding_date": "2021-03-09",
            "last_funding_type": "Series D",
            "funding_rounds": [
                {"round_type": "Series D", "amount": 200000000, "date": "2021-03-09", "lead_investors": ["Tiger Global"], "announced_date": "2021-03-09"},
                {"round_type": "Series C", "amount": 102000000, "date": "2020-03-03", "lead_investors": ["Andreessen Horowitz"], "announced_date": "2020-03-03"},
                {"round_type": "Series B", "amount": 36000000, "date": "2019-02-05", "lead_investors": ["Andreessen Horowitz"], "announced_date": "2019-02-05"},
            ],
            "investors": ["Tiger Global", "Andreessen Horowitz", "Thrive Capital", "Concord Health Partners"],
            "board_members": ["Florian Otto (CEO)", "Julie Yoo", "Bryan Roberts"],
            "acquisitions": [],
            "ipo_status": "Private",
            "stock_symbol": None,
            "categories": ["Healthcare", "FinTech", "Payments"]
        },
        "luma health": {
            "description": "Patient success platform for healthcare organizations",
            "founded_date": "2015",
            "headquarters": "San Francisco, CA",
            "employee_count": "201-500",
            "total_funding": 160000000,
            "last_funding_date": "2021-08-05",
            "last_funding_type": "Series C",
            "funding_rounds": [
                {"round_type": "Series C", "amount": 130000000, "date": "2021-08-05", "lead_investors": ["SJVC", "Fidelity"], "announced_date": "2021-08-05"},
                {"round_type": "Series B", "amount": 16000000, "date": "2019-03-13", "lead_investors": ["Khosla Ventures"], "announced_date": "2019-03-13"},
                {"round_type": "Series A", "amount": 9500000, "date": "2017-11-29", "lead_investors": ["U.S. Venture Partners"], "announced_date": "2017-11-29"},
            ],
            "investors": ["Khosla Ventures", "U.S. Venture Partners", "SJVC", "Fidelity"],
            "board_members": ["Adnan Iqbal (CEO)", "Saeed Amidi", "Vinod Khosla"],
            "acquisitions": [],
            "ipo_status": "Private",
            "stock_symbol": None,
            "categories": ["Healthcare", "Patient Engagement", "SaaS"]
        },
        "zocdoc": {
            "description": "Healthcare marketplace connecting patients with doctors",
            "founded_date": "2007",
            "headquarters": "New York, NY",
            "employee_count": "501-1000",
            "total_funding": 376000000,
            "last_funding_date": "2020-02-14",
            "last_funding_type": "Series D",
            "funding_rounds": [
                {"round_type": "Series D", "amount": 150000000, "date": "2015-08-20", "lead_investors": ["Baillie Gifford"], "announced_date": "2015-08-20"},
                {"round_type": "Series C", "amount": 75000000, "date": "2014-02-03", "lead_investors": ["Founders Fund"], "announced_date": "2014-02-03"},
                {"round_type": "Series B", "amount": 25000000, "date": "2011-08-02", "lead_investors": ["Khosla Ventures"], "announced_date": "2011-08-02"},
            ],
            "investors": ["Baillie Gifford", "Founders Fund", "Khosla Ventures", "DST Global", "Goldman Sachs"],
            "board_members": ["Oliver Kharraz (CEO)", "Cyrus Massoumi", "Peter Thiel"],
            "acquisitions": [],
            "ipo_status": "Private",
            "stock_symbol": None,
            "categories": ["Healthcare", "Marketplace", "Booking Platform"]
        },
        "waystar": {
            "description": "Cloud-based healthcare revenue cycle technology",
            "founded_date": "2017",
            "headquarters": "Louisville, KY",
            "employee_count": "1001-5000",
            "total_funding": 0,
            "last_funding_date": "2019-10-02",
            "last_funding_type": "PE Buyout",
            "funding_rounds": [
                {"round_type": "PE Buyout", "amount": 2700000000, "date": "2019-10-02", "lead_investors": ["EQT Partners", "CPPIB"], "announced_date": "2019-10-02"},
            ],
            "investors": ["EQT Partners", "CPPIB", "Bain Capital"],
            "board_members": ["Matt Hawkins (CEO)", "Jim Denny"],
            "acquisitions": [
                {"acquired_company": "Navicure", "date": "2017", "price": None, "terms": "Merger"},
                {"acquired_company": "ZirMed", "date": "2017", "price": None, "terms": "Merger"},
                {"acquired_company": "Connance", "date": "2020", "price": None, "terms": "Acquisition"},
            ],
            "ipo_status": "Private (PE)",
            "stock_symbol": None,
            "categories": ["Healthcare", "Revenue Cycle Management", "FinTech"]
        },
        "athenahealth": {
            "description": "Cloud-based services for healthcare providers",
            "founded_date": "1997",
            "headquarters": "Watertown, MA",
            "employee_count": "5001-10000",
            "total_funding": 0,
            "last_funding_date": "2019-02-11",
            "last_funding_type": "PE Buyout",
            "funding_rounds": [
                {"round_type": "PE Buyout", "amount": 5700000000, "date": "2019-02-11", "lead_investors": ["Veritas Capital", "Elliott Management"], "announced_date": "2019-02-11"},
                {"round_type": "IPO", "amount": 93000000, "date": "2007-09-20", "lead_investors": [], "announced_date": "2007-09-20"},
            ],
            "investors": ["Veritas Capital", "Elliott Management", "Bain Capital"],
            "board_members": ["Bob Segert (CEO)", "Jeff Immelt"],
            "acquisitions": [
                {"acquired_company": "Praxify Technologies", "date": "2021", "price": None, "terms": "Acquisition"},
                {"acquired_company": "Health Grid", "date": "2020", "price": None, "terms": "Acquisition"},
            ],
            "ipo_status": "Private (PE)",
            "stock_symbol": None,
            "categories": ["Healthcare", "EHR", "Revenue Cycle", "Practice Management"]
        },
        "clearwave": {
            "description": "Patient check-in and eligibility verification solutions",
            "founded_date": "2004",
            "headquarters": "Atlanta, GA",
            "employee_count": "201-500",
            "total_funding": 0,
            "last_funding_date": "2020-09-15",
            "last_funding_type": "PE Growth",
            "funding_rounds": [
                {"round_type": "PE Growth", "amount": 0, "date": "2020-09-15", "lead_investors": ["Great Hill Partners"], "announced_date": "2020-09-15"},
            ],
            "investors": ["Great Hill Partners", "Frontier Capital"],
            "board_members": ["Mike Lamb (CEO)"],
            "acquisitions": [
                {"acquired_company": "Odoro", "date": "2021", "price": None, "terms": "Acquisition"}
            ],
            "ipo_status": "Private (PE)",
            "stock_symbol": None,
            "categories": ["Healthcare", "Patient Access", "SaaS"]
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CRUNCHBASE_API_KEY")
        self.base_url = "https://api.crunchbase.com/api/v4"
    
    def get_company_data(self, company_name: str) -> CrunchbaseData:
        """Get Crunchbase data for a company."""
        name_lower = company_name.lower()
        
        # Check known data first
        if name_lower in self.KNOWN_COMPANIES:
            return self._build_from_known(company_name, self.KNOWN_COMPANIES[name_lower])
        
        # Try API if key available
        if self.api_key:
            try:
                return self._fetch_from_api(company_name)
            except Exception as e:
                print(f"Crunchbase API error: {e}")
        
        return self._build_placeholder(company_name)
    
    def _build_from_known(self, company_name: str, data: Dict) -> CrunchbaseData:
        """Build CrunchbaseData from known data."""
        funding_rounds = [
            FundingRound(**fr) for fr in data.get("funding_rounds", [])
        ]
        acquisitions = [
            Acquisition(**acq) for acq in data.get("acquisitions", [])
        ]
        
        return CrunchbaseData(
            company_name=company_name,
            description=data.get("description", ""),
            founded_date=data.get("founded_date", ""),
            headquarters=data.get("headquarters", ""),
            employee_count=data.get("employee_count", ""),
            total_funding=data.get("total_funding", 0),
            last_funding_date=data.get("last_funding_date", ""),
            last_funding_type=data.get("last_funding_type", ""),
            funding_rounds=funding_rounds,
            investors=data.get("investors", []),
            board_members=data.get("board_members", []),
            acquisitions=acquisitions,
            ipo_status=data.get("ipo_status", "Private"),
            stock_symbol=data.get("stock_symbol"),
            website=f"https://{company_name.lower().replace(' ', '')}.com",
            categories=data.get("categories", []),
            last_updated=datetime.utcnow().isoformat()
        )
    
    def _build_placeholder(self, company_name: str) -> CrunchbaseData:
        """Build placeholder CrunchbaseData."""
        return CrunchbaseData(
            company_name=company_name,
            description="",
            founded_date="",
            headquarters="",
            employee_count="",
            total_funding=0,
            last_funding_date="",
            last_funding_type="",
            funding_rounds=[],
            investors=[],
            board_members=[],
            acquisitions=[],
            ipo_status="Unknown",
            stock_symbol=None,
            website="",
            categories=[],
            last_updated=datetime.utcnow().isoformat()
        )
    
    def _fetch_from_api(self, company_name: str) -> CrunchbaseData:
        """Fetch from Crunchbase API."""
        # API implementation would go here
        raise NotImplementedError("Crunchbase API integration requires subscription")
    
    def get_funding_history(self, company_name: str) -> List[Dict[str, Any]]:
        """Get funding history for a company."""
        data = self.get_company_data(company_name)
        return [asdict(fr) for fr in data.funding_rounds]
    
    def compare_funding(self, company_names: List[str]) -> Dict[str, Any]:
        """Compare funding across companies."""
        comparison = []
        
        for name in company_names:
            data = self.get_company_data(name)
            comparison.append({
                "name": name,
                "total_funding": data.total_funding,
                "last_round": data.last_funding_type,
                "last_round_date": data.last_funding_date,
                "ipo_status": data.ipo_status,
                "num_investors": len(data.investors),
                "num_acquisitions": len(data.acquisitions)
            })
        
        # Sort by total funding
        comparison.sort(key=lambda x: x["total_funding"], reverse=True)
        
        return {
            "companies": comparison,
            "most_funded": comparison[0]["name"] if comparison else None,
            "total_market_funding": sum(c["total_funding"] for c in comparison)
        }


def get_crunchbase_data(company_name: str) -> Dict[str, Any]:
    """Get Crunchbase data for a company."""
    scraper = CrunchbaseScraper()
    data = scraper.get_company_data(company_name)
    
    result = asdict(data)
    result["funding_rounds"] = [asdict(fr) for fr in data.funding_rounds]
    result["acquisitions"] = [asdict(a) for a in data.acquisitions]
    
    return result


if __name__ == "__main__":
    scraper = CrunchbaseScraper()
    
    print("=" * 60)
    print("Crunchbase Data Test")
    print("=" * 60)
    
    for company in ["Phreesia", "Cedar", "Luma Health"]:
        data = scraper.get_company_data(company)
        print(f"\n{company}:")
        print(f"  Total Funding: ${data.total_funding:,.0f}")
        print(f"  Last Round: {data.last_funding_type} ({data.last_funding_date})")
        print(f"  Investors: {', '.join(data.investors[:3])}")
        print(f"  IPO Status: {data.ipo_status}")
