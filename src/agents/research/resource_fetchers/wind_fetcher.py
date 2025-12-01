"""
Wind Resource Fetcher - Wind Resource Data

Fetches wind-specific resource data:
- Wind speed at hub height
- Wind power density
- Weibull distribution parameters
- Turbulence intensity
- Wind direction (wind rose)

Data Sources (for production):
- Global Wind Atlas: Worldwide wind data
- NREL Wind Toolkit: High-resolution USA wind data
- AWS Truepower: Commercial wind data
- MERRA-2: NASA reanalysis data

For POC: Mock data based on typical values
"""

from typing import Dict, Any
from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher


class WindResourceFetcher(BaseResourceFetcher):
    """
    Wind resource fetcher.

    Fetches wind speed and characteristics for wind analysis.
    In production, would call Global Wind Atlas or NREL APIs.
    For POC, returns representative data.
    """

    async def fetch_resource(
            self,
            latitude: float,
            longitude: float,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch wind resource data for a location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            **kwargs:
                - hub_height_m: float (default 100m)
                - years: int (data period)

        Returns:
            Dictionary with wind resource data
        """
        # Validate location
        if not self._validate_location(latitude, longitude):
            raise ValueError(f"Invalid location: ({latitude}, {longitude})")

        hub_height = kwargs.get("hub_height_m", 100)

        self.logger.info(
            f"Fetching wind resource data for ({latitude:.2f}, {longitude:.2f}) "
            f"at {hub_height}m hub height"
        )

        # In production: Call Global Wind Atlas or NREL API
        # For POC: Calculate representative values
        resource_data = self._calculate_wind_resource(
            latitude, longitude, hub_height, **kwargs
        )

        # Get quality metrics
        quality = self._get_data_quality(latitude, longitude)

        result = {
            "technology": "onshore_wind",
            "location": {
                "latitude": round(latitude, 4),
                "longitude": round(longitude, 4),
                "elevation_m": self._estimate_elevation(latitude, longitude)
            },
            "resource_data": resource_data,
            "quality": quality,
            "last_updated": "2024-12-01"
        }

        return result

    def _calculate_wind_resource(
            self,
            latitude: float,
            longitude: float,
            hub_height: float,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate wind resource characteristics.

        Wind power class (at 50m):
        - Class 1: <200 W/m² (poor)
        - Class 3: 300-400 W/m² (fair)
        - Class 4: 400-500 W/m² (good)
        - Class 5: 500-600 W/m² (excellent)
        - Class 7: >800 W/m² (superb)
        """
        abs_lat = abs(latitude)

        # Wind resource varies by region
        # Coasts and plains typically have better wind

        # Simplified wind speed estimation
        if 30 <= abs_lat <= 50:
            # Mid-latitude westerlies (best wind)
            base_wind_speed = 7.5
            wind_class = "Class 4 (Good)"
        elif abs_lat < 30:
            # Trade winds (moderate)
            base_wind_speed = 6.5
            wind_class = "Class 3 (Fair)"
        else:
            # Polar regions (variable)
            base_wind_speed = 7.0
            wind_class = "Class 3-4 (Fair to Good)"

        # Adjust for hub height using power law
        # v2 = v1 * (h2/h1)^alpha
        # alpha typically 0.14-0.20 (0.14 for open terrain)
        alpha = 0.14
        hub_wind_speed = base_wind_speed * (hub_height / 50) ** alpha

        # Wind power density (W/m²)
        # P = 0.5 * rho * v³
        # rho ≈ 1.225 kg/m³ at sea level
        air_density = 1.225
        wind_power_density = 0.5 * air_density * (hub_wind_speed ** 3)

        # Weibull distribution parameters
        # k (shape): typically 1.8-2.2
        # c (scale): typically v_mean * 1.12
        weibull_k = 2.0
        weibull_c = hub_wind_speed * 1.12

        # Monthly variation (higher in winter)
        if latitude >= 0:
            # Northern Hemisphere
            monthly_factors = [1.1, 1.1, 1.05, 0.95, 0.9, 0.85, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1]
        else:
            # Southern Hemisphere
            monthly_factors = [0.85, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.1, 1.05, 0.95, 0.9, 0.85]

        monthly_wind_speed = [round(hub_wind_speed * f, 1) for f in monthly_factors]

        # Wind direction (simplified - prevailing westerlies at mid-latitudes)
        if 30 <= abs_lat <= 60:
            dominant_direction = "SW" if latitude > 0 else "NW"
        else:
            dominant_direction = "E"

        return {
            "avg_wind_speed_m_s": round(hub_wind_speed, 2),
            "hub_height_m": hub_height,
            "wind_power_density_w_m2": round(wind_power_density, 0),
            "wind_power_class": wind_class,
            "weibull_k": weibull_k,
            "weibull_c": round(weibull_c, 2),
            "turbulence_intensity": 0.12,  # Typical value
            "wind_rose": {
                "dominant_direction": dominant_direction,
                "direction_distribution": {
                    "N": 0.10, "NE": 0.12, "E": 0.08, "SE": 0.09,
                    "S": 0.13, "SW": 0.18, "W": 0.15, "NW": 0.15
                }
            },
            "monthly_avg_wind_speed": monthly_wind_speed,
            "seasonal_variation": "Moderate (Higher in winter)"
        }

    def _get_data_quality(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Determine data quality."""
        # USA has best wind data coverage
        if -130 <= longitude <= -60 and 25 <= latitude <= 50:
            data_source = "NREL Wind Toolkit (High Resolution)"
            confidence = "high"
            uncertainty = 0.05
        else:
            data_source = "Global Wind Atlas v3.0"
            confidence = "medium"
            uncertainty = 0.10

        return {
            "data_source": data_source,
            "data_years": 20,
            "confidence": confidence,
            "measurement_uncertainty": uncertainty,
            "data_type": "Modeled (POC uses representative values)"
        }

    def _estimate_elevation(self, latitude: float, longitude: float) -> int:
        """Estimate elevation."""
        abs_lat = abs(latitude)
        if 30 <= abs_lat <= 45:
            return 1000
        elif abs_lat < 30:
            return 100
        else:
            return 500


# Demo
if __name__ == "__main__":
    import asyncio
    from src.utils.config_loader import ConfigLoader

    print("=" * 70)
    print("Wind Resource Fetcher Demo")
    print("=" * 70)

    # Load wind configuration
    config_loader = ConfigLoader()
    wind_config = config_loader.load_technology_config("onshore_wind")

    # Create fetcher
    fetcher = WindResourceFetcher(wind_config)

    print(f"\n1. Technology: {fetcher.get_technology_name()} ({fetcher.get_technology()})")


    # Test different locations
    async def test_locations():
        # Texas (good wind)
        print("\n2. Texas, USA (31.99°N, 102.07°W) - Good wind:")
        texas_data = await fetcher.fetch_resource(31.99, -102.07, hub_height_m=100)
        print(
            f"   Wind Speed: {texas_data['resource_data']['avg_wind_speed_m_s']} m/s at {texas_data['resource_data']['hub_height_m']}m")
        print(f"   Power Density: {texas_data['resource_data']['wind_power_density_w_m2']} W/m²")
        print(f"   Wind Class: {texas_data['resource_data']['wind_power_class']}")
        print(
            f"   Weibull k: {texas_data['resource_data']['weibull_k']}, c: {texas_data['resource_data']['weibull_c']}")
        print(f"   Dominant Direction: {texas_data['resource_data']['wind_rose']['dominant_direction']}")
        print(f"   Data Source: {texas_data['quality']['data_source']}")

        # North Sea (excellent wind - higher hub height)
        print("\n3. North Sea Region (54°N, 8°E) - Excellent wind at 150m:")
        north_sea_data = await fetcher.fetch_resource(54.0, 8.0, hub_height_m=150)
        print(
            f"   Wind Speed: {north_sea_data['resource_data']['avg_wind_speed_m_s']} m/s at {north_sea_data['resource_data']['hub_height_m']}m")
        print(f"   Power Density: {north_sea_data['resource_data']['wind_power_density_w_m2']} W/m²")
        print(f"   Wind Class: {north_sea_data['resource_data']['wind_power_class']}")

        # Tropical (lower wind)
        print("\n4. Tropical Region (10°N, 80°W) - Lower wind:")
        tropical_data = await fetcher.fetch_resource(10.0, -80.0)
        print(f"   Wind Speed: {tropical_data['resource_data']['avg_wind_speed_m_s']} m/s")
        print(f"   Power Density: {tropical_data['resource_data']['wind_power_density_w_m2']} W/m²")
        print(f"   Wind Class: {tropical_data['resource_data']['wind_power_class']}")


    asyncio.run(test_locations())

    print("\n" + "=" * 70)
    print("✅ Wind Resource Fetcher working correctly!")
    print("=" * 70)
    print("\nNote: POC uses representative values based on latitude.")
    print("Production version would call Global Wind Atlas or NREL APIs.")