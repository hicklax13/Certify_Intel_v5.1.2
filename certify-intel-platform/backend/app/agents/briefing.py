"""
Executive briefing generation agent.
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class BriefingAgent:
    """
    AI agent for generating executive-ready intelligence briefings.
    """
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_weekly_briefing(
        self,
        period_start: datetime,
        period_end: datetime,
        changes: List[Dict[str, Any]],
        new_competitors: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        company_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a weekly executive briefing.
        
        Args:
            period_start: Start of the reporting period
            period_end: End of the reporting period
            changes: List of change events detected
            new_competitors: List of newly discovered competitors
            alerts: List of triggered alerts
            company_context: Optional context about Certify Health
        
        Returns:
            Briefing content with markdown and metadata
        """
        context = company_context or {
            "name": "Certify Health",
            "description": "Patient intake, insurance verification, and revenue cycle solutions for healthcare providers",
            "segments": ["ambulatory", "dental", "specialty practices"],
        }
        
        prompt = f"""
You are a senior competitive intelligence analyst preparing a weekly briefing for Certify Health's executive team.

COMPANY CONTEXT:
{json.dumps(context, indent=2)}

REPORTING PERIOD: {period_start.strftime('%B %d')} - {period_end.strftime('%B %d, %Y')}

NEW COMPETITORS DISCOVERED ({len(new_competitors)}):
{json.dumps(new_competitors[:10], indent=2) if new_competitors else "None"}

SIGNIFICANT CHANGES DETECTED ({len(changes)}):
{json.dumps(changes[:15], indent=2) if changes else "None"}

ALERTS TRIGGERED ({len(alerts)}):
{json.dumps(alerts[:10], indent=2) if alerts else "None"}

Generate an executive briefing with the following structure:

# Weekly Competitive Intelligence Briefing
## {period_start.strftime('%B %d')} - {period_end.strftime('%B %d, %Y')}

### Executive Summary
(3-4 sentences capturing the most important developments. Lead with insights, not data.)

### 🔴 Competitive Threats (if any)
(Ranked by urgency. For each: What happened, Why it matters, Recommended action)

### 🟢 Opportunities Identified (if any)
(Market gaps, competitor weaknesses, potential advantages)

### 📊 Market Activity
(Summary of competitive landscape changes, new entrants, etc.)

### 👁️ Watch List
(Emerging signals not yet threats, what would elevate them)

### Metrics Snapshot
- Total Competitors Tracked: [number]
- High-Threat Competitors: [number]
- Changes This Week: [number]
- Open Alerts: [number]

---

WRITING GUIDELINES:
- Write in crisp, direct executive language
- No fluff or filler - every sentence should add value
- Lead with insights and implications, not raw data
- Use specific numbers and competitor names
- Make recommendations actionable
- Keep the total length reasonable (800-1200 words)

Return a JSON object with:
- title: string (briefing title)
- executive_summary: string (just the summary paragraph)
- content_markdown: string (full briefing in markdown)
- threats_count: number
- opportunities_count: number
- key_insights: array of strings (3-5 most important takeaways)
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        result = json.loads(response.choices[0].message.content)
        result["period_start"] = period_start.isoformat()
        result["period_end"] = period_end.isoformat()
        result["generated_at"] = datetime.utcnow().isoformat()
        result["generation_model"] = self.model
        result["briefing_type"] = "weekly"
        
        return result
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_competitor_dossier(
        self,
        competitor: Dict[str, Any],
        claims: List[Dict[str, Any]],
        changes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive dossier for a single competitor.
        
        Args:
            competitor: Competitor information
            claims: All claims about this competitor
            changes: Change history for this competitor
        
        Returns:
            Dossier content with analysis
        """
        prompt = f"""
You are a competitive intelligence analyst creating a comprehensive dossier on a competitor.

COMPETITOR:
{json.dumps(competitor, indent=2)}

INTELLIGENCE (Claims):
{json.dumps(claims[:20], indent=2) if claims else "Limited intelligence available"}

CHANGE HISTORY:
{json.dumps(changes[:10], indent=2) if changes else "No changes tracked yet"}

Generate a competitor dossier with:

# {competitor.get('name', 'Competitor')} - Intelligence Dossier

## Company Overview
(Brief description, market position, size estimates if available)

## Product & Pricing
(What they offer, how they price, notable features)

## Market Positioning
(Target segments, value propositions, how they position vs. us)

## Strengths
(Competitive advantages, what they do well)

## Weaknesses
(Gaps, vulnerabilities, areas where Certify has an advantage)

## Recent Activity
(Notable changes, new releases, strategic moves)

## Threat Assessment
(Overall threat level with justification)

## Recommended Actions
(Specific actions Certify should take)

Return a JSON object with:
- company_name: string
- threat_level: "high" | "medium" | "low" | "watch"
- content_markdown: string (full dossier)
- strengths: array of strings
- weaknesses: array of strings
- recommended_actions: array of strings
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        
        result = json.loads(response.choices[0].message.content)
        result["competitor_id"] = competitor.get("id")
        result["generated_at"] = datetime.utcnow().isoformat()
        
        return result
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_insight(
        self,
        insight_type: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a single strategic insight from data.
        
        Args:
            insight_type: Type of insight (threat, opportunity, market_trend)
            data: Relevant data to analyze
        
        Returns:
            Structured insight with recommendations
        """
        prompts = {
            "threat": """
Analyze this competitive threat and provide:
1. A clear, actionable title (10 words max)
2. A concise summary (2-3 sentences)
3. Impact assessment for Certify Health
4. Recommended defensive actions
5. Urgency rating (critical, high, medium, low)
""",
            "opportunity": """
Analyze this market opportunity and provide:
1. A clear, actionable title (10 words max)
2. A concise summary (2-3 sentences)
3. Potential value for Certify Health
4. Recommended actions to capitalize
5. Effort estimate (low, medium, high)
""",
            "market_trend": """
Analyze this market trend and provide:
1. A clear title describing the trend
2. A concise summary (2-3 sentences)
3. Implications for the competitive landscape
4. What Certify should watch for
5. Confidence level (high, medium, low)
""",
        }
        
        prompt = f"""
You are a strategic analyst for Certify Health.

DATA:
{json.dumps(data, indent=2)}

{prompts.get(insight_type, prompts['market_trend'])}

Return a JSON object with: title, summary, details, severity, recommended_actions (array)
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        
        result = json.loads(response.choices[0].message.content)
        result["insight_type"] = insight_type
        result["generated_at"] = datetime.utcnow().isoformat()
        
        return result
