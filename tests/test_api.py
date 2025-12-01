"""
Quick API Test Script

Tests all country + technology combinations.
"""

import requests
import json
from typing import Dict, Any

API_URL = "http://localhost:8000/api/v1"


def analyze(country: str, technology: str, lat: float, lon: float, capacity: float = 100):
    """Call the API and return results."""
    response = requests.post(
        f"{API_URL}/analyze",
        json={
            "country": country,
            "technology": technology,
            "latitude": lat,
            "longitude": lon,
            "capacity_mw": capacity
        }
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def print_results(name: str, result: Dict[str, Any]):
    """Pretty print results."""
    print(f"\n{'=' * 70}")
    print(f"📊 {name}")
    print(f"{'=' * 70}")
    print(f"  LCOE: ${result['lcoe']:.2f}/MWh")
    print(f"  IRR: {result['irr']:.1f}%")
    print(f"  NPV: ${result['npv']:,.0f}")
    print(f"  Capacity Factor: {result['capacity_factor'] * 100:.1f}%")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Time: {result['execution_metrics']['total_time_seconds']:.3f}s")


# Test all combinations
print("🚀 Testing ROI API - All Combinations")
print("=" * 70)

# 1. USA + Solar
result = analyze("USA", "solar_pv", 31.99, -102.07, 100)
if result:
    print_results("USA + Solar PV (100 MW)", result)

# 2. USA + Wind
result = analyze("USA", "onshore_wind", 31.99, -102.07, 150)
if result:
    print_results("USA + Onshore Wind (150 MW)", result)

# 3. Germany + Solar
result = analyze("DEU", "solar_pv", 48.0, 11.0, 100)
if result:
    print_results("Germany + Solar PV (100 MW)", result)

# 4. Germany + Wind
result = analyze("DEU", "onshore_wind", 54.0, 8.0, 150)
if result:
    print_results("Germany + Onshore Wind (150 MW)", result)

# 5. India + Solar
result = analyze("IND", "solar_pv", 23.0, 72.0, 100)
if result:
    print_results("India + Solar PV (100 MW)", result)

# 6. India + Wind
result = analyze("IND", "onshore_wind", 23.0, 72.0, 150)
if result:
    print_results("India + Onshore Wind (150 MW)", result)

print("\n" + "=" * 70)
print("✅ All tests complete!")
print("=" * 70)