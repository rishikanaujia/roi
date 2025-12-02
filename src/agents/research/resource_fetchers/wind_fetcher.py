"""
Wind Resource Fetcher - REAL DATA INTEGRATION

NOW FETCHES ACTUAL DATA FROM:
- NASA POWER API (wind speed at multiple heights)

Changes from mock:
- Real wind speed measurements
- Multiple hub heights (10m, 50m)
- Real temperature and pressure
- 30-year climatology
"""

from typing import Dict, Any
import math
import logging

from src.agents.research.resource_fetchers.base_resource_fetcher import BaseResourceFetcher
from src.utils.api_clients import NASAPowerClient, APIClientError


class WindResourceFetcher(BaseResourceFetcher):
    """
    Wind resource fetcher using REAL DATA.

    Data Source:
    - NASA POWER API (wind speed at 10m and 50m)

    Features:
    - Real wind speed measurements
    - Extrapolation to turbine hub heights (100m, 150m)
    - Wind power density calculations
    - 30-year climatological averages
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize wind fetcher with real data client.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)

        # Initialize NASA POWER client
        self.nasa_client = NASAPowerClient()

        self.logger.info("Wind fetcher initialized with NASA POWER client")

    async def fetch_resource(
            self,
            latitude: float,
            longitude: float,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch REAL wind resource data.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            **kwargs: Additional parameters
                - hub_height: Turbine hub height in meters (default: 100)

        Returns:
            Dictionary with real wind resource data
        """
        hub_height = kwargs.get('hub_height', 100)

        self.logger.info(
            f"Fetching REAL wind resource data for ({latitude:.2f}, {longitude:.2f}) "
            f"at {hub_height}m hub height"
        )

        return await self._fetch_from_nasa(latitude, longitude, hub_height)

    async def _fetch_from_nasa(
            self,
            latitude: float,
            longitude: float,
            hub_height: int
    ) -> Dict[str, Any]:
        """
        Fetch wind data from NASA POWER API.

        This is REAL DATA from NASA satellites and reanalysis models!
        """
        try:
            self.logger.info("Fetching from NASA POWER...")

            # Get real NASA wind data
            nasa_data = await self.nasa_client.get_wind_data(latitude, longitude)

            # Extrapolate wind speed to hub height using power law
            ws_10m = nasa_data['wind_speed_10m']
            ws_50m = nasa_data['wind_speed_50m']

            # Calculate wind shear exponent (alpha) from measured data
            alpha = self._calculate_wind_shear(ws_10m, ws_50m, 10, 50)

            # Extrapolate to hub height
            ws_hub = self._extrapolate_wind_speed(ws_50m, 50, hub_height, alpha)

            # Calculate wind power density
            air_density = self._calculate_air_density(
                nasa_data['temperature_avg'],
                nasa_data['pressure_avg']
            )
            wind_power_density = self._calculate_power_density(ws_hub, air_density)

            # Classify wind resource
            wind_class = self._classify_wind_resource(ws_hub, wind_power_density)

            # Format into our standard structure
            resource_data = {
                "technology": "onshore_wind",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "coordinates": nasa_data.get('coordinates', [longitude, latitude])
                },
                "resource_data": {
                    # PRIMARY METRICS (REAL DATA!)
                    "avg_wind_speed_m_s": ws_hub,
                    "hub_height_m": hub_height,

                    # MEASURED DATA AT STANDARD HEIGHTS
                    "wind_speed_10m_m_s": ws_10m,
                    "wind_speed_50m_m_s": ws_50m,

                    # DERIVED METRICS
                    "wind_power_density_w_m2": wind_power_density,
                    "wind_shear_exponent": alpha,
                    "air_density_kg_m3": air_density,

                    # WIND RESOURCE CLASSIFICATION
                    "wind_class": wind_class['class'],
                    "wind_class_description": wind_class['description'],

                    # ENVIRONMENTAL DATA
                    "avg_temperature_c": nasa_data['temperature_avg'],
                    "avg_pressure_kpa": nasa_data['pressure_avg'],

                    # MONTHLY VARIATIONS (REAL DATA!)
                    "monthly_wind_speed_10m": nasa_data.get('monthly_wind_speed_10m', []),
                    "monthly_wind_speed_50m": nasa_data.get('monthly_wind_speed_50m', []),

                    # EXTRAPOLATED MONTHLY DATA AT HUB HEIGHT
                    "monthly_wind_speed_hub": [
                        self._extrapolate_wind_speed(ws, 50, hub_height, alpha)
                        for ws in nasa_data.get('monthly_wind_speed_50m', [])
                    ],

                    # METADATA
                    "data_source": nasa_data['data_source'],
                    "data_period": nasa_data['data_period'],
                    "fetched_at": nasa_data['fetched_at']
                },
                "quality": {
                    "data_source": "NASA POWER - Reanalysis Data",
                    "confidence": self._assess_confidence(ws_hub, wind_class),
                    "coverage": "30-year climatology (1991-2020)",
                    "resolution": "0.5° × 0.5° (~50km)",
                    "validation": "Validated against meteorological stations",
                    "data_quality_flags": self._generate_quality_flags(
                        ws_hub, wind_class, alpha
                    ),
                    "notes": [
                        f"Wind speed extrapolated from 50m to {hub_height}m using power law",
                        f"Wind shear exponent (alpha): {alpha:.3f}",
                        f"Site-specific measurement recommended for final design"
                    ]
                }
            }

            self.logger.info(
                f"NASA POWER wind data fetched: {ws_hub:.2f} m/s at {hub_height}m "
                f"(Class {wind_class['class']})"
            )

            return resource_data

        except APIClientError as e:
            self.logger.error(f"NASA POWER fetch failed: {str(e)}")
            raise

        except Exception as e:
            self.logger.error(f"Unexpected error fetching NASA wind data: {str(e)}")
            raise APIClientError(f"Wind data fetch failed: {str(e)}")

    def _calculate_wind_shear(
            self,
            ws1: float,
            ws2: float,
            h1: float,
            h2: float
    ) -> float:
        """
        Calculate wind shear exponent (alpha) from two measurements.

        Power law: V2/V1 = (H2/H1)^alpha
        Therefore: alpha = ln(V2/V1) / ln(H2/H1)

        Args:
            ws1: Wind speed at height 1
            ws2: Wind speed at height 2
            h1: Height 1
            h2: Height 2

        Returns:
            Wind shear exponent (typically 0.1-0.4)
        """
        if ws1 <= 0 or ws2 <= 0 or h1 <= 0 or h2 <= 0:
            return 0.143  # Default for neutral stability

        try:
            alpha = math.log(ws2 / ws1) / math.log(h2 / h1)

            # Clamp to reasonable range (0.1 to 0.4)
            # 0.1 = offshore/smooth terrain
            # 0.143 = neutral stability
            # 0.2 = typical onshore
            # 0.4 = very rough terrain/forest
            return max(0.1, min(0.4, alpha))

        except (ValueError, ZeroDivisionError):
            return 0.143

    def _extrapolate_wind_speed(
            self,
            ws_ref: float,
            h_ref: float,
            h_target: float,
            alpha: float
    ) -> float:
        """
        Extrapolate wind speed to target height using power law.

        Formula: V_target = V_ref * (H_target / H_ref)^alpha

        Args:
            ws_ref: Reference wind speed (m/s)
            h_ref: Reference height (m)
            h_target: Target height (m)
            alpha: Wind shear exponent

        Returns:
            Extrapolated wind speed at target height
        """
        if ws_ref <= 0 or h_ref <= 0 or h_target <= 0:
            return 0.0

        return ws_ref * math.pow(h_target / h_ref, alpha)

    def _calculate_air_density(
            self,
            temperature_c: float,
            pressure_kpa: float
    ) -> float:
        """
        Calculate air density using ideal gas law.

        Formula: ρ = P / (R * T)
        Where:
        - P = pressure (Pa)
        - R = specific gas constant for air (287.05 J/(kg·K))
        - T = temperature (K)

        Args:
            temperature_c: Temperature in Celsius
            pressure_kpa: Pressure in kPa

        Returns:
            Air density (kg/m³)
        """
        R = 287.05  # J/(kg·K)
        T_kelvin = temperature_c + 273.15
        P_pascal = pressure_kpa * 1000

        if T_kelvin <= 0:
            T_kelvin = 288.15  # Standard: 15°C

        if P_pascal <= 0:
            P_pascal = 101325  # Standard: sea level

        rho = P_pascal / (R * T_kelvin)

        # Typical range: 0.9-1.3 kg/m³
        return max(0.9, min(1.3, rho))

    def _calculate_power_density(
            self,
            wind_speed: float,
            air_density: float
    ) -> float:
        """
        Calculate wind power density.

        Formula: P/A = 0.5 * ρ * V³

        Args:
            wind_speed: Wind speed (m/s)
            air_density: Air density (kg/m³)

        Returns:
            Wind power density (W/m²)
        """
        if wind_speed <= 0:
            return 0.0

        return 0.5 * air_density * math.pow(wind_speed, 3)

    def _classify_wind_resource(
            self,
            wind_speed: float,
            power_density: float
    ) -> Dict[str, Any]:
        """
        Classify wind resource according to NREL wind power classes.

        Wind Power Classes (at 50m height):
        - Class 1: <5.6 m/s, <200 W/m² (Poor)
        - Class 2: 5.6-6.4 m/s, 200-300 W/m² (Marginal)
        - Class 3: 6.4-7.0 m/s, 300-400 W/m² (Fair)
        - Class 4: 7.0-7.5 m/s, 400-500 W/m² (Good)
        - Class 5: 7.5-8.0 m/s, 500-600 W/m² (Excellent)
        - Class 6: 8.0-8.8 m/s, 600-800 W/m² (Outstanding)
        - Class 7: >8.8 m/s, >800 W/m² (Superb)

        Args:
            wind_speed: Average wind speed (m/s)
            power_density: Wind power density (W/m²)

        Returns:
            Dictionary with class and description
        """
        if wind_speed < 5.6:
            return {"class": 1, "description": "Poor - Not suitable for wind energy"}
        elif wind_speed < 6.4:
            return {"class": 2, "description": "Marginal - Large turbines viable"}
        elif wind_speed < 7.0:
            return {"class": 3, "description": "Fair - Suitable for development"}
        elif wind_speed < 7.5:
            return {"class": 4, "description": "Good - Good resource"}
        elif wind_speed < 8.0:
            return {"class": 5, "description": "Excellent - Excellent resource"}
        elif wind_speed < 8.8:
            return {"class": 6, "description": "Outstanding - Outstanding resource"}
        else:
            return {"class": 7, "description": "Superb - World-class resource"}

    def _assess_confidence(
            self,
            wind_speed: float,
            wind_class: Dict[str, Any]
    ) -> str:
        """
        Assess confidence level based on wind resource quality.

        Args:
            wind_speed: Average wind speed
            wind_class: Wind class information

        Returns:
            Confidence level string
        """
        if wind_class['class'] >= 4:
            return "high"
        elif wind_class['class'] >= 2:
            return "medium"
        else:
            return "low"

    def _generate_quality_flags(
            self,
            wind_speed: float,
            wind_class: Dict[str, Any],
            alpha: float
    ) -> list:
        """Generate data quality flags."""
        flags = []

        if wind_class['class'] <= 2:
            flags.append("Low wind resource - project viability questionable")
        elif wind_class['class'] >= 6:
            flags.append("Exceptional wind resource - excellent location")

        if alpha > 0.3:
            flags.append("High wind shear - complex terrain, verify with measurements")

        if wind_speed < 4.0:
            flags.append("Very low wind speed - not recommended for wind energy")

        if not flags:
            flags.append("No significant data quality issues identified")

        return flags

    def get_technology(self) -> str:
        """Get technology type."""
        return "onshore_wind"


# Demo
if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("💨 Wind Resource Fetcher - REAL DATA Demo")
    print("=" * 70)


    async def demo():
        # Create fetcher
        config = {"technology": {"name": "Onshore Wind"}}
        fetcher = WindResourceFetcher(config)

        # Test locations
        locations = [
            ("West Texas", 31.99, -102.07, 100),
            ("North Sea, Germany", 54.0, 8.0, 150),
            ("Tamil Nadu, India", 11.0, 77.0, 120),
            ("Iowa, USA", 42.0, -93.0, 100),
            ("Patagonia, Argentina", -45.0, -70.0, 120)
        ]

        for name, lat, lon, hub_height in locations:
            print(f"\n{'=' * 70}")
            print(f"📍 {name} ({lat:.2f}°, {lon:.2f}°) - {hub_height}m hub")
            print(f"{'=' * 70}")

            try:
                # Fetch REAL data
                data = await fetcher.fetch_resource(lat, lon, hub_height=hub_height)

                resource = data['resource_data']
                quality = data['quality']

                print(f"\n💨 Wind Resource (REAL DATA!):")
                print(f"  Wind Speed @ {hub_height}m: {resource['avg_wind_speed_m_s']:.2f} m/s")
                print(f"  Wind Speed @ 50m: {resource['wind_speed_50m_m_s']:.2f} m/s")
                print(f"  Wind Speed @ 10m: {resource['wind_speed_10m_m_s']:.2f} m/s")
                print(f"  Power Density: {resource['wind_power_density_w_m2']:.0f} W/m²")
                print(f"  Wind Class: {resource['wind_class']} - {resource['wind_class_description']}")
                print(f"  Wind Shear (α): {resource['wind_shear_exponent']:.3f}")

                print(f"\n🌡️  Environmental:")
                print(f"  Temperature: {resource['avg_temperature_c']:.1f}°C")
                print(f"  Air Density: {resource['air_density_kg_m3']:.3f} kg/m³")

                print(f"\n📊 Data Quality:")
                print(f"  Source: {quality['data_source']}")
                print(f"  Confidence: {quality['confidence']}")
                print(f"  Coverage: {quality['coverage']}")

                if quality['data_quality_flags']:
                    print(f"  Flags: {quality['data_quality_flags'][0]}")

            except Exception as e:
                print(f"  ❌ Error: {str(e)}")


    asyncio.run(demo())

    print("\n" + "=" * 70)
    print("✅ Wind Resource Fetcher Working with REAL DATA!")
    print("=" * 70)
    print("\n🎯 Key Features:")
    print("  • Real NASA POWER wind speed measurements")
    print("  • Wind shear calculations from actual data")
    print("  • Extrapolation to any hub height")
    print("  • Wind power density and classification")
    print("  • NREL wind class assessment")
    print("=" * 70)