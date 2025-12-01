"""
Resource Fetcher Factory - Creates Technology-Specific Fetchers

This factory implements the Factory Pattern to create the appropriate
resource fetcher based on technology code.

Key Benefits:
1. ResearchAgent doesn't need to know about specific fetchers
2. Easy to add new technologies - just register them here
3. Centralized fetcher creation logic
4. Type safety and error handling

Adding a new technology (3 steps):
1. Create fetcher: hydro_fetcher.py
2. Import it here
3. Register in _fetchers dict

That's it! Now works everywhere.

Example:
    # Factory automatically picks the right fetcher
    solar_fetcher = ResourceFetcherFactory.create("solar_pv", config)
    wind_fetcher = ResourceFetcherFactory.create("onshore_wind", config)

    # Both have same interface, different implementations
    solar_resource = await solar_fetcher.fetch_resource(31.99, -102.07)
    wind_resource = await wind_fetcher.fetch_resource(31.99, -102.07)
"""

from typing import Dict, Any, Type
from src.core.interfaces.resource_fetcher_interface import IResourceFetcher
from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher
from src.agents.research.resource_fetchers.solar_fetcher import SolarResourceFetcher
from src.agents.research.resource_fetchers.wind_fetcher import WindResourceFetcher


class ResourceFetcherFactory:
    """
    Factory for creating technology-specific resource fetchers.

    Maintains a registry of available fetchers and creates them on demand.

    Class Attributes:
        _fetchers: Dictionary mapping technology codes to fetcher classes
    """

    # Registry of available fetchers
    # Add new technologies here!
    _fetchers: Dict[str, Type[BaseResourceFetcher]] = {
        "solar_pv": SolarResourceFetcher,
        "onshore_wind": WindResourceFetcher,
        # Add more technologies here as you scale:
        # "offshore_wind": OffshoreWindResourceFetcher,
        # "hydro": HydroResourceFetcher,
        # "geothermal": GeothermalResourceFetcher,
        # etc.
    }

    @classmethod
    def create(
            cls,
            technology: str,
            config: Dict[str, Any]
    ) -> BaseResourceFetcher:
        """
        Create a resource fetcher for the specified technology.

        Args:
            technology: Technology code (e.g., "solar_pv", "onshore_wind")
            config: Technology configuration dictionary

        Returns:
            Instance of technology-specific resource fetcher

        Raises:
            ValueError: If technology is not supported

        Example:
            >>> from src.utils.config_loader import ConfigLoader
            >>>
            >>> loader = ConfigLoader()
            >>> solar_config = loader.load_technology_config("solar_pv")
            >>>
            >>> fetcher = ResourceFetcherFactory.create("solar_pv", solar_config)
            >>> print(type(fetcher).__name__)
            'SolarResourceFetcher'
            >>>
            >>> resource = await fetcher.fetch_resource(31.99, -102.07)
        """
        # Normalize technology code (lowercase)
        technology = technology.lower()

        # Get fetcher class
        fetcher_class = cls._fetchers.get(technology)

        if fetcher_class is None:
            available = ", ".join(cls._fetchers.keys())
            raise ValueError(
                f"No resource fetcher registered for technology: {technology}. "
                f"Available technologies: {available}"
            )

        # Create and return fetcher instance
        return fetcher_class(config)

    @classmethod
    def register(
            cls,
            technology: str,
            fetcher_class: Type[BaseResourceFetcher]
    ):
        """
        Register a new resource fetcher dynamically.

        Use this to add fetchers at runtime without modifying this file.
        Useful for plugins or technology-specific modules.

        Args:
            technology: Technology code to register
            fetcher_class: Fetcher class to register

        Example:
            >>> class HydroResourceFetcher(BaseResourceFetcher):
            ...     async def fetch_resource(self, lat, lon, **kwargs):
            ...         return {"technology": "hydro", ...}
            >>>
            >>> ResourceFetcherFactory.register("hydro", HydroResourceFetcher)
            >>> fetcher = ResourceFetcherFactory.create("hydro", hydro_config)
        """
        cls._fetchers[technology.lower()] = fetcher_class

    @classmethod
    def get_supported_technologies(cls) -> list:
        """
        Get list of supported technologies.

        Returns:
            List of technology codes

        Example:
            >>> technologies = ResourceFetcherFactory.get_supported_technologies()
            >>> print(technologies)
            ['solar_pv', 'onshore_wind']
        """
        return sorted(cls._fetchers.keys())

    @classmethod
    def is_supported(cls, technology: str) -> bool:
        """
        Check if a technology is supported.

        Args:
            technology: Technology code to check

        Returns:
            True if supported, False otherwise

        Example:
            >>> ResourceFetcherFactory.is_supported("solar_pv")
            True
            >>> ResourceFetcherFactory.is_supported("nuclear")
            False
        """
        return technology.lower() in cls._fetchers


# Demo
if __name__ == "__main__":
    import asyncio
    from src.utils.config_loader import ConfigLoader

    print("=" * 70)
    print("Resource Fetcher Factory Demo")
    print("=" * 70)

    # Initialize config loader
    config_loader = ConfigLoader()

    print(f"\n1. Supported technologies: {ResourceFetcherFactory.get_supported_technologies()}")

    # Test Solar
    print("\n2. Testing Solar fetcher creation:")
    print(f"   Is solar_pv supported? {ResourceFetcherFactory.is_supported('solar_pv')}")

    solar_config = config_loader.load_technology_config("solar_pv")
    solar_fetcher = ResourceFetcherFactory.create("solar_pv", solar_config)
    print(f"   Created: {type(solar_fetcher).__name__}")
    print(f"   Technology: {solar_fetcher.get_technology_name()} ({solar_fetcher.get_technology()})")

    # Test Wind
    print("\n3. Testing Wind fetcher creation:")
    print(f"   Is onshore_wind supported? {ResourceFetcherFactory.is_supported('onshore_wind')}")

    wind_config = config_loader.load_technology_config("onshore_wind")
    wind_fetcher = ResourceFetcherFactory.create("onshore_wind", wind_config)
    print(f"   Created: {type(wind_fetcher).__name__}")
    print(f"   Technology: {wind_fetcher.get_technology_name()} ({wind_fetcher.get_technology()})")

    # Test actual resource fetching
    print("\n4. Fetching resources from both technologies:")


    async def test_fetch():
        # Solar resource
        solar_resource = await solar_fetcher.fetch_resource(31.99, -102.07)
        print(f"   Solar GHI: {solar_resource['resource_data']['avg_ghi_kwh_m2_day']} kWh/m²/day")

        # Wind resource
        wind_resource = await wind_fetcher.fetch_resource(31.99, -102.07)
        print(f"   Wind Speed: {wind_resource['resource_data']['avg_wind_speed_m_s']} m/s")


    asyncio.run(test_fetch())

    # Test error handling
    print("\n5. Testing error handling:")
    try:
        ResourceFetcherFactory.create("nuclear", {})
    except ValueError as e:
        print(f"   Expected error: {e}")

    # Test dynamic registration
    print("\n6. Testing dynamic registration:")


    class TestTechFetcher(BaseResourceFetcher):
        async def fetch_resource(self, latitude: float, longitude: float, **kwargs):
            return {
                "technology": "test_tech",
                "location": {"latitude": latitude, "longitude": longitude},
                "resource_data": {"test": "data"},
                "quality": {"confidence": "high"}
            }


    print(f"   Before: Supported = {ResourceFetcherFactory.get_supported_technologies()}")
    ResourceFetcherFactory.register("test_tech", TestTechFetcher)
    print(f"   After:  Supported = {ResourceFetcherFactory.get_supported_technologies()}")

    test_fetcher = ResourceFetcherFactory.create("test_tech", {"technology": {"code": "test_tech"}})
    print(f"   Created: {type(test_fetcher).__name__}")

    print("\n" + "=" * 70)
    print("✅ Resource Fetcher Factory working correctly!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("- Factory creates the right fetcher automatically")
    print("- ResearchAgent just calls: ResourceFetcherFactory.create(tech, config)")
    print("- Add new technology: Create fetcher + register in _fetchers")
    print("- Can also register dynamically at runtime")