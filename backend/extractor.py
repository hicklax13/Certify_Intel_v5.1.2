"""
Certify Intel - GPT Data Extraction
Uses OpenAI GPT to extract structured competitor data from scraped content.
"""
import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Run: pip install openai")


@dataclass
class ExtractedData:
    """Structured data extracted from competitor website."""
    
    # Pricing
    pricing_model: Optional[str] = None
    base_price: Optional[str] = None
    price_unit: Optional[str] = None
    
    # Product
    product_categories: Optional[str] = None
    key_features: Optional[str] = None
    integration_partners: Optional[str] = None
    certifications: Optional[str] = None
    
    # Market
    target_segments: Optional[str] = None
    customer_size_focus: Optional[str] = None
    geographic_focus: Optional[str] = None
    customer_count: Optional[str] = None
    key_customers: Optional[str] = None
    
    # Company
    employee_count: Optional[str] = None
    year_founded: Optional[str] = None
    headquarters: Optional[str] = None
    funding_total: Optional[str] = None
    
    # Digital
    recent_launches: Optional[str] = None
    
    # Metadata
    confidence_score: Optional[int] = None
    extraction_notes: Optional[str] = None


class GPTExtractor:
    """Uses GPT to extract structured data from website content."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    def extract_from_content(self, competitor_name: str, content: str, page_type: str = "homepage") -> ExtractedData:
        """Extract structured data from page content using GPT."""
        
        if not self.client:
            return ExtractedData(
                extraction_notes="OpenAI client not available. Set OPENAI_API_KEY environment variable."
            )
        
        # Truncate content if too long
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = self._build_extraction_prompt(competitor_name, content, page_type)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._parse_result(result)
            
        except Exception as e:
            return ExtractedData(
                extraction_notes=f"Extraction failed: {str(e)}"
            )
    
    def _get_system_prompt(self) -> str:
        """System prompt for the extraction agent."""
        return """You are a competitive intelligence analyst specializing in healthcare IT companies.
Your task is to extract structured data from competitor websites.
Be precise and only extract information that is clearly stated.
If information is not available, use null.
For pricing, look for specific numbers, not vague ranges.
For features, focus on product capabilities relevant to patient intake, eligibility verification, payments, and patient engagement.

Always respond with valid JSON matching the requested schema."""

    def _build_extraction_prompt(self, competitor_name: str, content: str, page_type: str) -> str:
        """Build the extraction prompt based on page type."""
        
        base_prompt = f"""Analyze this content from {competitor_name}'s {page_type} page and extract the following information.
Return a JSON object with these fields (use null if not found):

{{
    "pricing_model": "How they charge (e.g., 'Per Visit', 'Per Provider', 'Per Location', 'Subscription', 'Custom')",
    "base_price": "Starting price with currency symbol (e.g., '$3.00', '$199/month')",
    "price_unit": "Unit of pricing (e.g., 'per visit', 'per provider/month')",
    "product_categories": "Product types separated by semicolons (e.g., 'Patient Intake; Payments; Scheduling')",
    "key_features": "Main features, comma-separated",
    "integration_partners": "EHR/PM systems they integrate with, semicolon-separated",
    "certifications": "Security certifications (e.g., 'HIPAA; SOC2; HITRUST')",
    "target_segments": "Customer segments (e.g., 'Health Systems; Specialty Practices')",
    "customer_size_focus": "Practice size focus (e.g., 'Small (1-15)', 'Medium (15-50)', 'Large (50+)')",
    "geographic_focus": "Geographic markets",
    "customer_count": "Number of customers if mentioned",
    "key_customers": "Notable customer names if mentioned",
    "employee_count": "Employee count if mentioned",
    "year_founded": "Year company was founded",
    "headquarters": "Company headquarters location",
    "funding_total": "Total funding raised if mentioned",
    "recent_launches": "Recent product announcements",
    "confidence_score": "Your confidence in the extraction (1-100)",
    "extraction_notes": "Any notes about the extraction or data quality"
}}

CONTENT TO ANALYZE:
{content}"""
        
        return base_prompt
    
    def _parse_result(self, result: Dict[str, Any]) -> ExtractedData:
        """Parse GPT response into ExtractedData."""
        return ExtractedData(
            pricing_model=result.get("pricing_model"),
            base_price=result.get("base_price"),
            price_unit=result.get("price_unit"),
            product_categories=result.get("product_categories"),
            key_features=result.get("key_features"),
            integration_partners=result.get("integration_partners"),
            certifications=result.get("certifications"),
            target_segments=result.get("target_segments"),
            customer_size_focus=result.get("customer_size_focus"),
            geographic_focus=result.get("geographic_focus"),
            customer_count=result.get("customer_count"),
            key_customers=result.get("key_customers"),
            employee_count=result.get("employee_count"),
            year_founded=result.get("year_founded"),
            headquarters=result.get("headquarters"),
            funding_total=result.get("funding_total"),
            recent_launches=result.get("recent_launches"),
            confidence_score=result.get("confidence_score"),
            extraction_notes=result.get("extraction_notes")
        )
    
    def merge_extractions(self, extractions: List[ExtractedData]) -> ExtractedData:
        """Merge multiple extractions (from different pages) into one."""
        if not extractions:
            return ExtractedData()
        
        merged = ExtractedData()
        
        # For each field, take the first non-None value
        for extraction in extractions:
            for field in ExtractedData.__dataclass_fields__:
                if getattr(merged, field) is None:
                    value = getattr(extraction, field)
                    if value is not None:
                        setattr(merged, field, value)
        
        return merged


# Convenience function
def extract_competitor_data(competitor_name: str, content: str, page_type: str = "homepage") -> ExtractedData:
    """Extract competitor data from content."""
    extractor = GPTExtractor()
    return extractor.extract_from_content(competitor_name, content, page_type)


# Test function
def test_extraction():
    """Test the extractor with sample content."""
    sample_content = """
    Phreesia - Patient Intake Solutions
    
    Pricing: Starting at $3 per patient visit
    
    Features:
    - Digital patient intake
    - Insurance eligibility verification
    - Patient payments and collections
    - Appointment reminders
    - Patient surveys
    
    Integrations: Epic, Cerner, Allscripts, athenahealth, eClinicalWorks
    
    Trusted by over 3,000 healthcare organizations
    
    HIPAA compliant, SOC 2 certified, HITRUST certified
    
    Founded in 2005, headquartered in Raleigh, NC
    """
    
    extractor = GPTExtractor()
    result = extractor.extract_from_content("Phreesia", sample_content, "homepage")
    
    print("Extraction Result:")
    for field, value in asdict(result).items():
        if value:
            print(f"  {field}: {value}")


if __name__ == "__main__":
    test_extraction()
