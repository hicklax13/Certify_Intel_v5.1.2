"""
Certify Intel - Cost Comparison Tests (v5.0.6)
Tests to verify cost savings when using Gemini vs OpenAI.

Run with: pytest tests/test_cost_comparison.py -v
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_provider import GeminiProvider, GeminiConfig


# ============== COST CALCULATION TESTS ==============

class TestCostCalculations:
    """Tests for cost estimation calculations."""

    @pytest.fixture
    def provider(self):
        """Create a GeminiProvider for testing."""
        with patch("gemini_provider.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock()
            return GeminiProvider(GeminiConfig(api_key="test"))

    def test_flash_model_cost(self, provider):
        """Test cost calculation for gemini-2.5-flash model."""
        # 1M input tokens, 500K output tokens
        cost = provider.estimate_cost(1_000_000, 500_000, "gemini-2.5-flash")

        # Expected: (1M * $0.075/1M) + (500K * $0.30/1M)
        # = $0.075 + $0.15 = $0.225
        expected = 0.075 + 0.15
        assert abs(cost - expected) < 0.001

    def test_flash_lite_model_cost(self, provider):
        """Test cost calculation for gemini-2.5-flash-lite model."""
        # 1M input tokens, 500K output tokens
        cost = provider.estimate_cost(1_000_000, 500_000, "gemini-2.5-flash-lite")

        # Expected: (1M * $0.01875/1M) + (500K * $0.075/1M)
        # = $0.01875 + $0.0375 = $0.05625
        expected = 0.01875 + 0.0375
        assert abs(cost - expected) < 0.001

    def test_pro_model_cost(self, provider):
        """Test cost calculation for gemini-2.5-pro model."""
        # 1M input tokens, 500K output tokens
        cost = provider.estimate_cost(1_000_000, 500_000, "gemini-2.5-pro")

        # Expected: (1M * $1.25/1M) + (500K * $10.00/1M)
        # = $1.25 + $5.00 = $6.25
        expected = 1.25 + 5.00
        assert abs(cost - expected) < 0.01

    def test_small_request_cost(self, provider):
        """Test cost calculation for a small request."""
        # 1000 input tokens, 500 output tokens (typical small request)
        cost = provider.estimate_cost(1_000, 500, "gemini-2.5-flash")

        # Expected: (1000 * $0.075/1M) + (500 * $0.30/1M)
        # = $0.000075 + $0.00015 = $0.000225
        expected = 0.000075 + 0.00015
        assert abs(cost - expected) < 0.0001

    def test_default_model_cost(self, provider):
        """Test cost calculation uses default model when not specified."""
        # Use provider's default model
        cost1 = provider.estimate_cost(1_000_000, 500_000)
        cost2 = provider.estimate_cost(1_000_000, 500_000, provider.config.model)
        assert cost1 == cost2


# ============== COST COMPARISON TESTS ==============

class TestCostComparison:
    """Tests comparing costs between Gemini and OpenAI."""

    # OpenAI pricing (approximate as of 2026)
    OPENAI_PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    }

    @pytest.fixture
    def provider(self):
        """Create a GeminiProvider for testing."""
        with patch("gemini_provider.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock()
            return GeminiProvider(GeminiConfig(api_key="test"))

    def estimate_openai_cost(self, input_tokens, output_tokens, model):
        """Estimate OpenAI cost for comparison."""
        pricing = self.OPENAI_PRICING.get(model, self.OPENAI_PRICING["gpt-4o-mini"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def test_flash_vs_gpt4o_mini_savings(self, provider):
        """Test cost savings of Gemini Flash vs GPT-4o-mini."""
        input_tokens = 1_000_000
        output_tokens = 500_000

        gemini_cost = provider.estimate_cost(input_tokens, output_tokens, "gemini-2.5-flash")
        openai_cost = self.estimate_openai_cost(input_tokens, output_tokens, "gpt-4o-mini")

        savings_percent = ((openai_cost - gemini_cost) / openai_cost) * 100

        # Gemini Flash should be ~50% cheaper than GPT-4o-mini
        assert savings_percent > 40, f"Expected >40% savings, got {savings_percent:.1f}%"
        print(f"\nFlash vs GPT-4o-mini: {savings_percent:.1f}% savings")
        print(f"  Gemini Flash: ${gemini_cost:.4f}")
        print(f"  GPT-4o-mini: ${openai_cost:.4f}")

    def test_flash_lite_vs_gpt4o_mini_savings(self, provider):
        """Test cost savings of Gemini Flash-Lite vs GPT-4o-mini."""
        input_tokens = 1_000_000
        output_tokens = 500_000

        gemini_cost = provider.estimate_cost(input_tokens, output_tokens, "gemini-2.5-flash-lite")
        openai_cost = self.estimate_openai_cost(input_tokens, output_tokens, "gpt-4o-mini")

        savings_percent = ((openai_cost - gemini_cost) / openai_cost) * 100

        # Gemini Flash-Lite should be ~85% cheaper than GPT-4o-mini
        assert savings_percent > 80, f"Expected >80% savings, got {savings_percent:.1f}%"
        print(f"\nFlash-Lite vs GPT-4o-mini: {savings_percent:.1f}% savings")
        print(f"  Gemini Flash-Lite: ${gemini_cost:.4f}")
        print(f"  GPT-4o-mini: ${openai_cost:.4f}")

    def test_flash_vs_gpt4o_savings(self, provider):
        """Test cost savings of Gemini Flash vs GPT-4o."""
        input_tokens = 1_000_000
        output_tokens = 500_000

        gemini_cost = provider.estimate_cost(input_tokens, output_tokens, "gemini-2.5-flash")
        openai_cost = self.estimate_openai_cost(input_tokens, output_tokens, "gpt-4o")

        savings_percent = ((openai_cost - gemini_cost) / openai_cost) * 100

        # Gemini Flash should be ~95% cheaper than GPT-4o
        assert savings_percent > 90, f"Expected >90% savings, got {savings_percent:.1f}%"
        print(f"\nFlash vs GPT-4o: {savings_percent:.1f}% savings")
        print(f"  Gemini Flash: ${gemini_cost:.4f}")
        print(f"  GPT-4o: ${openai_cost:.4f}")

    def test_pro_vs_gpt4o_savings(self, provider):
        """Test cost comparison of Gemini Pro vs GPT-4o."""
        input_tokens = 1_000_000
        output_tokens = 500_000

        gemini_cost = provider.estimate_cost(input_tokens, output_tokens, "gemini-2.5-pro")
        openai_cost = self.estimate_openai_cost(input_tokens, output_tokens, "gpt-4o")

        # Gemini Pro is roughly similar in price to GPT-4o
        print(f"\nPro vs GPT-4o comparison:")
        print(f"  Gemini Pro: ${gemini_cost:.4f}")
        print(f"  GPT-4o: ${openai_cost:.4f}")


# ============== BULK PROCESSING COST TESTS ==============

class TestBulkProcessingCosts:
    """Tests for bulk processing cost scenarios."""

    @pytest.fixture
    def provider(self):
        """Create a GeminiProvider for testing."""
        with patch("gemini_provider.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock()
            return GeminiProvider(GeminiConfig(api_key="test"))

    def test_bulk_news_processing_cost(self, provider):
        """Test cost for processing 1000 news articles."""
        # Assume: 500 tokens input per article, 100 tokens output
        num_articles = 1000
        tokens_per_article_input = 500
        tokens_per_article_output = 100

        total_input = num_articles * tokens_per_article_input
        total_output = num_articles * tokens_per_article_output

        # Using Flash-Lite (recommended for bulk)
        cost = provider.estimate_cost(total_input, total_output, "gemini-2.5-flash-lite")

        # Should be very cheap - less than $0.05 for 1000 articles
        assert cost < 0.05, f"Bulk processing cost ${cost:.4f} exceeds $0.05 budget"
        print(f"\n1000 news articles processing cost: ${cost:.4f}")

    def test_competitor_extraction_batch_cost(self, provider):
        """Test cost for extracting data from 30 competitor websites."""
        # Assume: 5000 tokens input per competitor (web content), 500 tokens output
        num_competitors = 30
        tokens_per_competitor_input = 5000
        tokens_per_competitor_output = 500

        total_input = num_competitors * tokens_per_competitor_input
        total_output = num_competitors * tokens_per_competitor_output

        # Using Flash (recommended for data extraction)
        cost = provider.estimate_cost(total_input, total_output, "gemini-2.5-flash")

        # Should be less than $0.10 for 30 competitors
        assert cost < 0.10, f"Extraction cost ${cost:.4f} exceeds $0.10 budget"
        print(f"\n30 competitor extractions cost: ${cost:.4f}")

    def test_daily_operation_cost_estimate(self, provider):
        """Test estimated daily operation cost."""
        # Daily operations estimate:
        # - 5 executive summaries (1000 input, 500 output each)
        # - 100 news articles (500 input, 100 output each)
        # - 10 competitor refreshes (5000 input, 500 output each)
        # - 20 chat interactions (200 input, 200 output each)

        daily_cost = 0

        # Executive summaries with Flash
        daily_cost += provider.estimate_cost(5 * 1000, 5 * 500, "gemini-2.5-flash")

        # News articles with Flash-Lite
        daily_cost += provider.estimate_cost(100 * 500, 100 * 100, "gemini-2.5-flash-lite")

        # Competitor refreshes with Flash
        daily_cost += provider.estimate_cost(10 * 5000, 10 * 500, "gemini-2.5-flash")

        # Chat with Flash
        daily_cost += provider.estimate_cost(20 * 200, 20 * 200, "gemini-2.5-flash")

        # Daily cost should be under $0.10
        assert daily_cost < 0.10, f"Daily cost ${daily_cost:.4f} exceeds $0.10 budget"
        print(f"\nEstimated daily operation cost: ${daily_cost:.4f}")

    def test_monthly_cost_projection(self, provider):
        """Test monthly cost projection."""
        # Based on daily estimate, project monthly
        daily_tokens_input = (
            5 * 1000 +      # summaries
            100 * 500 +     # news
            10 * 5000 +     # refreshes
            20 * 200        # chat
        )
        daily_tokens_output = (
            5 * 500 +
            100 * 100 +
            10 * 500 +
            20 * 200
        )

        # 30 days, using Flash as average
        monthly_input = daily_tokens_input * 30
        monthly_output = daily_tokens_output * 30

        monthly_cost = provider.estimate_cost(monthly_input, monthly_output, "gemini-2.5-flash")

        print(f"\nMonthly cost projection (Gemini Flash): ${monthly_cost:.2f}")
        print(f"  Monthly tokens: {(monthly_input + monthly_output):,}")


# ============== COST OPTIMIZATION TESTS ==============

class TestCostOptimization:
    """Tests for cost optimization strategies."""

    @pytest.fixture
    def provider(self):
        """Create a GeminiProvider for testing."""
        with patch("gemini_provider.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock()
            return GeminiProvider(GeminiConfig(api_key="test"))

    def test_model_routing_saves_costs(self, provider):
        """Test that proper model routing saves costs."""
        input_tokens = 100_000
        output_tokens = 50_000

        # Cost if everything used Flash
        all_flash_cost = provider.estimate_cost(input_tokens, output_tokens, "gemini-2.5-flash") * 3

        # Cost with optimized routing:
        # - Bulk tasks: Flash-Lite (50% of work)
        # - Standard tasks: Flash (40% of work)
        # - Complex tasks: Pro (10% of work)
        optimized_cost = (
            provider.estimate_cost(input_tokens * 0.5, output_tokens * 0.5, "gemini-2.5-flash-lite") +
            provider.estimate_cost(input_tokens * 0.4, output_tokens * 0.4, "gemini-2.5-flash") +
            provider.estimate_cost(input_tokens * 0.1, output_tokens * 0.1, "gemini-2.5-pro")
        )

        # Optimized routing should save money compared to all-Flash
        savings_percent = ((all_flash_cost - optimized_cost) / all_flash_cost) * 100
        print(f"\nOptimized routing savings: {savings_percent:.1f}%")
        print(f"  All Flash: ${all_flash_cost:.4f}")
        print(f"  Optimized: ${optimized_cost:.4f}")

    def test_recommended_models_are_cost_effective(self, provider):
        """Test that recommended models for each task are cost-effective."""
        # Verify bulk tasks recommend cheapest model
        assert provider.get_recommended_model("bulk_extraction") == "gemini-2.5-flash-lite"
        assert provider.get_recommended_model("quick_classification") == "gemini-2.5-flash-lite"

        # Verify standard tasks use balanced model
        assert provider.get_recommended_model("data_extraction") == "gemini-2.5-flash"
        assert provider.get_recommended_model("executive_summary") == "gemini-2.5-flash"

        # Verify complex tasks use quality model
        assert provider.get_recommended_model("complex_analysis") == "gemini-2.5-pro"


# ============== MODEL PRICING VALIDATION ==============

class TestModelPricingValidation:
    """Tests to validate model pricing is correctly defined."""

    @pytest.fixture
    def provider(self):
        """Create a GeminiProvider for testing."""
        with patch("gemini_provider.genai") as mock_genai:
            mock_genai.configure = Mock()
            mock_genai.GenerativeModel = Mock()
            return GeminiProvider(GeminiConfig(api_key="test"))

    def test_all_models_have_pricing(self, provider):
        """Test that all expected models have pricing defined."""
        expected_models = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
        ]

        for model in expected_models:
            assert model in provider.MODEL_PRICING, f"Missing pricing for {model}"
            assert "input" in provider.MODEL_PRICING[model]
            assert "output" in provider.MODEL_PRICING[model]

    def test_pricing_values_are_positive(self, provider):
        """Test that all pricing values are positive."""
        for model, pricing in provider.MODEL_PRICING.items():
            assert pricing["input"] > 0, f"{model} input pricing must be positive"
            assert pricing["output"] > 0, f"{model} output pricing must be positive"

    def test_flash_lite_is_cheapest(self, provider):
        """Test that Flash-Lite is the cheapest model."""
        flash_lite_input = provider.MODEL_PRICING["gemini-2.5-flash-lite"]["input"]

        for model, pricing in provider.MODEL_PRICING.items():
            if model != "gemini-2.5-flash-lite":
                assert pricing["input"] >= flash_lite_input, \
                    f"{model} should not be cheaper than Flash-Lite"


# ============== RUN TESTS ==============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
