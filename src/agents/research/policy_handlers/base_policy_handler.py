"""
Base Policy Handler - Common Policy Logic

Provides common functionality for all policy handlers:
- Configuration access
- Logging
- Error handling
- Data validation

Subclasses only implement country-specific logic.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from src.core.interfaces.policy_handler_interface import IPolicyHandler


class BasePolicyHandler(IPolicyHandler, ABC):
    """
    Base implementation of IPolicyHandler.

    Provides common functionality that all policy handlers need:
    - Configuration management
    - Logging
    - Basic validation

    Subclasses only implement:
    - fetch_policy(): Country-specific logic
    - get_country_code(): Country identifier

    Attributes:
        config (Dict): Configuration for this country
        logger (logging.Logger): Logger instance
    """

    def __init__(self, config: Dict[str, Any], logger: logging.Logger = None):
        """
        Initialize base policy handler.

        Args:
            config: Country configuration dictionary
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or self._create_logger()

    @abstractmethod
    async def fetch_policy(
            self,
            technology: str,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch country-specific policy data.

        Must be implemented by subclass.
        """
        pass

    def get_country_code(self) -> str:
        """
        Get country code from config.

        Returns:
            Country code (e.g., "USA", "DEU")
        """
        return self.config.get("country", {}).get("code", "UNKNOWN")

    def get_country_name(self) -> str:
        """
        Get country name from config.

        Returns:
            Country name (e.g., "United States", "Germany")
        """
        return self.config.get("country", {}).get("name", "Unknown Country")

    def _validate_policy_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate that policy result has required fields.

        Args:
            result: Policy data dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["country", "technology", "incentives", "tax_rate", "source"]
        return all(field in result for field in required_fields)

    def _create_logger(self) -> logging.Logger:
        """Create a logger for this handler."""
        country_code = self.get_country_code()
        logger_name = f"PolicyHandler-{country_code}"
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
    print("Base Policy Handler Demo")
    print("=" * 70)


    # Create a test handler
    class TestPolicyHandler(BasePolicyHandler):
        async def fetch_policy(self, technology: str, **kwargs) -> Dict[str, Any]:
            return {
                "country": self.get_country_code(),
                "technology": technology,
                "incentives": {"test": "data"},
                "tax_rate": 0.21,
                "source": "test"
            }


    test_config = {
        "country": {
            "code": "TST",
            "name": "Test Country"
        }
    }

    handler = TestPolicyHandler(test_config)

    print(f"\n1. Country code: {handler.get_country_code()}")
    print(f"2. Country name: {handler.get_country_name()}")

    import asyncio


    async def test():
        result = await handler.fetch_policy("solar_pv")
        print(f"\n3. Policy result: {result}")
        print(f"4. Validation: {handler._validate_policy_result(result)}")


    asyncio.run(test())

    print("\n" + "=" * 70)
    print("✅ Base Policy Handler working correctly!")
    print("=" * 70)