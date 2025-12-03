"""
Research Agent - Hybrid Architecture Implementation

This is THE KEY FILE that demonstrates hybrid architecture.

One agent that works for ANY country + ANY technology:
- USA + Solar PV ✅
- USA + Wind ✅
- Germany + Solar PV ✅
- Germany + Wind ✅
- Add India? Just create policy handler → Works for all technologies!
- Add Hydro? Just create resource fetcher → Works for all countries!

How it works:
1. Agent is initialized with country_code + technology
2. ConfigLoader loads the combined configuration
3. PolicyHandlerFactory creates the right country handler
4. ResourceFetcherFactory creates the right technology fetcher
5. Agent orchestrates both to fetch complete data

NO hardcoding. NO duplication. Pure scalability.

Example:
    # USA + Solar
    agent = ResearchAgent(llm, config, "USA", "solar_pv")
    result = await agent.execute({"latitude": 31.99, "longitude": -102.07})

    # Germany + Wind (same agent class, different behavior!)
    agent = ResearchAgent(llm, config, "DEU", "onshore_wind")
    result = await agent.execute({"latitude": 48.0, "longitude": 11.0})
"""

import json
from typing import Dict, Any
from src.core.base_agent import BaseAgent
from src.utils.config_loader import ConfigLoader
from src.agents.research.policy_handlers.factory import PolicyHandlerFactory
from src.agents.research.resource_fetchers.factory import ResourceFetcherFactory


class ResearchAgent(BaseAgent):
    """
    Research Agent with Hybrid Architecture.

    Generic research agent that works for ANY country + technology combination.

    Architecture:
    - Generic framework (this class)
    - Pluggable policy handler (country-specific)
    - Pluggable resource fetcher (technology-specific)
    - Dynamic configuration loading

    Attributes:
        country_code (str): Country code (e.g., "USA", "DEU")
        technology (str): Technology code (e.g., "solar_pv", "onshore_wind")
        runtime_config (Dict): Merged country + technology configuration
        policy_handler: Country-specific policy handler
        resource_fetcher: Technology-specific resource fetcher
    """

    def __init__(
            self,
            llm_provider,  # In full implementation, this would be ILLMProvider
            config: Dict[str, Any],
            country_code: str,
            technology: str,
            logger=None
    ):
        """
        Initialize Research Agent.

        Args:
            llm_provider: LLM provider for AI operations
            config: Base configuration
            country_code: Country code (e.g., "USA", "DEU")
            technology: Technology code (e.g., "solar_pv", "onshore_wind")
            logger: Optional logger
        """
        super().__init__("ResearchAgent", llm_provider, config, logger)

        self.country_code = country_code.upper()
        self.technology = technology.lower()

        # Load dynamic configuration
        self.logger.info(f"Initializing ResearchAgent for {country_code} + {technology}")
        config_loader = ConfigLoader()
        self.runtime_config = config_loader.load_combination_config(
            self.country_code,
            self.technology
        )

        # Plug in country-specific policy handler
        self.logger.info(f"Creating policy handler for {country_code}")
        self.policy_handler = PolicyHandlerFactory.create(
            self.country_code,
            self.runtime_config
        )

        # Plug in technology-specific resource fetcher
        self.logger.info(f"Creating resource fetcher for {technology}")
        self.resource_fetcher = ResourceFetcherFactory.create(
            self.technology,
            self.runtime_config
        )

        self.logger.info(
            f"ResearchAgent ready: {self.runtime_config['country']['name']} + "
            f"{self.runtime_config['technology']['name']}"
        )

    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core execution - Fetch policy and resource data.

        This is where the magic happens:
        1. Fetch policy data using country-specific handler
        2. Fetch resource data using technology-specific fetcher
        3. Combine and normalize both

        Args:
            input_data: Must contain latitude, longitude

        Returns:
            Dictionary with policy_data, resource_data, and metadata
        """
        latitude = input_data["latitude"]
        longitude = input_data["longitude"]

        self.logger.info(
            f"Researching {self.technology} opportunity in {self.country_code} "
            f"at ({latitude}, {longitude})"
        )

        # Step 1: Fetch policy data (country-specific implementation)
        self.logger.info("Fetching policy data...")
        policy_data = await self.policy_handler.fetch_policy(
            technology=self.technology,
            **input_data  # Contains latitude, longitude, and other params
        )

        # Step 2: Fetch resource data (technology-specific implementation)
        self.logger.info("Fetching resource data...")
        resource_data = await self.resource_fetcher.fetch_resource(
            **input_data  # Contains latitude, longitude, and other params
        )

        # Step 3: Combine and structure results
        result = {
            "country": self.country_code,
            "technology": self.technology,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "policy_data": policy_data,
            "resource_data": resource_data,
            "data_completeness": self._assess_completeness(policy_data, resource_data),
            "research_status": "complete"
        }

        self.logger.info("Research complete")
        return result

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input has required fields.

        Args:
            input_data: Input to validate

        Returns:
            True if valid, False otherwise
        """
        # Check base validation
        if not super().validate_input(input_data):
            return False

        # Check required fields
        required = ["latitude", "longitude"]
        if not all(field in input_data for field in required):
            self.logger.error(f"Missing required fields: {required}")
            return False

        # Validate latitude/longitude ranges
        lat = input_data["latitude"]
        lon = input_data["longitude"]

        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            self.logger.error("Latitude and longitude must be numbers")
            return False

        if not -90 <= lat <= 90:
            self.logger.error(f"Latitude {lat} out of range (-90 to 90)")
            return False

        if not -180 <= lon <= 180:
            self.logger.error(f"Longitude {lon} out of range (-180 to 180)")
            return False

        return True

    def _assess_completeness(
            self,
            policy_data: Dict[str, Any],
            resource_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess data completeness and confidence.

        Args:
            policy_data: Policy information
            resource_data: Resource information

        Returns:
            Dictionary with completeness assessment
        """
        policy_confidence = policy_data.get("confidence", "unknown")
        resource_confidence = resource_data.get("quality", {}).get("confidence", "unknown")

        # Overall confidence is the minimum of both
        confidence_levels = ["unknown", "low", "medium", "high", "very_high"]

        try:
            policy_idx = confidence_levels.index(policy_confidence)
            resource_idx = confidence_levels.index(resource_confidence)
            overall_idx = min(policy_idx, resource_idx)
            overall_confidence = confidence_levels[overall_idx]
        except ValueError:
            overall_confidence = "unknown"

        return {
            "policy_confidence": policy_confidence,
            "resource_confidence": resource_confidence,
            "overall_confidence": overall_confidence,
            "has_policy_data": bool(policy_data),
            "has_resource_data": bool(resource_data),
            "ready_for_analysis": overall_confidence in ["medium", "high", "very_high"]
        }


# Demo
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("🎉 ResearchAgent - HYBRID ARCHITECTURE IN ACTION! 🎉")
    print("=" * 70)


    # Mock LLM provider for demo
    class MockLLMProvider:
        pass


    async def demo():
        # Test 1: USA + Solar PV
        print("\n" + "=" * 70)
        print("TEST 1: USA + Solar PV")
        print("=" * 70)

        agent1 = ResearchAgent(
            llm_provider=MockLLMProvider(),
            config={},
            country_code="USA",
            technology="solar_pv"
        )

        print(f"\nAgent initialized:")
        print(f"  Country: {agent1.runtime_config['country']['name']}")
        print(f"  Technology: {agent1.runtime_config['technology']['name']}")
        print(f"  Policy Handler: {type(agent1.policy_handler).__name__}")
        print(f"  Resource Fetcher: {type(agent1.resource_fetcher).__name__}")

        # Execute research
        input_data = {
            "latitude": 31.99,
            "longitude": -102.07,
            "capacity_mw": 100
        }

        result1 = await agent1.execute(input_data)

        print(f"\nResults:")
        print(f"  Location: ({result1['location']['latitude']}, {result1['location']['longitude']})")
        print(f"  Policy - ITC: {result1['policy_data']['incentives']['federal_itc_percentage']}%")
        print(f"  Resource - GHI: {result1['resource_data']['resource_data']['avg_ghi_kwh_m2_day']} kWh/m²/day")
        print(f"  Overall Confidence: {result1['data_completeness']['overall_confidence']}")

        # Test 2: Germany + Onshore Wind
        print("\n" + "=" * 70)
        print("TEST 2: Germany + Onshore Wind")
        print("=" * 70)

        agent2 = ResearchAgent(
            llm_provider=MockLLMProvider(),
            config={},
            country_code="DEU",
            technology="onshore_wind"
        )

        print(f"\nAgent initialized:")
        print(f"  Country: {agent2.runtime_config['country']['name']}")
        print(f"  Technology: {agent2.runtime_config['technology']['name']}")
        print(f"  Policy Handler: {type(agent2.policy_handler).__name__}")
        print(f"  Resource Fetcher: {type(agent2.resource_fetcher).__name__}")

        # Execute research
        input_data2 = {
            "latitude": 48.0,
            "longitude": 11.0,
            "capacity_mw": 150
        }

        result2 = await agent2.execute(input_data2)

        print(f"\nResults:")
        print(f"  Location: ({result2['location']['latitude']}, {result2['location']['longitude']})")
        print(f"  Policy - EEG Tariff: €{result2['policy_data']['incentives']['base_tariff_eur_per_mwh']}/MWh")
        print(f"  Resource - Wind Speed: {result2['resource_data']['resource_data']['avg_wind_speed_m_s']} m/s")
        print(f"  Overall Confidence: {result2['data_completeness']['overall_confidence']}")

        # Test 3: USA + Wind (same country, different technology)
        print("\n" + "=" * 70)
        print("TEST 3: USA + Onshore Wind (Same country, different tech)")
        print("=" * 70)

        agent3 = ResearchAgent(
            llm_provider=MockLLMProvider(),
            config={},
            country_code="USA",
            technology="onshore_wind"
        )

        print(f"  Policy Handler: {type(agent3.policy_handler).__name__} (Same as Test 1)")
        print(f"  Resource Fetcher: {type(agent3.resource_fetcher).__name__} (Different from Test 1)")

        result3 = await agent3.execute(input_data)
        print(f"\n  Policy - PTC: ${result3['policy_data']['incentives']['federal_ptc_usd_per_mwh']}/MWh")
        print(f"  Resource - Wind Speed: {result3['resource_data']['resource_data']['avg_wind_speed_m_s']} m/s")

        # Test 4: Germany + Solar (same technology, different country)
        print("\n" + "=" * 70)
        print("TEST 4: Germany + Solar PV (Different country, same tech)")
        print("=" * 70)

        agent4 = ResearchAgent(
            llm_provider=MockLLMProvider(),
            config={},
            country_code="DEU",
            technology="solar_pv"
        )

        print(f"  Policy Handler: {type(agent4.policy_handler).__name__} (Different from Test 1)")
        print(f"  Resource Fetcher: {type(agent4.resource_fetcher).__name__} (Same as Test 1)")

        result4 = await agent4.execute(input_data2)
        print(f"\n  Policy - EEG Tariff: €{result4['policy_data']['incentives']['base_tariff_eur_per_mwh']}/MWh")
        print(f"  Resource - GHI: {result4['resource_data']['resource_data']['avg_ghi_kwh_m2_day']} kWh/m²/day")


    asyncio.run(demo())

    print("\n" + "=" * 70)
    print("✅ HYBRID ARCHITECTURE WORKING PERFECTLY!")
    print("=" * 70)
    print("\n🎯 Key Achievement:")
    print("  ONE ResearchAgent class works for:")
    print("    ✓ 2 countries × 2 technologies = 4 combinations")
    print("    ✓ Add 1 country = works for both technologies instantly")
    print("    ✓ Add 1 technology = works for both countries instantly")
    print("    ✓ NO code duplication")
    print("    ✓ NO breaking changes")
    print("\n📈 Scaling:")
    print("  Specialized Agents: 100 countries × 5 tech = 1,000 agent files")
    print("  Hybrid (This):      100 handlers + 5 fetchers = 105 files")
    print("  Reduction:          90% less code!")
    print("=" * 70)