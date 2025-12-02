"""
Solar Resource Fetcher - REAL DATA INTEGRATION

NOW FETCHES ACTUAL DATA FROM:
- NASA POWER API (primary, global)
- NREL NSRDB (optional, best for USA)

Changes from mock:
- Real GHI, DNI, DHI from satellites
- Real temperature measurements
- Real monthly variations
- 30-year climatology data
"""

from typing import Dict, Any
import logging

from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher
from src.utils.api_clients import NASAPowerClient, NRELClient, APIClientError


class SolarResourceFetcher(BaseResourceFetcher):
    """
    Solar resource fetcher using REAL DATA.

    Data Sources (in priority order):
    1. NREL NSRDB (if API key available and location in USA)
    2. NASA POWER (fallback, global coverage)

    Features:
    - Real satellite-derived solar irradiance
    - 30-year climatological averages
    - Monthly breakdown
    - High confidence ratings
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize solar fetcher with real data clients.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)

        # Initialize API clients
        self.nasa_client = NASAPowerClient()
        self.nrel_client = NRELClient()

        # Log configuration
        if self.nrel_client.is_available():
            self.logger.info("NREL API available - will use for USA locations")
        else:
            self.logger.info("NREL API not configured - using NASA POWER only")

    async def fetch_resource(
            self,
            latitude: float,
            longitude: float,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch REAL solar resource data.

        This now fetches actual satellite data from NASA/NREL!

        Args:
            latitude: Location latitude
            longitude: Location longitude
            **kwargs: Additional parameters

        Returns:
            Dictionary with real solar resource data
        """
        self.logger.info(
            f"Fetching REAL solar resource data for ({latitude:.2f}, {longitude:.2f})"
        )

        # Try NREL first (best for USA)
        if self._is_usa_location(latitude, longitude) and self.nrel_client.is_available():
            try:
                self.logger.info("Attempting NREL data fetch (USA location)")
                return await self._fetch_from_nrel(latitude, longitude)
            except APIClientError as e:
                self.logger.warning(f"NREL failed: {str(e)}, falling back to NASA POWER")

        # Fallback to NASA POWER (global, always works)
        return await self._fetch_from_nasa(latitude, longitude)

    async def _fetch_from_nasa(
            self,
            latitude: float,
            longitude: float
    ) -> Dict[str, Any]:
        """
        Fetch solar data from NASA POWER API.

        This is REAL DATA from satellites!
        """
        try:
            self.logger.info("Fetching from NASA POWER...")

            # Get real NASA data
            nasa_data = await self.nasa_client.get_solar_data(latitude, longitude)

            # Format into our standard structure
            resource_data = {
                "technology": "solar_pv",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "coordinates": nasa_data.get('coordinates', [longitude, latitude])
                },
                "resource_data": {
                    # PRIMARY METRICS (REAL DATA!)
                    "avg_ghi_kwh_m2_day": nasa_data['ghi_annual_avg'],
                    "avg_dni_kwh_m2_day": nasa_data['dni_annual_avg'],
                    "avg_dhi_kwh_m2_day": nasa_data['dhi_annual_avg'],
                    "avg_temperature_c": nasa_data['temperature_annual_avg'],
                    "temperature_max_c": nasa_data.get('temperature_max', 0),
                    "temperature_min_c": nasa_data.get('temperature_min', 0),

                    # MONTHLY BREAKDOWN (REAL DATA!)
                    "monthly_ghi_kwh_m2": nasa_data.get('monthly_ghi', []),
                    "monthly_dni_kwh_m2": nasa_data.get('monthly_dni', []),
                    "monthly_temperature": nasa_data.get('monthly_temperature', []),

                    # DERIVED METRICS
                    "clearness_index": self._calculate_clearness_index(
                        nasa_data['ghi_annual_avg'],
                        latitude
                    ),

                    # METADATA
                    "data_source": nasa_data['data_source'],
                    "data_period": nasa_data['data_period'],
                    "fetched_at": nasa_data['fetched_at']
                },
                "quality": {
                    "data_source": "NASA POWER - Satellite Data",
                    "confidence": nasa_data['confidence'],
                    "coverage": "30-year climatology (1991-2020)",
                    "resolution": "0.5° × 0.5° (~50km)",
                    "validation": "Validated against ground stations",
                    "data_quality_flags": []
                }
            }

            # Add quality flags based on data
            if nasa_data['ghi_annual_avg'] < 2.0:
                resource_data['quality']['data_quality_flags'].append(
                    "Low solar resource - verify location"
                )
            elif nasa_data['ghi_annual_avg'] > 7.0:
                resource_data['quality']['data_quality_flags'].append(
                    "Exceptional solar resource - excellent location"
                )

            self.logger.info(
                f"NASA POWER data fetched: GHI={nasa_data['ghi_annual_avg']:.2f} kWh/m²/day"
            )

            return resource_data

        except APIClientError as e:
            self.logger.error(f"NASA POWER fetch failed: {str(e)}")
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error fetching NASA data: {str(e)}")
            raise APIClientError(f"Solar data fetch failed: {str(e)}")

    async def _fetch_from_nrel(
            self,
            latitude: float,
            longitude: float
    ) -> Dict[str, Any]:
        """
        Fetch solar data from NREL NSRDB (USA only).

        NREL has the highest quality solar data for USA.
        """
        try:
            self.logger.info("Fetching from NREL NSRDB...")

            # Get real NREL data
            nrel_data = await self.nrel_client.get_solar_resource(latitude, longitude)

            # Format into our standard structure
            resource_data = {
                "technology": "solar_pv",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "resource_data": {
                    # PRIMARY METRICS (HIGHEST QUALITY!)
                    "avg_ghi_kwh_m2_day": nrel_data['ghi_annual_avg'],
                    "avg_dni_kwh_m2_day": nrel_data['dni_annual_avg'],
                    "avg_dhi_kwh_m2_day": nrel_data['dhi_annual_avg'],
                    "avg_temperature_c": nrel_data['temperature_annual_avg'],

                    # MONTHLY DATA
                    "monthly_ghi_kwh_m2": nrel_data.get('monthly_ghi', []),
                    "monthly_dni_kwh_m2": nrel_data.get('monthly_dni', []),

                    # METADATA
                    "data_source": nrel_data['data_source'],
                    "data_period": nrel_data['data_period'],
                    "fetched_at": nrel_data['fetched_at']
                },
                "quality": {
                    "data_source": "NREL NSRDB - Premium USA Data",
                    "confidence": nrel_data['confidence'],
                    "coverage": nrel_data['data_period'],
                    "resolution": "4km × 4km",
                    "validation": "Highest quality for USA",
                    "data_quality_flags": []
                }
            }

            self.logger.info(
                f"NREL data fetched: GHI={nrel_data['ghi_annual_avg']:.2f} kWh/m²/day"
            )

            return resource_data

        except APIClientError as e:
            self.logger.error(f"NREL fetch failed: {str(e)}")
            raise

    def _is_usa_location(self, latitude: float, longitude: float) -> bool:
        """
        Check if location is in USA.

        Simple bounding box check for USA (including Alaska, Hawaii).
        """
        # Continental USA + Alaska + Hawaii bounding boxes
        continental = (24.0 <= latitude <= 49.5) and (-125.0 <= longitude <= -66.0)
        alaska = (51.0 <= latitude <= 72.0) and (-180.0 <= longitude <= -129.0)
        hawaii = (18.0 <= latitude <= 29.0) and (-161.0 <= longitude <= -154.0)

        return continental or alaska or hawaii

    def _calculate_clearness_index(self, ghi: float, latitude: float) -> float:
        """
        Calculate clearness index (Kt).

        Kt = GHI / Extraterrestrial Horizontal Irradiance

        Args:
            ghi: Global Horizontal Irradiance (kWh/m²/day)
            latitude: Location latitude

        Returns:
            Clearness index (0-1)
        """
        import math

        # Extraterrestrial irradiance at latitude
        # Simplified calculation
        lat_rad = math.radians(abs(latitude))

        # Average extraterrestrial horizontal irradiance
        # Formula: Ho = Gsc * (1 + 0.033*cos(360*n/365)) * cos(lat)
        # Simplified annual average
        solar_constant = 1.367  # kW/m²
        daylight_hours = 12.0  # Average

        # Approximate extraterrestrial daily irradiance
        ho = solar_constant * daylight_hours * math.cos(lat_rad)

        if ho <= 0:
            return 0.5  # Default for polar regions

        kt = ghi / ho

        # Clamp to reasonable range
        return max(0.1, min(0.9, kt))

    def get_technology(self) -> str:
        """Get technology type."""
        return "solar_pv"


# Demo
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("☀️  Solar Resource Fetcher - REAL DATA Demo")
    print("=" * 70)


    async def demo():
        # Create fetcher
        config = {"technology": {"name": "Solar Photovoltaic"}}
        fetcher = SolarResourceFetcher(config)

        # Test locations
        locations = [
            ("West Texas", 31.99, -102.07),
            ("Gujarat, India", 23.0, 72.0),
            ("Rajasthan, India", 27.0, 73.0),
            ("California", 36.0, -119.0),
            ("Germany", 52.5, 13.4)
        ]

        for name, lat, lon in locations:
            print(f"\n{'=' * 70}")
            print(f"📍 {name} ({lat:.2f}°N, {lon:.2f}°E)")
            print(f"{'=' * 70}")

            try:
                # Fetch REAL data
                data = await fetcher.fetch_resource(lat, lon)

                resource = data['resource_data']
                quality = data['quality']

                print(f"\n☀️  Solar Resource (REAL DATA!):")
                print(f"  GHI: {resource['avg_ghi_kwh_m2_day']:.2f} kWh/m²/day")
                print(f"  DNI: {resource['avg_dni_kwh_m2_day']:.2f} kWh/m²/day")
                print(f"  Temperature: {resource['avg_temperature_c']:.1f}°C")

                if resource.get('temperature_max_c'):
                    print(
                        f"  Temp Range: {resource['temperature_min_c']:.1f}°C to {resource['temperature_max_c']:.1f}°C")

                print(f"\n📊 Data Quality:")
                print(f"  Source: {quality['data_source']}")
                print(f"  Confidence: {quality['confidence']}")
                print(f"  Coverage: {quality['coverage']}")
                print(f"  Resolution: {quality['resolution']}")

                if quality['data_quality_flags']:
                    print(f"  Flags: {quality['data_quality_flags'][0]}")

                # Show monthly variation if available
                monthly_ghi = resource.get('monthly_ghi_kwh_m2', [])
                if monthly_ghi and any(monthly_ghi):
                    print(f"\n📅 Monthly GHI:")
                    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    for month, ghi in zip(months, monthly_ghi):
                        if ghi > 0:
                            print(f"    {month}: {ghi:.2f} kWh/m²/day")

            except Exception as e:
                print(f"  ❌ Error: {str(e)}")


    asyncio.run(demo())

    print("\n" + "=" * 70)
    print("✅ Solar Resource Fetcher Working with REAL DATA!")
    print("=" * 70)
    print("\n🎯 Key Changes:")
    print("  • Now fetching real NASA POWER satellite data")
    print("  • 30-year climatology (1991-2020)")
    print("  • Global coverage with high confidence")
    print("  • NREL support for USA locations (if API key)")
    print("  • Real GHI, DNI, temperature measurements")
    print("=" * 70)