"""
LLM Provider Factory - Create LLM Providers

Factory for creating different LLM providers:
- Mock: For testing/demo (free)
- OpenAI: GPT-4 (best, ~$0.03/analysis)
- Anthropic: Claude (good alternative, ~$0.015/analysis)

Usage:
    # Create from environment
    provider = LLMProviderFactory.create_from_env()

    # Create specific provider
    provider = LLMProviderFactory.create("openai", api_key="sk-...")
"""

import os
import logging
from typing import Optional, Dict, Any

from src.core.interfaces.llm_provider_interface import ILLMProvider
from src.llm.mock_provider import MockLLMProvider


class LLMProviderFactory:
    """
    Factory for creating LLM providers.

    Supports:
    - mock: Mock provider (free, for testing)
    - openai: OpenAI GPT-4
    - anthropic: Anthropic Claude (future)
    """

    @staticmethod
    def create(
            provider_type: str = "mock",
            api_key: Optional[str] = None,
            model: Optional[str] = None,
            logger: Optional[logging.Logger] = None,
            **kwargs
    ) -> ILLMProvider:
        """
        Create LLM provider.

        Args:
            provider_type: Type of provider ("mock", "openai", "anthropic")
            api_key: API key for provider (optional, reads from env)
            model: Model to use (optional, uses provider default)
            logger: Logger instance (optional)
            **kwargs: Additional provider-specific arguments

        Returns:
            LLM provider instance

        Raises:
            ValueError: If provider type unknown
            ImportError: If required package not installed

        Examples:
            # Mock provider (free)
            >>> provider = LLMProviderFactory.create("mock")

            # OpenAI GPT-4
            >>> provider = LLMProviderFactory.create(
            ...     "openai",
            ...     api_key="sk-...",
            ...     model="gpt-4o"
            ... )

            # From environment variable
            >>> os.environ["LLM_PROVIDER"] = "openai"
            >>> provider = LLMProviderFactory.create_from_env()
        """
        provider_type = provider_type.lower().strip()

        if provider_type == "mock":
            return MockLLMProvider()

        elif provider_type == "openai":
            try:
                from src.llm.openai_provider import OpenAIProvider

                return OpenAIProvider(
                    api_key=api_key,
                    model=model or "gpt-4o",
                    logger=logger
                )
            except ImportError as e:
                raise ImportError(
                    "OpenAI provider requires 'openai' package. "
                    "Install with: pip install openai"
                ) from e

        elif provider_type == "anthropic":
            try:
                from src.llm.anthropic_provider import AnthropicProvider

                return AnthropicProvider(
                    api_key=api_key,
                    model=model or "claude-3-5-sonnet-20241022",
                    logger=logger
                )
            except ImportError:
                raise ImportError(
                    "Anthropic provider not yet implemented. "
                    "Use 'openai' or 'mock' instead."
                )

        else:
            raise ValueError(
                f"Unknown provider type: {provider_type}. "
                f"Supported: 'mock', 'openai', 'anthropic'"
            )

    @staticmethod
    def create_from_env(
            logger: Optional[logging.Logger] = None
    ) -> ILLMProvider:
        """
        Create LLM provider from environment variables.

        Reads configuration from:
        - LLM_PROVIDER: Provider type (default: "mock")
        - LLM_MODEL: Model name (optional)
        - OPENAI_API_KEY: For OpenAI
        - ANTHROPIC_API_KEY: For Anthropic

        Returns:
            LLM provider instance

        Examples:
            # Set environment variables
            >>> os.environ["LLM_PROVIDER"] = "openai"
            >>> os.environ["OPENAI_API_KEY"] = "sk-..."
            >>> os.environ["LLM_MODEL"] = "gpt-4o"

            # Create provider
            >>> provider = LLMProviderFactory.create_from_env()
        """
        provider_type = os.getenv("LLM_PROVIDER", "mock")
        model = os.getenv("LLM_MODEL")

        # Get API key based on provider type
        api_key = None
        if provider_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider_type == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")

        return LLMProviderFactory.create(
            provider_type=provider_type,
            api_key=api_key,
            model=model,
            logger=logger
        )

    @staticmethod
    def get_available_providers() -> Dict[str, Dict[str, Any]]:
        """
        Get information about available providers.

        Returns:
            Dictionary with provider information
        """
        return {
            "mock": {
                "name": "Mock Provider",
                "description": "Mock LLM for testing and demo",
                "cost": "Free",
                "quality": "Basic",
                "requires": None,
                "env_var": None
            },
            "openai": {
                "name": "OpenAI GPT-4",
                "description": "OpenAI's GPT-4 models",
                "cost": "$0.003-0.06 per analysis",
                "quality": "Excellent",
                "requires": "openai package",
                "env_var": "OPENAI_API_KEY",
                "models": ["gpt-4o", "gpt-4-turbo", "gpt-4"],
                "recommended": "gpt-4o"
            },
            "anthropic": {
                "name": "Anthropic Claude",
                "description": "Anthropic's Claude models",
                "cost": "$0.015 per analysis",
                "quality": "Excellent",
                "requires": "anthropic package",
                "env_var": "ANTHROPIC_API_KEY",
                "models": ["claude-3-5-sonnet-20241022"],
                "status": "Coming soon"
            }
        }


# Demo
if __name__ == "__main__":
    print("=" * 70)
    print("🏭 LLM Provider Factory Demo")
    print("=" * 70)

    # Show available providers
    print("\n📋 Available Providers:")
    print("-" * 70)

    providers = LLMProviderFactory.get_available_providers()
    for key, info in providers.items():
        print(f"\n{info['name']} ({key}):")
        print(f"  Description: {info['description']}")
        print(f"  Cost: {info['cost']}")
        print(f"  Quality: {info['quality']}")
        if info.get('requires'):
            print(f"  Requires: {info['requires']}")
        if info.get('env_var'):
            print(f"  API Key Env: {info['env_var']}")
        if info.get('models'):
            print(f"  Models: {', '.join(info['models'])}")
            if info.get('recommended'):
                print(f"  Recommended: {info['recommended']}")
        if info.get('status'):
            print(f"  Status: {info['status']}")

    # Test provider creation
    print("\n" + "=" * 70)
    print("🧪 Testing Provider Creation")
    print("=" * 70)

    # Test 1: Mock provider (always works)
    print("\n1. Creating Mock Provider...")
    try:
        mock_provider = LLMProviderFactory.create("mock")
        print(f"   ✅ Success: {mock_provider.get_provider_name()}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

    # Test 2: OpenAI provider
    print("\n2. Creating OpenAI Provider...")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            openai_provider = LLMProviderFactory.create("openai")
            print(f"   ✅ Success: {openai_provider.get_provider_name()}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    else:
        print("   ⚠️  OPENAI_API_KEY not set")

    # Test 3: From environment
    print("\n3. Creating from Environment...")
    try:
        env_provider = LLMProviderFactory.create_from_env()
        print(f"   ✅ Success: {env_provider.get_provider_name()}")
        print(f"   Provider type: {os.getenv('LLM_PROVIDER', 'mock')}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

    # Show configuration
    print("\n" + "=" * 70)
    print("⚙️  Current Configuration")
    print("=" * 70)
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'mock (default)')}")
    print(f"  LLM_MODEL: {os.getenv('LLM_MODEL', 'provider default')}")
    print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")

    print("\n" + "=" * 70)
    print("✅ LLM Provider Factory Working!")
    print("=" * 70)
    print("\n💡 To use OpenAI:")
    print("   export LLM_PROVIDER='openai'")
    print("   export OPENAI_API_KEY='sk-...'")
    print("   export LLM_MODEL='gpt-4o'  # optional")
    print("=" * 70)