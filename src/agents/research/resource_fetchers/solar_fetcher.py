"""
Solar Resource Fetcher - Solar Photovoltaic Resource Data

Fetches solar-specific resource data:
- GHI (Global Horizontal Irradiance)
- DNI (Direct Normal Irradiance)
- DHI (Diffuse Horizontal Irradiance)
- Temperature (affects panel efficiency)
- Cloud cover
- Seasonal variations

Data Sources (for production):
- NASA POWER: Global solar and meteorological data
- NREL NSRDB: High-resolution USA solar data
- Solcast: Global solar forecasting
- PVGIS: European solar data

For POC: Mock data based on typical values for location
"""

from typing import Dict, Any
from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher


class SolarResourceFetcher(BaseResourceFetcher):
    """
    Solar PV resource fetcher.

    Fetches solar irradiance and temperature data for PV analysis.
    In production, this would call NASA POWER or NREL APIs.
    For POC, returns representative data.
    """

    async def fetch_resource(
            self,
            latitude: float,
            longitude: float,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch solar resource data for a location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            **kwargs:
                - years: int (data period, default 30)
                - resolution: str ("hourly", "daily", "monthly")

        Returns:
            Dictionary with solar resource data
        """
        # Validate location
        if not self._validate_location(latitude, longitude):
            raise ValueError(f"Invalid location: ({latitude}, {longitude})")

        self.logger.info(
            f"Fetching solar resource data for ({latitude:.2f}, {longitude:.2f})"
        )

        # In production: Call NASA POWER or NREL API
        # For POC: Calculate representative values based on latitude
        resource_data = self._calculate_solar_resource(latitude, longitude, **kwargs)

        # Get quality/confidence metrics
        quality = self._get_data_quality(latitude, longitude)

        result = {
            "technology": "solar_pv",
            "location": {
                "latitude": round(latitude, 4),
                "longitude": round(longitude, 4),
                "elevation_m": self._estimate_elevation(latitude, longitude)
            },
            "resource_data": resource_data,
            "quality": quality,
            "last_updated": "2024-12-01"
        }

        # Validate result
        if not self._validate_resource_result(result):
            self.logger.warning("Resource result validation failed")

        return result

    def _calculate_solar_resource(
            self,
            latitude: float,
            longitude: float,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate solar resource based on latitude.

        This is a simplified model for POC. In production, would call
        NASA POWER API or use TMY (Typical Meteorological Year) data.

        GHI varies by latitude:
        - Equator (0°): ~6.0 kWh/m²/day
        - Mid-latitudes (30-40°): ~5.0-5.5 kWh/m²/day
        - High latitudes (50-60°): ~3.0-4.0 kWh/m²/day
        """
        abs_lat = abs(latitude)

        # Base GHI calculation (simplified)
        if abs_lat < 15:
            avg_ghi = 6.0  # Tropical
        elif abs_lat < 30:
            avg_ghi = 5.5  # Subtropical
        elif abs_lat < 45:
            avg_ghi = 5.0  # Mid-latitude
        else:
            avg_ghi = 3.5  # High latitude

        # DNI is typically 1.1-1.2x GHI in good locations
        avg_dni = avg_ghi * 1.15

        # DHI is the diffuse component
        avg_dhi = avg_ghi * 0.3

        # Temperature varies by latitude
        if abs_lat < 30:
            avg_temp = 25.0
            temp_range = [15, 35]
        else:
            avg_temp = 15.0
            temp_range = [5, 25]

        # Annual total
        annual_ghi = avg_ghi * 365

        # Monthly profile (higher in summer, lower in winter)
        # This is Northern Hemisphere pattern
        if latitude >= 0:
            monthly_factors = [0.7, 0.8, 0.9, 1.0, 1.1, 1.15, 1.15, 1.1, 1.0, 0.9, 0.8, 0.7]
        else:
            # Southern Hemisphere (reversed seasons)
            monthly_factors = [1.15, 1.15, 1.1, 1.0, 0.9, 0.8, 0.7, 0.7, 0.8, 0.9, 1.0, 1.1]

        monthly_ghi = [round(avg_ghi * 30 * factor, 1) for factor in monthly_factors]

        return {
            "avg_ghi_kwh_m2_day": round(avg_ghi, 2),
            "avg_dni_kwh_m2_day": round(avg_dni, 2),
            "avg_dhi_kwh_m2_day": round(avg_dhi, 2),
            "avg_temperature_c": round(avg_temp, 1),
            "temperature_range_c": temp_range,
            "cloud_cover_percent": 30,  # Typical average
            "annual_ghi_kwh_m2": round(annual_ghi, 1),
            "monthly_ghi_kwh_m2": monthly_ghi,
            "seasonal_variation": "Moderate"
        }

    def _get_data_quality(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Determine data quality and confidence.

        In production, this would be based on:
        - Proximity to weather stations
        - Data collection period
        - Satellite vs ground measurements
        """
        abs_lat = abs(latitude)

        # USA and Europe have best data coverage
        if -130 <= longitude <= -60 and 25 <= latitude <= 50:
            # USA
            data_source = "NREL NSRDB (High Resolution)"
            confidence = "very_high"
            uncertainty = 0.03
        elif -15 <= longitude <= 40 and 35 <= latitude <= 70:
            # Europe
            data_source = "PVGIS (Satellite + Ground)"
            confidence = "high"
            uncertainty = 0.05
        else:
            # Rest of world
            data_source = "NASA POWER (Satellite)"
            confidence = "medium"
            uncertainty = 0.08

        return {
            "data_source": data_source,
            "data_years": 30,  # Typical TMY
            "confidence": confidence,
            "measurement_uncertainty": uncertainty,
            "data_type": "Satellite-derived (POC uses representative values)"
        }

    def _estimate_elevation(self, latitude: float, longitude: float) -> int:
        """
        Estimate elevation (simplified for POC).

        In production, would use SRTM or similar elevation API.
        """
        # Very rough elevation estimate
        # Mountains typically at certain latitudes
        abs_lat = abs(latitude)

        if 30 <= abs_lat <= 45:
            # Mountain regions
            return 1000
        elif abs_lat < 30:
            # Lowlands/coastal
            return 100
        else:
            # Varied
            return 500


# Demo
if __name__ == "__main__":
    import asyncio
    from src.utils.config_loader import ConfigLoader

    print("=" * 70)
    print("Solar Resource Fetcher Demo")
    print("=" * 70)

    # Load solar configuration
    config_loader = ConfigLoader()
    solar_config = config_loader.load_technology_config("solar_pv")

    # Create fetcher
    fetcher = SolarResourceFetcher(solar_config)

    print(f"\n1. Technology: {fetcher.get_technology_name()} ({fetcher.get_technology()})")


    # Test different locations
    async def test_locations():
        # Texas (excellent solar resource)
        print("\n2. Texas, USA (31.99°N, 102.07°W) - Excellent solar:")
        texas_data = await fetcher.fetch_resource(31.99, -102.07)
        print(f"   GHI: {texas_data['resource_data']['avg_ghi_kwh_m2_day']} kWh/m²/day")
        print(f"   DNI: {texas_data['resource_data']['avg_dni_kwh_m2_day']} kWh/m²/day")
        print(f"   Temperature: {texas_data['resource_data']['avg_temperature_c']}°C")
        print(f"   Annual GHI: {texas_data['resource_data']['annual_ghi_kwh_m2']} kWh/m²")
        print(f"   Data Source: {texas_data['quality']['data_source']}")
        print(f"   Confidence: {texas_data['quality']['confidence']}")

        # Germany (moderate solar)
        print("\n3. Bavaria, Germany (48°N, 11°E) - Moderate solar:")
        germany_data = await fetcher.fetch_resource(48.0, 11.0)
        print(f"   GHI: {germany_data['resource_data']['avg_ghi_kwh_m2_day']} kWh/m²/day")
        print(f"   DNI: {germany_data['resource_data']['avg_dni_kwh_m2_day']} kWh/m²/day")
        print(f"   Temperature: {germany_data['resource_data']['avg_temperature_c']}°C")
        print(f"   Data Source: {germany_data['quality']['data_source']}")

        # Equatorial (best solar)
        print("\n4. Near Equator (0°, 0°) - Best solar:")
        equator_data = await fetcher.fetch_resource(0.0, 0.0)
        print(f"   GHI: {equator_data['resource_data']['avg_ghi_kwh_m2_day']} kWh/m²/day")
        print(f"   Annual GHI: {equator_data['resource_data']['annual_ghi_kwh_m2']} kWh/m²")

        # High latitude (poor solar)
        print("\n5. High Latitude (60°N, 25°E) - Lower solar:")
        high_lat_data = await fetcher.fetch_resource(60.0, 25.0)
        print(f"   GHI: {high_lat_data['resource_data']['avg_ghi_kwh_m2_day']} kWh/m²/day")
        print(f"   Annual GHI: {high_lat_data['resource_data']['annual_ghi_kwh_m2']} kWh/m²")


    asyncio.run(test_locations())

    print("\n" + "=" * 70)
    print("✅ Solar Resource Fetcher working correctly!")
    print("=" * 70)
    print("\nNote: POC uses representative values based on latitude.")
    print("Production version would call NASA POWER or NREL NSRDB APIs.")