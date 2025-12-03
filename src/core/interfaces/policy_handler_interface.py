"""
Policy Handler Interface - Country-Specific Policy Fetching

This interface defines the contract for country-specific policy handlers.
Each country (USA, Germany, India, etc.) will have its own implementation.

Why separate interface?
- Countries have VERY different policy structures
- USA: Federal ITC + State incentives + MACRS
- Germany: EEG feed-in tariffs + market premium
- China: FIT + provincial subsidies + green certificates

Design Pattern: Strategy Pattern
- Policy handlers are interchangeable strategies
- Factory creates the right handler based on country code
- Agent doesn't know which handler it's using

Example:
    # USA handler fetches IRS ITC data
    usa_handler = USAPolicyHandler(config)
    policy = await usa_handler.fetch_policy("solar_pv")

    # Germany handler fetches EEG data
    germany_handler = GermanyPolicyHandler(config)
    policy = await germany_handler.fetch_policy("solar_pv")

    # Both return consistent structure, different data
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IPolicyHandler(ABC):
    """
    Interface for country-specific policy handlers.

    Each country implements this to fetch its specific policy data:
    - Tax incentives
    - Subsidies
    - Depreciation rules
    - Feed-in tariffs
    - Renewable energy credits
    - etc.

    All handlers must return data in a consistent structure so
    the ResearchAgent can process it uniformly.
    """

    @abstractmethod
    async def fetch_policy(
            self,
            technology: str,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch policy data for a specific technology.

        This is where country-specific logic lives:
        - USA: Call IRS API for ITC, DSIRE for state incentives
        - Germany: Call BNetzA for EEG tariffs
        - China: Call NDRC for FIT rates

        Args:
            technology: Technology code (e.g., "solar_pv", "onshore_wind")
            **kwargs: Additional parameters
                - latitude: float (optional, for regional policies)
                - longitude: float (optional, for regional policies)
                - capacity_mw: float (optional, size-dependent policies)
                - state: str (optional, for USA state-level policies)

        Returns:
            Dictionary containing policy data:
            {
                "country": "USA",
                "technology": "solar_pv",
                "incentives": {
                    "federal_itc_percentage": 30.0,
                    "state_incentives": [...],
                    "production_tax_credit": 0.0
                },
                "depreciation": {
                    "method": "MACRS",
                    "years": 5,
                    "schedule": [0.20, 0.32, ...]
                },
                "tax_rate": 0.21,
                "source": "IRS + DSIRE",
                "confidence": "high",
                "last_updated": "2024-12-01"
            }

        Example:
            >>> handler = USAPolicyHandler(config)
            >>> policy = await handler.fetch_policy("solar_pv", state="TX")
            >>> print(policy["incentives"]["federal_itc_percentage"])
            30.0
            >>> print(policy["incentives"]["state_incentives"])
            ["Texas RPS: 10,000 MW by 2025"]
        """
        pass

    @abstractmethod
    def get_country_code(self) -> str:
        """
        Get the country code this handler is for.

        Returns:
            ISO 3166-1 alpha-3 country code (e.g., "USA", "DEU", "CHN")

        Example:
            >>> handler = USAPolicyHandler(config)
            >>> handler.get_country_code()
            'USA'
        """
        pass


# Example result structure for documentation
POLICY_RESULT_EXAMPLE = {
    "country": "USA",
    "technology": "solar_pv",
    "incentives": {
        "federal_itc_percentage": 30.0,
        "state_incentives": [
            "Texas RPS: 10,000 MW by 2025",
            "Federal Production Tax Credit: $27.50/MWh (if applicable)"
        ],
        "depreciation_benefit_percentage": 15.0  # Calculated benefit
    },
    "depreciation": {
        "method": "MACRS",
        "years": 5,
        "schedule": [0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576]
    },
    "tax_rate": 0.21,
    "regulatory": {
        "permitting_months": 6,
        "environmental_review_required": True,
        "interconnection_study_months": 3
    },
    "source": "IRS (2024) + DSIRE Database",
    "confidence": "high",
    "last_updated": "2024-12-01",
    "notes": "ITC reduced to 26% after 2025, 22% in 2026"
}

if __name__ == "__main__":
    print("=" * 70)
    print("Policy Handler Interface Demo")
    print("=" * 70)

    print("\nThis interface defines the contract for country-specific policy handlers.")
    print("\nExpected return structure:")

    import json

    print(json.dumps(POLICY_RESULT_EXAMPLE, indent=2))

    print("\n" + "=" * 70)
    print("Key Points:")
    print("- Each country implements this interface")
    print("- USA handler: Fetches IRS ITC + DSIRE state incentives")
    print("- Germany handler: Fetches EEG feed-in tariffs")
    print("- All return consistent structure")
    print("- ResearchAgent doesn't care which handler is used")
    print("=" * 70)