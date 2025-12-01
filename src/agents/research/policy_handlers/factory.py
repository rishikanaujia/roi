"""
Policy Handler Factory - Creates Country-Specific Handlers

This factory implements the Factory Pattern to create the appropriate
policy handler based on country code.

Key Benefits:
1. ResearchAgent doesn't need to know about specific handlers
2. Easy to add new countries - just register them here
3. Centralized handler creation logic
4. Type safety and error handling

Adding a new country (3 steps):
1. Create handler: india_policy_handler.py
2. Import it here
3. Register in _handlers dict

That's it! Now works everywhere.

Example:
    # Factory automatically picks the right handler
    usa_handler = PolicyHandlerFactory.create("USA", config)
    germany_handler = PolicyHandlerFactory.create("DEU", config)

    # Both have same interface, different implementations
    usa_policy = await usa_handler.fetch_policy("solar_pv")
    germany_policy = await germany_handler.fetch_policy("solar_pv")
"""

from typing import Dict, Any, Type
from src.core.interfaces.policy_handler_interface import IPolicyHandler
from src.agents.research.policy_handlers.base_policy_handler import BasePolicyHandler
from src.agents.research.policy_handlers.usa_policy_handler import USAPolicyHandler
from src.agents.research.policy_handlers.germany_policy_handler import GermanyPolicyHandler


class PolicyHandlerFactory:
    """
    Factory for creating country-specific policy handlers.

    Maintains a registry of available handlers and creates them on demand.

    Class Attributes:
        _handlers: Dictionary mapping country codes to handler classes
    """

    # Registry of available handlers
    # Add new countries here!
    _handlers: Dict[str, Type[BasePolicyHandler]] = {
        "USA": USAPolicyHandler,
        "DEU": GermanyPolicyHandler,
        # Add more countries here as you scale:
        # "CHN": ChinaPolicyHandler,
        # "IND": IndiaPolicyHandler,
        # "BRA": BrazilPolicyHandler,
        # "AUS": AustraliaPolicyHandler,
        # etc.
    }

    @classmethod
    def create(
            cls,
            country_code: str,
            config: Dict[str, Any]
    ) -> BasePolicyHandler:
        """
        Create a policy handler for the specified country.

        Args:
            country_code: ISO 3166-1 alpha-3 code (e.g., "USA", "DEU", "CHN")
            config: Country configuration dictionary

        Returns:
            Instance of country-specific policy handler

        Raises:
            ValueError: If country is not supported

        Example:
            >>> from src.utils.config_loader import ConfigLoader
            >>>
            >>> loader = ConfigLoader()
            >>> usa_config = loader.load_country_config("USA")
            >>>
            >>> handler = PolicyHandlerFactory.create("USA", usa_config)
            >>> print(type(handler).__name__)
            'USAPolicyHandler'
            >>>
            >>> policy = await handler.fetch_policy("solar_pv")
        """
        # Normalize country code (uppercase)
        country_code = country_code.upper()

        # Get handler class
        handler_class = cls._handlers.get(country_code)

        if handler_class is None:
            available = ", ".join(cls._handlers.keys())
            raise ValueError(
                f"No policy handler registered for country: {country_code}. "
                f"Available countries: {available}"
            )

        # Create and return handler instance
        return handler_class(config)

    @classmethod
    def register(
            cls,
            country_code: str,
            handler_class: Type[BasePolicyHandler]
    ):
        """
        Register a new policy handler dynamically.

        Use this to add handlers at runtime without modifying this file.
        Useful for plugins or country-specific modules.

        Args:
            country_code: Country code to register
            handler_class: Handler class to register

        Example:
            >>> class IndiaPolicyHandler(BasePolicyHandler):
            ...     async def fetch_policy(self, tech, **kwargs):
            ...         return {"country": "IND", ...}
            >>>
            >>> PolicyHandlerFactory.register("IND", IndiaPolicyHandler)
            >>> handler = PolicyHandlerFactory.create("IND", india_config)
        """
        cls._handlers[country_code.upper()] = handler_class

    @classmethod
    def get_supported_countries(cls) -> list:
        """
        Get list of supported countries.

        Returns:
            List of country codes

        Example:
            >>> countries = PolicyHandlerFactory.get_supported_countries()
            >>> print(countries)
            ['USA', 'DEU']
        """
        return sorted(cls._handlers.keys())

    @classmethod
    def is_supported(cls, country_code: str) -> bool:
        """
        Check if a country is supported.

        Args:
            country_code: Country code to check

        Returns:
            True if supported, False otherwise

        Example:
            >>> PolicyHandlerFactory.is_supported("USA")
            True
            >>> PolicyHandlerFactory.is_supported("ZZZ")
            False
        """
        return country_code.upper() in cls._handlers


# Demo
if __name__ == "__main__":
    import asyncio
    from src.utils.config_loader import ConfigLoader

    print("=" * 70)
    print("Policy Handler Factory Demo")
    print("=" * 70)

    # Initialize config loader
    config_loader = ConfigLoader()

    print(f"\n1. Supported countries: {PolicyHandlerFactory.get_supported_countries()}")

    # Test USA
    print("\n2. Testing USA handler creation:")
    print(f"   Is USA supported? {PolicyHandlerFactory.is_supported('USA')}")

    usa_config = config_loader.load_country_config("USA")
    usa_handler = PolicyHandlerFactory.create("USA", usa_config)
    print(f"   Created: {type(usa_handler).__name__}")
    print(f"   Country: {usa_handler.get_country_name()} ({usa_handler.get_country_code()})")

    # Test Germany
    print("\n3. Testing Germany handler creation:")
    print(f"   Is DEU supported? {PolicyHandlerFactory.is_supported('DEU')}")

    germany_config = config_loader.load_country_config("DEU")
    germany_handler = PolicyHandlerFactory.create("DEU", germany_config)
    print(f"   Created: {type(germany_handler).__name__}")
    print(f"   Country: {germany_handler.get_country_name()} ({germany_handler.get_country_code()})")

    # Test actual policy fetching
    print("\n4. Fetching policies from both countries:")


    async def test_fetch():
        # USA Solar
        usa_solar = await usa_handler.fetch_policy("solar_pv", state="TX")
        print(f"   USA Solar ITC: {usa_solar['incentives']['federal_itc_percentage']}%")

        # Germany Solar
        germany_solar = await germany_handler.fetch_policy("solar_pv")
        print(f"   Germany Solar Tariff: €{germany_solar['incentives']['base_tariff_eur_per_mwh']}/MWh")


    asyncio.run(test_fetch())

    # Test error handling
    print("\n5. Testing error handling:")
    try:
        PolicyHandlerFactory.create("ZZZ", {})
    except ValueError as e:
        print(f"   Expected error: {e}")

    # Test dynamic registration
    print("\n6. Testing dynamic registration:")


    class TestCountryHandler(BasePolicyHandler):
        async def fetch_policy(self, technology: str, **kwargs):
            return {
                "country": "TST",
                "technology": technology,
                "incentives": {"test": "data"},
                "tax_rate": 0.20,
                "source": "test"
            }


    print(f"   Before: Supported = {PolicyHandlerFactory.get_supported_countries()}")
    PolicyHandlerFactory.register("TST", TestCountryHandler)
    print(f"   After:  Supported = {PolicyHandlerFactory.get_supported_countries()}")

    test_handler = PolicyHandlerFactory.create("TST", {"country": {"code": "TST"}})
    print(f"   Created: {type(test_handler).__name__}")

    print("\n" + "=" * 70)
    print("✅ Policy Handler Factory working correctly!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("- Factory creates the right handler automatically")
    print("- ResearchAgent just calls: PolicyHandlerFactory.create(country, config)")
    print("- Add new country: Create handler + register in _handlers")
    print("- Can also register dynamically at runtime")