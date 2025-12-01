"""
Base Resource Fetcher - Common Resource Logic

Provides common functionality for all resource fetchers:
- Configuration access
- Logging
- Location validation
- Data quality checks

Subclasses only implement technology-specific logic.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from src.core.interfaces.resource_fetcher_interface import IResourceFetcher


class BaseResourceFetcher(IResourceFetcher, ABC):
    """
    Base implementation of IResourceFetcher.

    Provides common functionality that all resource fetchers need:
    - Configuration management
    - Logging
    - Location validation
    - Basic data validation

    Subclasses only implement:
    - fetch_resource(): Technology-specific logic
    - get_technology(): Technology identifier

    Attributes:
        config (Dict): Configuration for this technology
        logger (logging.Logger): Logger instance
    """

    def __init__(self, config: Dict[str, Any], logger: logging.Logger = None):
        """
        Initialize base resource fetcher.

        Args:
            config: Technology configuration dictionary
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or self._create_logger()

    @abstractmethod
    async def fetch_resource(
            self,
            latitude: float,
            longitude: float,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch technology-specific resource data.

        Must be implemented by subclass.
        """
        pass

    def get_technology(self) -> str:
        """
        Get technology code from config.

        Returns:
            Technology code (e.g., "solar_pv", "onshore_wind")
        """
        return self.config.get("technology", {}).get("code", "UNKNOWN")

    def get_technology_name(self) -> str:
        """
        Get technology name from config.

        Returns:
            Technology name (e.g., "Solar Photovoltaic", "Onshore Wind")
        """
        return self.config.get("technology", {}).get("name", "Unknown Technology")

    def _validate_location(self, latitude: float, longitude: float) -> bool:
        """
        Validate latitude and longitude.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return False

        if not -90 <= latitude <= 90:
            self.logger.error(f"Invalid latitude: {latitude} (must be -90 to 90)")
            return False

        if not -180 <= longitude <= 180:
            self.logger.error(f"Invalid longitude: {longitude} (must be -180 to 180)")
            return False

        return True

    def _validate_resource_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate that resource result has required fields.

        Args:
            result: Resource data dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["technology", "location", "resource_data", "quality"]
        return all(field in result for field in required_fields)

    def _create_logger(self) -> logging.Logger:
        """Create a logger for this fetcher."""
        tech_code = self.get_technology()
        logger_name = f"ResourceFetcher-{tech_code}"
        logger = logging.getLogger(logger_name)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger


if __name__ == "__main__":
    print("=" * 70)
    print("Base Resource Fetcher Demo")
    print("=" * 70)


    # Create a test fetcher
    class TestResourceFetcher(BaseResourceFetcher):
        async def fetch_resource(self, latitude: float, longitude: float, **kwargs) -> Dict[str, Any]:
            if not self._validate_location(latitude, longitude):
                raise ValueError("Invalid location")

            return {
                "technology": self.get_technology(),
                "location": {"latitude": latitude, "longitude": longitude},
                "resource_data": {"test": "data"},
                "quality": {"confidence": "high"}
            }


    test_config = {
        "technology": {
            "code": "test_tech",
            "name": "Test Technology"
        }
    }

    fetcher = TestResourceFetcher(test_config)

    print(f"\n1. Technology code: {fetcher.get_technology()}")
    print(f"2. Technology name: {fetcher.get_technology_name()}")

    # Test location validation
    print("\n3. Testing location validation:")
    print(f"   Valid (31.99, -102.07): {fetcher._validate_location(31.99, -102.07)}")
    print(f"   Invalid (91.0, 0.0): {fetcher._validate_location(91.0, 0.0)}")
    print(f"   Invalid (0.0, 181.0): {fetcher._validate_location(0.0, 181.0)}")

    import asyncio


    async def test():
        result = await fetcher.fetch_resource(31.99, -102.07)
        print(f"\n4. Resource result: {result}")
        print(f"5. Validation: {fetcher._validate_resource_result(result)}")


    asyncio.run(test())

    print("\n" + "=" * 70)
    print("✅ Base Resource Fetcher working correctly!")
    print("=" * 70)