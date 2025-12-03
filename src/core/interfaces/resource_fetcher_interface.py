"""
Resource Fetcher Interface - Technology-Specific Resource Data

This interface defines the contract for technology-specific resource fetchers.
Each technology (Solar, Wind, Hydro, etc.) has its own implementation.

Why separate interface?
- Technologies require VERY different resource data
- Solar: GHI, DNI, temperature, cloud cover
- Wind: Wind speed, power density, Weibull parameters
- Hydro: River flow, hydraulic head, seasonal variation
- Offshore Wind: Marine data (wave height, water depth)

Design Pattern: Strategy Pattern
- Resource fetchers are interchangeable strategies
- Factory creates the right fetcher based on technology code
- Agent doesn't know which fetcher it's using

Example:
    # Solar fetcher gets irradiance data
    solar_fetcher = SolarResourceFetcher(config)
    resource = await solar_fetcher.fetch_resource(31.99, -102.07)

    # Wind fetcher gets wind speed data
    wind_fetcher = WindResourceFetcher(config)
    resource = await wind_fetcher.fetch_resource(31.99, -102.07)

    # Both return consistent structure, different data
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IResourceFetcher(ABC):
    """
    Interface for technology-specific resource fetchers.

    Each technology implements this to fetch its specific resource data:
    - Solar: Irradiance (GHI, DNI), temperature
    - Wind: Wind speed, power density, Weibull distribution
    - Hydro: River flow, head, seasonal patterns
    - Geothermal: Underground temperature, geology

    All fetchers must return data in a consistent structure.
    """

    @abstractmethod
    async def fetch_resource(
            self,
            latitude: float,
            longitude: float,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch resource data for a specific location.

        This is where technology-specific logic lives:
        - Solar: Call NASA POWER or NREL NSRDB for irradiance
        - Wind: Call Global Wind Atlas or NREL Wind Toolkit
        - Hydro: Call USGS Water Data or regional databases

        Args:
            latitude: Location latitude (decimal degrees)
            longitude: Location longitude (decimal degrees)
            **kwargs: Technology-specific parameters
                - hub_height_m: float (for wind, measurement height)
                - water_depth_m: float (for offshore wind/hydro)
                - years: int (how many years of data)
                - data_resolution: str ("hourly", "daily", "monthly")

        Returns:
            Dictionary containing resource data:
            {
                "technology": "solar_pv",
                "location": {
                    "latitude": 31.99,
                    "longitude": -102.07,
                    "elevation_m": 850
                },
                "resource_data": {
                    "avg_ghi_kwh_m2_day": 5.5,
                    "avg_dni_kwh_m2_day": 6.2,
                    "avg_temperature_c": 25.0,
                    "annual_ghi_kwh_m2": 2007.5
                },
                "quality": {
                    "data_source": "NASA POWER",
                    "data_years": 30,
                    "confidence": "high",
                    "measurement_uncertainty": 0.05
                },
                "last_updated": "2024-12-01"
            }

        Example:
            >>> fetcher = SolarResourceFetcher(config)
            >>> resource = await fetcher.fetch_resource(31.99, -102.07)
            >>> print(resource["resource_data"]["avg_ghi_kwh_m2_day"])
            5.5
        """
        pass

    @abstractmethod
    def get_technology(self) -> str:
        """
        Get the technology code this fetcher is for.

        Returns:
            Technology code (e.g., "solar_pv", "onshore_wind", "hydro")

        Example:
            >>> fetcher = SolarResourceFetcher(config)
            >>> fetcher.get_technology()
            'solar_pv'
        """
        pass


# Example result structures for documentation

SOLAR_RESULT_EXAMPLE = {
    "technology": "solar_pv",
    "location": {
        "latitude": 31.99,
        "longitude": -102.07,
        "elevation_m": 850,
        "timezone": "America/Chicago"
    },
    "resource_data": {
        "avg_ghi_kwh_m2_day": 5.5,  # Global Horizontal Irradiance
        "avg_dni_kwh_m2_day": 6.2,  # Direct Normal Irradiance
        "avg_dhi_kwh_m2_day": 1.8,  # Diffuse Horizontal Irradiance
        "avg_temperature_c": 25.0,
        "temperature_range_c": [10, 40],
        "cloud_cover_percent": 30,
        "annual_ghi_kwh_m2": 2007.5,
        "monthly_ghi_kwh_m2": [150, 165, 180, 190, 200, 210, 215, 210, 195, 180, 160, 145]
    },
    "quality": {
        "data_source": "NASA POWER",
        "data_years": 30,
        "confidence": "high",
        "measurement_uncertainty": 0.05
    },
    "last_updated": "2024-12-01"
}

WIND_RESULT_EXAMPLE = {
    "technology": "onshore_wind",
    "location": {
        "latitude": 31.99,
        "longitude": -102.07,
        "elevation_m": 850
    },
    "resource_data": {
        "avg_wind_speed_m_s": 7.5,
        "hub_height_m": 100,
        "wind_power_density_w_m2": 400,
        "weibull_k": 2.0,
        "weibull_c": 8.5,
        "turbulence_intensity": 0.12,
        "wind_rose": {
            "dominant_direction": "SW",
            "direction_distribution": {"N": 0.1, "NE": 0.12, "E": 0.08, "SE": 0.09, "S": 0.13, "SW": 0.18, "W": 0.15, "NW": 0.15}
        },
        "monthly_avg_wind_speed": [7.0, 7.5, 8.0, 7.8, 7.2, 6.8, 6.5, 6.7, 7.0, 7.5, 7.8, 7.3]
    },
    "quality": {
        "data_source": "Global Wind Atlas",
        "data_years": 20,
        "confidence": "high",
        "measurement_uncertainty": 0.08
    },
    "last_updated": "2024-12-01"
}

if __name__ == "__main__":
    print("=" * 70)
    print("Resource Fetcher Interface Demo")
    print("=" * 70)

    print("\nThis interface defines the contract for technology-specific resource fetchers.")

    print("\n" + "=" * 40)
    print("Solar Resource Example:")
    print("=" * 40)
    import json

    print(json.dumps(SOLAR_RESULT_EXAMPLE, indent=2))

    print("\n" + "=" * 40)
    print("Wind Resource Example:")
    print("=" * 40)
    print(json.dumps(WIND_RESULT_EXAMPLE, indent=2))

    print("\n" + "=" * 70)
    print("Key Points:")
    print("- Each technology implements this interface")
    print("- Solar fetcher: Gets GHI, DNI, temperature from NASA POWER")
    print("- Wind fetcher: Gets wind speed, power density from Global Wind Atlas")
    print("- All return consistent structure")
    print("- ResearchAgent doesn't care which fetcher is used")
    print("=" * 70)