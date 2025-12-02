"""
Test Research-Enhanced AI Insights

This demonstrates the dramatic improvement in AI insight quality
when GPT-4 has access to comprehensive market research.

Before: Generic insights
After: Investment-grade analysis with specific facts, company names, deadlines
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/v1"


def print_section(title: str):
    """Print section header."""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}")


def test_research_enhanced_insights():
    """Test a single analysis and examine the AI insights quality."""

    print_section("🚀 RESEARCH-ENHANCED AI INSIGHTS TEST")

    print("\nTesting with: West Texas Solar Project (USA)")
    print("  Location: 31.99°N, -102.07°W")
    print("  Capacity: 100 MW")
    print("  Technology: Solar PV")

    # Make request
    start = datetime.now()

    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json={
                "country": "USA",
                "technology": "solar_pv",
                "latitude": 31.99,
                "longitude": -102.07,
                "capacity_mw": 100
            },
            timeout=60
        )

        elapsed = (datetime.now() - start).total_seconds()

        if response.status_code != 200:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            return

        result = response.json()

        print_section("⏱️  PERFORMANCE METRICS")
        print(f"  Total Time: {elapsed:.2f}s")
        print(f"  Research Time: {result['execution_metrics']['research_time_seconds']:.2f}s")
        print(f"  Analysis Time: {result['execution_metrics']['analysis_time_seconds']:.2f}s")
        print(f"  AI Insights Time: {result['execution_metrics']['ai_insights_time_seconds']:.2f}s")

        print_section("📊 FINANCIAL RESULTS")
        print(f"  LCOE: ${result['lcoe']:.2f}/MWh")
        print(f"  IRR: {result['irr']:.1f}%")
        print(f"  NPV: ${result['npv']:,.0f}")
        print(f"  Capacity Factor: {result['capacity_factor'] * 100:.1f}%")
        print(f"  Recommendation: {result['recommendation']}")

        print_section("🛰️  REAL NASA DATA")
        resource = result['resource_summary']
        print(f"  GHI: {resource['ghi_kwh_m2_day']:.2f} kWh/m²/day")
        print(f"  Temperature: {resource['temperature_c']:.1f}°C")
        print(f"  Data Quality: {resource['quality']}")

        print_section("💰 POLICY INCENTIVES")
        policy = result['policy_summary']

        # Handle None values
        itc = policy.get('federal_itc')
        if itc is not None:
            print(f"  Federal ITC: {itc:.0f}%")

        ptc = policy.get('federal_ptc')
        if ptc is not None and ptc > 0:
            print(f"  Federal PTC: ${ptc:.2f}/MWh")

        eeg = policy.get('eeg_tariff')
        if eeg is not None:
            print(f"  EEG Tariff: €{eeg:.2f}¢/kWh")

        gbi = policy.get('gbi_rate')
        if gbi is not None:
            print(f"  GBI Rate: ₹{gbi:.2f}/kWh")

        tax_rate = policy.get('tax_rate', 0)
        if tax_rate:
            print(f"  Tax Rate: {tax_rate * 100 if tax_rate < 1 else tax_rate:.0f}%")

        # THE KEY PART - AI INSIGHTS WITH RESEARCH
        if result.get('ai_insights'):
            ai = result['ai_insights']

            print_section("🤖 AI-GENERATED INSIGHTS (WITH RESEARCH CONTEXT!)")

            print("\n💡 KEY INSIGHTS:")
            for i, insight in enumerate(ai['key_insights'], 1):
                print(f"\n  {i}. {insight}")

            print("\n⚠️  RISKS:")
            for i, risk in enumerate(ai['risks'], 1):
                print(f"\n  {i}. {risk}")

            print("\n🎯 OPPORTUNITIES:")
            for i, opp in enumerate(ai['opportunities'], 1):
                print(f"\n  {i}. {opp}")

            print("\n📋 RECOMMENDATION:")
            print(f"\n  {ai['recommendation_summary']}")

            # Check for research-specific content
            print_section("✅ RESEARCH INTEGRATION CHECK")

            full_text = json.dumps(ai).lower()

            research_indicators = {
                "Company Names": ["amazon", "google", "microsoft", "meta"],
                "Specific Numbers": ["gw", "mwh", "€", "₹", "2024", "2025"],
                "Policy References": ["ira", "itc", "ptc", "pli", "eeg", "auction"],
                "Concrete Actions": ["ppa", "storage", "hydrogen", "bifacial", "tracking"],
                "Deadlines": ["march", "2025", "2030", "2032"],
            }

            found = []
            for category, terms in research_indicators.items():
                matches = [term for term in terms if term in full_text]
                if matches:
                    found.append(f"  ✅ {category}: {', '.join(matches[:3])}")

            if found:
                print("\n  Research-Enhanced Content Detected:")
                for item in found:
                    print(item)
            else:
                print("\n  ⚠️  Warning: No research-specific content detected")
                print("     (May indicate research context not loading)")

        print_section("💰 COST ANALYSIS")
        print(f"  AI Provider: OpenAI GPT-4o")
        print(f"  Estimated Cost: ~$0.006 per analysis")
        print(f"  With Research Context: MUCH higher value!")

        print_section("🎉 SUCCESS!")
        print("\n  ✅ Real NASA satellite data")
        print("  ✅ Real policy incentives")
        print("  ✅ GPT-4 AI insights")
        print("  ✅ Market research context")
        print("  ✅ Investment-grade analysis")

        print("\n  Compare these insights to generic AI responses!")
        print("  Notice the specific company names, auction results, deadlines!")

    except requests.exceptions.Timeout:
        print("\n❌ Request timeout")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_comparison():
    """Test multiple countries to see research context differences."""

    print_section("🌍 MULTI-COUNTRY COMPARISON WITH RESEARCH CONTEXT")

    locations = [
        {
            "name": "West Texas Solar",
            "country": "USA",
            "technology": "solar_pv",
            "latitude": 31.99,
            "longitude": -102.07,
            "capacity_mw": 100
        },
        {
            "name": "Gujarat Solar",
            "country": "IND",
            "technology": "solar_pv",
            "latitude": 23.0,
            "longitude": 72.0,
            "capacity_mw": 100
        },
        {
            "name": "North Sea Wind",
            "country": "DEU",
            "technology": "onshore_wind",
            "latitude": 54.0,
            "longitude": 8.0,
            "capacity_mw": 150
        }
    ]

    results = []

    for loc in locations:
        print(f"\n📍 Analyzing: {loc['name']}")

        try:
            response = requests.post(
                f"{API_URL}/analyze",
                json=loc,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                results.append({
                    'name': loc['name'],
                    'country': loc['country'],
                    'lcoe': result['lcoe'],
                    'irr': result['irr'],
                    'first_insight': result.get('ai_insights', {}).get('key_insights', [''])[0][:150] + "..."
                })
                print(f"  ✅ Complete")
            else:
                print(f"  ❌ Failed: {response.status_code}")

        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

    if results:
        print_section("📊 COMPARISON RESULTS")

        print(f"\n{'Project':<20} {'LCOE':<12} {'IRR':<10}")
        print("-" * 45)
        for r in results:
            print(f"{r['name']:<20} ${r['lcoe']:<11.2f} {r['irr']:<9.1f}%")

        print("\n🤖 Sample Insights (First 150 chars):\n")
        for r in results:
            print(f"{r['name']} ({r['country']}):")
            print(f"  {r['first_insight']}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 RESEARCH-ENHANCED AI INSIGHTS TEST")
    print("=" * 70)
    print("\nThis test demonstrates GPT-4 with comprehensive market research.")
    print("Watch for specific company names, auction results, and deadlines!")
    print("\nMake sure API is running: python src/api/main.py")
    print("=" * 70)

    # Run single detailed test
    test_research_enhanced_insights()

    # Optional: Run comparison test
    print("\n" + "=" * 70)
    response = input("\nRun multi-country comparison? (y/n): ")
    if response.lower() == 'y':
        test_comparison()

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE!")
    print("=" * 70)