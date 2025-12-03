"""
Test Parallel Analysis - Compare Multiple Countries

This demonstrates the batch analysis endpoint that runs
multiple analyses in parallel.

Example: Compare USA vs India vs Germany renewable opportunities
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/v1"


def test_parallel_comparison():
    """Test comparing multiple countries/technologies in parallel."""

    print("=" * 70)
    print("🌍 PARALLEL ANALYSIS TEST - Compare Multiple Opportunities")
    print("=" * 70)
    print("\nComparing renewable energy opportunities across:")
    print("  • USA (Solar + Wind)")
    print("  • India (Solar)")
    print("  • Germany (Wind)")
    print("\nRunning analyses IN PARALLEL with real NASA data + GPT-4 insights...")

    # Define analyses to compare
    batch_request = {
        "analyses": [
            {
                "name": "West Texas Solar",
                "country": "USA",
                "technology": "solar_pv",
                "latitude": 31.99,
                "longitude": -102.07,
                "capacity_mw": 100
            },
            {
                "name": "Iowa Wind Farm",
                "country": "USA",
                "technology": "onshore_wind",
                "latitude": 42.0,
                "longitude": -93.0,
                "capacity_mw": 150
            },
            {
                "name": "Gujarat Solar Park",
                "country": "IND",
                "technology": "solar_pv",
                "latitude": 23.0,
                "longitude": 72.0,
                "capacity_mw": 100
            },
            {
                "name": "North Sea Wind Farm",
                "country": "DEU",
                "technology": "onshore_wind",
                "latitude": 54.0,
                "longitude": 8.0,
                "capacity_mw": 150
            }
        ]
    }

    # Track timing
    start = datetime.now()

    # Call batch analysis endpoint
    try:
        response = requests.post(
            f"{API_URL}/analyze/batch",
            json=batch_request,
            timeout=120
        )

        if response.status_code != 200:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            return

        result = response.json()
        elapsed = (datetime.now() - start).total_seconds()

        # Display summary
        print(f"\n✅ Analysis Complete!")
        print(f"\n⏱️  Performance:")
        print(f"  Total Time: {result['total_time_seconds']:.2f}s")
        print(f"  Analyses Run: {result['total_analyses']}")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Avg Time per Analysis: {result['avg_time_per_analysis']:.2f}s")

        if elapsed < 40:
            print(f"\n🚀 Parallel Speedup Achieved!")
            print(f"  Sequential would take: ~{result['total_analyses'] * 13:.0f}s")
            print(f"  Parallel took: {elapsed:.0f}s")
            print(f"  Speedup: {(result['total_analyses'] * 13 / elapsed):.1f}x faster!")

        # Display comparison summary
        comparison = result['comparison_summary']

        print(f"\n{'=' * 70}")
        print("🏆 COMPARISON SUMMARY")
        print(f"{'=' * 70}")

        print(f"\n📊 Key Findings:")
        print(f"  Total Projects Analyzed: {comparison['total_projects']}")
        print(f"  Viable Projects: {comparison['viable_projects']}")

        if comparison.get('best_irr'):
            print(f"\n  🥇 Best IRR: {comparison['best_irr']['project']}")
            print(f"     IRR: {comparison['best_irr']['value']:.1f}%")

        if comparison.get('lowest_lcoe'):
            print(f"\n  💰 Lowest LCOE: {comparison['lowest_lcoe']['project']}")
            print(f"     LCOE: ${comparison['lowest_lcoe']['value']:.2f}/MWh")

        if comparison.get('highest_capacity_factor'):
            print(f"\n  ⚡ Highest Capacity Factor: {comparison['highest_capacity_factor']['project']}")
            print(f"     CF: {comparison['highest_capacity_factor']['value']:.1f}%")

        # Display comparison table
        print(f"\n{'=' * 70}")
        print("📊 DETAILED COMPARISON")
        print(f"{'=' * 70}")

        table = comparison['comparison_table']

        # Header
        print(f"\n{'Project':<25} {'Country':<8} {'Tech':<12} {'LCOE':<10} {'IRR':<8} {'CF':<8} {'Status':<15}")
        print("-" * 95)

        # Rows
        for project in table:
            name = project['name'][:24]
            country = project['country']
            tech = project['technology'][:11]
            lcoe = f"${project['lcoe']:.2f}"
            irr = f"{project['irr']:.1f}%"
            cf = f"{project['capacity_factor']:.1f}%"
            status = project['recommendation']

            print(f"{name:<25} {country:<8} {tech:<12} {lcoe:<10} {irr:<8} {cf:<8} {status:<15}")

        # Display rankings
        print(f"\n{'=' * 70}")
        print("🏅 RANKINGS")
        print(f"{'=' * 70}")

        rankings = comparison['rankings']

        print("\n📈 By IRR (Best Returns):")
        for item in rankings['by_irr']:
            print(f"  {item['rank']}. {item['name']}: {item['irr']:.1f}%")

        print("\n💵 By LCOE (Lowest Cost):")
        for item in rankings['by_lcoe']:
            print(f"  {item['rank']}. {item['name']}: ${item['lcoe']:.2f}/MWh")

        print("\n⚡ By Capacity Factor (Best Resource):")
        for item in rankings['by_capacity_factor']:
            print(f"  {item['rank']}. {item['name']}: {item['cf']:.1f}%")

        # Display AI insights for best project
        print(f"\n{'=' * 70}")
        print("🤖 AI INSIGHTS - Best Project")
        print(f"{'=' * 70}")

        if result['detailed_results']:
            best = result['detailed_results'][0]  # First result (can sort by IRR)

            print(f"\nProject: {best['name']}")

            if best.get('ai_insights'):
                ai = best['ai_insights']

                print(f"\n💡 Key Insight:")
                print(f"  {ai['key_insights'][0]}")

                print(f"\n⚠️  Top Risk:")
                print(f"  {ai['risks'][0]}")

                if ai['opportunities']:
                    print(f"\n🎯 Top Opportunity:")
                    print(f"  {ai['opportunities'][0]}")

        print(f"\n{'=' * 70}")
        print("✅ PARALLEL ANALYSIS TEST COMPLETE!")
        print(f"{'=' * 70}")

        # Show cost
        if result['successful'] > 0:
            cost = result['successful'] * 0.006  # $0.006 per analysis with GPT-4
            print(f"\n💰 Total AI Cost: ${cost:.4f}")
            print(f"   (${0.006:.4f} × {result['successful']} analyses)")

    except requests.exceptions.Timeout:
        print("\n❌ Request timeout - analyses taking too long")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    test_parallel_comparison()