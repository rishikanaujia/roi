"""
LLM Provider Interface - AI Integration Contract

Defines the contract for LLM providers (OpenAI, Anthropic, etc.)

This enables:
- AI-generated insights
- Risk assessment
- Data quality analysis
- Investment recommendations
- Natural language summaries

Design Pattern: Strategy Pattern
- Different LLM providers are interchangeable
- Easy to switch from Mock → OpenAI → Claude
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum


class LLMRole(Enum):
    """LLM conversation roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ILLMProvider(ABC):
    """
    Interface for LLM providers.

    All LLM providers (OpenAI, Anthropic, etc.) must implement this interface.
    """

    @abstractmethod
    async def generate_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: int = 500
    ) -> str:
        """
        Generate a completion from messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text

        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are a financial analyst."},
            ...     {"role": "user", "content": "Analyze this solar project..."}
            ... ]
            >>> response = await provider.generate_completion(messages)
        """
        pass

    @abstractmethod
    async def generate_insights(
            self,
            analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate investment insights from analysis data.

        Args:
            analysis_data: Complete analysis results

        Returns:
            Dictionary with insights:
            {
                "key_insights": ["insight1", "insight2", ...],
                "risks": ["risk1", "risk2", ...],
                "opportunities": ["opp1", "opp2", ...],
                "recommendation_summary": "Natural language summary"
            }
        """
        pass

    @abstractmethod
    async def assess_data_quality(
            self,
            research_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess quality of research data.

        Args:
            research_data: Research results

        Returns:
            Dictionary with quality assessment:
            {
                "overall_quality": "high/medium/low",
                "confidence_score": 0.85,
                "data_gaps": ["gap1", "gap2"],
                "quality_notes": "Explanation..."
            }
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name (e.g., 'OpenAI', 'Anthropic', 'Mock')."""
        pass


if __name__ == "__main__":
    print("=" * 70)
    print("LLM Provider Interface")
    print("=" * 70)
    print("\nThis interface enables AI-powered features:")
    print("  • Investment insights generation")
    print("  • Risk assessment")
    print("  • Data quality analysis")
    print("  • Natural language recommendations")
    print("\nProviders can be:")
    print("  • MockLLMProvider (for testing/demo)")
    print("  • OpenAIProvider (GPT-4)")
    print("  • AnthropicProvider (Claude)")
    print("=" * 70)