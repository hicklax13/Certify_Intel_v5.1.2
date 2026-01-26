"""
Certify Intel - AI Deep Research Integration (v5.0.6)
Provides deep research capabilities using ChatGPT and Gemini.

Features:
- ChatGPT Deep Research: Comprehensive multi-source research using GPT-4
- Gemini Deep Research: Real-time grounded research using Google Search
- Battlecard Report Generation: One-click competitive reports

NEWS-4B: ChatGPT Deep Research integration
NEWS-4C: Gemini Deep Research integration
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

# Check for available providers
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed. Run: pip install openai")

try:
    from gemini_provider import GeminiProvider
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Gemini provider not available")


@dataclass
class ResearchResult:
    """Result of a deep research request."""
    competitor_name: str
    research_type: str
    content: str
    sections: Dict[str, str]
    sources_used: List[str]
    provider: str
    model: str
    timestamp: str
    cost_estimate: float
    latency_ms: float
    success: bool
    error: Optional[str] = None


class ChatGPTResearcher:
    """
    ChatGPT Deep Research for competitive intelligence.

    Uses GPT-4 with structured prompts to generate comprehensive
    competitor research reports.
    """

    # Research templates
    RESEARCH_TEMPLATES = {
        "battlecard": """Generate a comprehensive sales battlecard for {competitor_name}.

Structure the report with these sections:

## COMPANY OVERVIEW
- Brief description
- Founded, headquarters, employee count
- Key executives
- Recent news/developments

## PRODUCTS & SERVICES
- Main product offerings
- Key features and capabilities
- Target market segments
- Pricing model (if known)

## STRENGTHS
- 3-5 key competitive strengths
- What they do well

## WEAKNESSES
- 3-5 potential weaknesses
- Where we can compete

## COMPETITIVE POSITIONING
- How they position against alternatives
- Key messaging and claims

## OBJECTION HANDLING
For each common objection, provide a response:
1. "They're more established" - [response]
2. "They have more features" - [response]
3. "They're cheaper" - [response]

## KEY DIFFERENTIATORS
- What makes them unique
- What makes US better

## RECOMMENDED APPROACH
- Best strategy for competing
- Key talking points

Provide specific, actionable intelligence based on available information.
""",
        "market_analysis": """Analyze {competitor_name}'s market position:

## MARKET POSITION
- Current market standing
- Market share estimate
- Growth trajectory

## TARGET CUSTOMERS
- Primary customer segments
- Ideal customer profile
- Key verticals

## GO-TO-MARKET STRATEGY
- Sales approach
- Marketing channels
- Partnership strategy

## COMPETITIVE LANDSCAPE
- Key competitors
- Positioning vs. alternatives

## SWOT ANALYSIS
- Strengths
- Weaknesses
- Opportunities
- Threats

## MARKET TRENDS
- Industry trends affecting them
- How they're responding
""",
        "product_deep_dive": """Deep dive into {competitor_name}'s product:

## PRODUCT OVERVIEW
- Product name(s) and description
- Core functionality
- User interface/experience

## FEATURE ANALYSIS
- Key features (list with descriptions)
- Unique capabilities
- Feature gaps

## TECHNICAL ARCHITECTURE
- Technology stack (if known)
- Integration capabilities
- Security/compliance

## PRICING
- Pricing model
- Price points
- Value proposition

## CUSTOMER FEEDBACK
- Common praise
- Common complaints
- Feature requests

## PRODUCT ROADMAP
- Recent releases
- Announced future features
- Strategic direction
""",
        "quick_summary": """Provide a quick competitive summary for {competitor_name}:

## AT A GLANCE
- One sentence description
- Key metric: customers/revenue/employees
- Threat level: High/Medium/Low

## TOP 3 STRENGTHS
1.
2.
3.

## TOP 3 WEAKNESSES
1.
2.
3.

## KEY TAKEAWAY
One paragraph on how to compete with them.
"""
    }

    def __init__(self):
        """Initialize ChatGPT researcher."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.client = None

        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"ChatGPT researcher initialized with model: {self.model}")

    @property
    def is_available(self) -> bool:
        """Check if researcher is available."""
        return self.client is not None

    def research(
        self,
        competitor_name: str,
        research_type: str = "battlecard",
        additional_context: Optional[str] = None,
    ) -> ResearchResult:
        """
        Generate deep research report for a competitor.

        Args:
            competitor_name: Name of the competitor
            research_type: Type of research (battlecard, market_analysis, product_deep_dive, quick_summary)
            additional_context: Additional context to include

        Returns:
            ResearchResult with the generated report
        """
        if not self.is_available:
            return ResearchResult(
                competitor_name=competitor_name,
                research_type=research_type,
                content="",
                sections={},
                sources_used=[],
                provider="chatgpt",
                model=self.model,
                timestamp=datetime.utcnow().isoformat(),
                cost_estimate=0.0,
                latency_ms=0.0,
                success=False,
                error="ChatGPT not available. Configure OPENAI_API_KEY."
            )

        start_time = datetime.now()

        try:
            # Get template
            template = self.RESEARCH_TEMPLATES.get(research_type, self.RESEARCH_TEMPLATES["battlecard"])
            prompt = template.format(competitor_name=competitor_name)

            if additional_context:
                prompt += f"\n\nADDITIONAL CONTEXT:\n{additional_context}"

            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior competitive intelligence analyst specializing in healthcare technology. Provide detailed, accurate, and actionable competitive intelligence. Use markdown formatting for structure."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
            )

            latency = (datetime.now() - start_time).total_seconds() * 1000
            content = response.choices[0].message.content

            # Parse sections from markdown
            sections = self._parse_sections(content)

            # Estimate cost
            tokens_used = response.usage.total_tokens if response.usage else 0
            cost_estimate = self._estimate_cost(tokens_used)

            return ResearchResult(
                competitor_name=competitor_name,
                research_type=research_type,
                content=content,
                sections=sections,
                sources_used=["ChatGPT Knowledge Base"],
                provider="chatgpt",
                model=self.model,
                timestamp=datetime.utcnow().isoformat(),
                cost_estimate=cost_estimate,
                latency_ms=latency,
                success=True
            )

        except Exception as e:
            latency = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"ChatGPT research failed: {e}")
            return ResearchResult(
                competitor_name=competitor_name,
                research_type=research_type,
                content="",
                sections={},
                sources_used=[],
                provider="chatgpt",
                model=self.model,
                timestamp=datetime.utcnow().isoformat(),
                cost_estimate=0.0,
                latency_ms=latency,
                success=False,
                error=str(e)
            )

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown sections from content."""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on model and tokens."""
        # GPT-4o pricing (approximate)
        pricing = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        }
        model_pricing = pricing.get(self.model, pricing["gpt-4o-mini"])
        # Rough 50/50 split between input and output
        return (tokens / 2 / 1_000_000) * (model_pricing["input"] + model_pricing["output"])


class GeminiResearcher:
    """
    Gemini Deep Research for competitive intelligence.

    Uses Gemini with real-time Google Search grounding for
    current, factual information about competitors.
    """

    def __init__(self):
        """Initialize Gemini researcher."""
        self.provider = None
        if GEMINI_AVAILABLE:
            self.provider = GeminiProvider()
            if self.provider.is_available:
                logger.info("Gemini researcher initialized")

    @property
    def is_available(self) -> bool:
        """Check if researcher is available."""
        return self.provider is not None and self.provider.is_available

    def research(
        self,
        competitor_name: str,
        research_type: str = "battlecard",
        additional_context: Optional[str] = None,
    ) -> ResearchResult:
        """
        Generate deep research report using Gemini with grounding.

        Args:
            competitor_name: Name of the competitor
            research_type: Type of research
            additional_context: Additional context to include

        Returns:
            ResearchResult with the generated report
        """
        if not self.is_available:
            return ResearchResult(
                competitor_name=competitor_name,
                research_type=research_type,
                content="",
                sections={},
                sources_used=[],
                provider="gemini",
                model="",
                timestamp=datetime.utcnow().isoformat(),
                cost_estimate=0.0,
                latency_ms=0.0,
                success=False,
                error="Gemini not available. Configure GOOGLE_AI_API_KEY."
            )

        start_time = datetime.now()

        try:
            # Use research_competitor for comprehensive research
            result = self.provider.research_competitor(
                competitor_name=competitor_name,
                research_areas=self._get_research_areas(research_type)
            )

            latency = (datetime.now() - start_time).total_seconds() * 1000

            # Format content from sections
            content = self._format_research_content(competitor_name, result, research_type)
            sections = result.get("sections", {})

            return ResearchResult(
                competitor_name=competitor_name,
                research_type=research_type,
                content=content,
                sections=sections,
                sources_used=["Google Search", "Gemini Grounding"],
                provider="gemini",
                model="gemini-2.0-flash",
                timestamp=datetime.utcnow().isoformat(),
                cost_estimate=0.01,  # Rough estimate
                latency_ms=latency,
                success=True
            )

        except Exception as e:
            latency = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"Gemini research failed: {e}")
            return ResearchResult(
                competitor_name=competitor_name,
                research_type=research_type,
                content="",
                sections={},
                sources_used=[],
                provider="gemini",
                model="gemini-2.0-flash",
                timestamp=datetime.utcnow().isoformat(),
                cost_estimate=0.0,
                latency_ms=latency,
                success=False,
                error=str(e)
            )

    def _get_research_areas(self, research_type: str) -> List[str]:
        """Get research areas for a given research type."""
        areas = {
            "battlecard": ["overview", "products", "pricing", "news", "customers", "competitors"],
            "market_analysis": ["overview", "customers", "competitors", "financials"],
            "product_deep_dive": ["products", "technology", "pricing", "partnerships"],
            "quick_summary": ["overview", "products", "news"],
        }
        return areas.get(research_type, areas["battlecard"])

    def _format_research_content(
        self,
        competitor_name: str,
        result: Dict[str, Any],
        research_type: str
    ) -> str:
        """Format research results into markdown content."""
        sections = result.get("sections", {})

        content = f"# {competitor_name} - {research_type.replace('_', ' ').title()}\n\n"
        content += f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n"
        content += "*Source: Real-time Google Search via Gemini*\n\n"

        for section_name, section_content in sections.items():
            content += f"## {section_name.upper()}\n\n"
            content += f"{section_content}\n\n"

        return content


class DeepResearchManager:
    """
    Unified manager for deep research across providers.

    Automatically selects the best provider based on availability
    and research type.
    """

    def __init__(self):
        """Initialize research manager."""
        self.chatgpt = ChatGPTResearcher()
        self.gemini = GeminiResearcher()

    def research(
        self,
        competitor_name: str,
        research_type: str = "battlecard",
        provider: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> ResearchResult:
        """
        Generate deep research report.

        Args:
            competitor_name: Name of the competitor
            research_type: Type of research
            provider: Preferred provider ("chatgpt", "gemini", or None for auto)
            additional_context: Additional context

        Returns:
            ResearchResult from the selected provider
        """
        # Select provider
        if provider == "chatgpt" and self.chatgpt.is_available:
            return self.chatgpt.research(competitor_name, research_type, additional_context)
        elif provider == "gemini" and self.gemini.is_available:
            return self.gemini.research(competitor_name, research_type, additional_context)
        elif provider is None:
            # Auto-select based on research type
            # Gemini is better for real-time data, ChatGPT for comprehensive analysis
            if research_type in ["quick_summary", "news"]:
                if self.gemini.is_available:
                    return self.gemini.research(competitor_name, research_type, additional_context)
            if self.chatgpt.is_available:
                return self.chatgpt.research(competitor_name, research_type, additional_context)
            if self.gemini.is_available:
                return self.gemini.research(competitor_name, research_type, additional_context)

        return ResearchResult(
            competitor_name=competitor_name,
            research_type=research_type,
            content="",
            sections={},
            sources_used=[],
            provider="none",
            model="none",
            timestamp=datetime.utcnow().isoformat(),
            cost_estimate=0.0,
            latency_ms=0.0,
            success=False,
            error="No AI provider available. Configure OPENAI_API_KEY or GOOGLE_AI_API_KEY."
        )

    def get_available_providers(self) -> Dict[str, bool]:
        """Get availability status of all providers."""
        return {
            "chatgpt": self.chatgpt.is_available,
            "gemini": self.gemini.is_available,
        }

    def get_research_types(self) -> List[Dict[str, str]]:
        """Get available research types with descriptions."""
        return [
            {"type": "battlecard", "name": "Sales Battlecard", "description": "Comprehensive competitive analysis for sales"},
            {"type": "market_analysis", "name": "Market Analysis", "description": "Market position and competitive landscape"},
            {"type": "product_deep_dive", "name": "Product Deep Dive", "description": "Detailed product analysis"},
            {"type": "quick_summary", "name": "Quick Summary", "description": "Brief competitive overview"},
        ]


# ============== CONVENIENCE FUNCTIONS ==============

def get_research_manager() -> DeepResearchManager:
    """Get the deep research manager instance."""
    return DeepResearchManager()


def generate_battlecard(
    competitor_name: str,
    provider: Optional[str] = None,
    additional_context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a sales battlecard for a competitor.

    Args:
        competitor_name: Name of the competitor
        provider: Preferred provider (chatgpt/gemini)
        additional_context: Additional context to include

    Returns:
        Dictionary with battlecard content
    """
    manager = get_research_manager()
    result = manager.research(
        competitor_name=competitor_name,
        research_type="battlecard",
        provider=provider,
        additional_context=additional_context
    )
    return asdict(result)


def generate_quick_summary(competitor_name: str) -> Dict[str, Any]:
    """Generate a quick competitive summary."""
    manager = get_research_manager()
    result = manager.research(
        competitor_name=competitor_name,
        research_type="quick_summary"
    )
    return asdict(result)


# ============== TEST FUNCTION ==============

def test_ai_research():
    """Test the AI research module."""
    print("Testing AI Deep Research...")
    print("-" * 50)

    manager = get_research_manager()
    providers = manager.get_available_providers()

    print(f"ChatGPT available: {providers['chatgpt']}")
    print(f"Gemini available: {providers['gemini']}")

    if not any(providers.values()):
        print("\nNo AI providers configured. Set OPENAI_API_KEY or GOOGLE_AI_API_KEY.")
        return

    print("\nAvailable research types:")
    for rt in manager.get_research_types():
        print(f"  - {rt['type']}: {rt['description']}")

    # Test with available provider
    print("\nGenerating quick summary for 'Phreesia'...")
    result = manager.research("Phreesia", "quick_summary")

    if result.success:
        print(f"Provider: {result.provider}")
        print(f"Latency: {result.latency_ms:.0f}ms")
        print(f"Cost: ${result.cost_estimate:.4f}")
        print(f"\nContent preview:\n{result.content[:500]}...")
    else:
        print(f"Error: {result.error}")

    print("\n" + "-" * 50)
    print("AI Deep Research test complete!")


if __name__ == "__main__":
    test_ai_research()
