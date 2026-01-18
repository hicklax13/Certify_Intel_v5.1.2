"""
LLM-powered extraction agent for structured data extraction from evidence.
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class ExtractionAgent:
    """
    AI agent for extracting structured claims from evidence text.
    Uses OpenAI GPT-4 with structured output schemas.
    """
    
    PRICING_SCHEMA = {
        "type": "object",
        "properties": {
            "pricing_model": {
                "type": "string",
                "enum": ["per_user", "per_facility", "flat", "usage_based", "custom", "unknown"]
            },
            "base_price": {"type": ["number", "null"]},
            "price_unit": {"type": "string"},
            "currency": {"type": "string", "default": "USD"},
            "tiers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": ["number", "null"]},
                        "features": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "enterprise_pricing": {"type": "string"},
            "free_tier": {"type": "boolean"},
            "evidence_quote": {"type": "string"},
            "extraction_reasoning": {"type": "string"}
        },
        "required": ["pricing_model", "extraction_reasoning"]
    }
    
    FEATURE_SCHEMA = {
        "type": "object",
        "properties": {
            "feature_name": {"type": "string"},
            "feature_category": {
                "type": "string",
                "enum": ["core", "integration", "security", "compliance", "analytics", "automation", "other"]
            },
            "description": {"type": "string"},
            "is_premium": {"type": "boolean"},
            "evidence_quote": {"type": "string"},
            "extraction_reasoning": {"type": "string"}
        },
        "required": ["feature_name", "feature_category", "extraction_reasoning"]
    }
    
    POSITIONING_SCHEMA = {
        "type": "object",
        "properties": {
            "target_segments": {"type": "array", "items": {"type": "string"}},
            "value_propositions": {"type": "array", "items": {"type": "string"}},
            "differentiators": {"type": "array", "items": {"type": "string"}},
            "tone": {
                "type": "string",
                "enum": ["enterprise", "startup", "professional", "friendly", "technical"]
            },
            "evidence_quote": {"type": "string"},
            "extraction_reasoning": {"type": "string"}
        },
        "required": ["target_segments", "value_propositions", "extraction_reasoning"]
    }
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def extract_pricing(self, content: str, url: str, competitor_name: str) -> Dict[str, Any]:
        """Extract pricing information from webpage content."""
        prompt = f"""
You are an expert competitive intelligence analyst. Extract pricing information from the following webpage content.

COMPETITOR: {competitor_name}
URL: {url}

CONTENT:
{content[:8000]}

INSTRUCTIONS:
1. Identify any pricing information mentioned
2. Extract the pricing model (per-user, per-facility, flat rate, etc.)
3. Extract specific prices if mentioned
4. Note any tiers or plans
5. If pricing is not clearly stated, set pricing_model to "unknown" and explain in reasoning
6. Always include the exact quote that supports your extraction
7. Be conservative - only extract what is clearly stated

Return a JSON object matching the schema.
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        
        result = json.loads(response.choices[0].message.content)
        result["source_url"] = url
        result["extracted_at"] = datetime.utcnow().isoformat()
        result["extraction_model"] = self.model
        
        # Calculate confidence based on extraction quality
        result["confidence"] = self._calculate_confidence(result, "pricing")
        
        return result
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def extract_features(self, content: str, url: str, competitor_name: str) -> list[Dict[str, Any]]:
        """Extract product features from webpage content."""
        prompt = f"""
You are an expert competitive intelligence analyst. Extract product features from the following webpage content.

COMPETITOR: {competitor_name}
URL: {url}

CONTENT:
{content[:8000]}

INSTRUCTIONS:
1. Identify all product features mentioned
2. Categorize each feature (core, integration, security, compliance, analytics, automation, other)
3. Note if features are premium/paid add-ons
4. Include evidence quotes for each feature
5. Be thorough but accurate - only extract actual features, not marketing fluff

Return a JSON object with a "features" array containing feature objects.
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        
        result = json.loads(response.choices[0].message.content)
        features = result.get("features", [])
        
        # Add metadata to each feature
        for feature in features:
            feature["source_url"] = url
            feature["extracted_at"] = datetime.utcnow().isoformat()
            feature["extraction_model"] = self.model
            feature["confidence"] = self._calculate_confidence(feature, "feature")
        
        return features
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def extract_positioning(self, content: str, url: str, competitor_name: str) -> Dict[str, Any]:
        """Extract market positioning from webpage content."""
        prompt = f"""
You are an expert competitive intelligence analyst. Analyze the market positioning from the following webpage content.

COMPETITOR: {competitor_name}
URL: {url}

CONTENT:
{content[:8000]}

INSTRUCTIONS:
1. Identify target customer segments (enterprise, mid-market, SMB, specific verticals)
2. Extract key value propositions
3. Identify stated differentiators vs competitors
4. Analyze the overall tone/positioning (enterprise-focused, startup-friendly, etc.)
5. Include evidence quotes supporting your analysis
6. Be analytical and precise

Return a JSON object matching the schema.
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        
        result = json.loads(response.choices[0].message.content)
        result["source_url"] = url
        result["extracted_at"] = datetime.utcnow().isoformat()
        result["extraction_model"] = self.model
        result["confidence"] = self._calculate_confidence(result, "positioning")
        
        return result
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze_change(
        self, 
        previous_content: str, 
        current_content: str, 
        url: str, 
        competitor_name: str
    ) -> Dict[str, Any]:
        """Analyze changes between two versions of content."""
        prompt = f"""
You are an expert competitive intelligence analyst. Analyze the changes between two versions of a competitor's webpage.

COMPETITOR: {competitor_name}
URL: {url}

PREVIOUS VERSION:
{previous_content[:4000]}

CURRENT VERSION:
{current_content[:4000]}

INSTRUCTIONS:
1. Identify significant changes (ignore minor typos or formatting)
2. Classify the change type: pricing_change, feature_added, feature_removed, positioning_shift, leadership_change, integration_added, other
3. Assess the severity: high (competitive threat), medium (notable), low (minor), info (informational)
4. Explain the business impact for Certify Health
5. Recommend actions if appropriate

Return a JSON object with:
- has_significant_change: boolean
- change_type: string
- severity: string
- change_summary: string (1-2 sentences)
- impact_assessment: string (2-3 sentences)
- recommended_action: string (optional)
- evidence_quote_before: string
- evidence_quote_after: string
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        
        result = json.loads(response.choices[0].message.content)
        result["analyzed_at"] = datetime.utcnow().isoformat()
        result["analysis_model"] = self.model
        
        return result
    
    def _calculate_confidence(self, extraction: Dict[str, Any], claim_type: str) -> float:
        """Calculate confidence score based on extraction quality."""
        confidence = 0.5  # Base confidence
        
        # Has evidence quote
        if extraction.get("evidence_quote"):
            confidence += 0.2
        
        # Has reasoning
        if extraction.get("extraction_reasoning"):
            confidence += 0.1
        
        # Type-specific adjustments
        if claim_type == "pricing":
            if extraction.get("base_price") is not None:
                confidence += 0.15
            if extraction.get("pricing_model") and extraction["pricing_model"] != "unknown":
                confidence += 0.05
        
        elif claim_type == "feature":
            if extraction.get("description"):
                confidence += 0.1
            if extraction.get("feature_category") and extraction["feature_category"] != "other":
                confidence += 0.1
        
        elif claim_type == "positioning":
            if extraction.get("target_segments") and len(extraction["target_segments"]) > 0:
                confidence += 0.1
            if extraction.get("value_propositions") and len(extraction["value_propositions"]) > 0:
                confidence += 0.1
        
        return min(confidence, 1.0)
