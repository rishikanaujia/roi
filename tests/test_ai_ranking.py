"""
Test AI-powered country ranking with iterative verification.
Saves complete iteration history to JSON for inspection.
"""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration.country_comparison_orchestrator import CountryComparisonOrchestrator
from src.llm.factory import LLMProviderFactory


async def test_country_comparison():
    """Test complete country comparison with iterative ranking."""
    
    print("="*70)
    print("🌍 COUNTRY COMPARISON TEST")
    print("="*70)
    print()
    
    # Create LLM provider
    llm_provider = LLMProviderFactory.create('openai', model='gpt-4o')
    
    # Create orchestrator
    orchestrator = CountryComparisonOrchestrator(llm_provider=llm_provider)
    
    # Countries to compare
    countries = ["USA", "DEU", "IND"]
    
    print(f"Comparing countries: {', '.join(countries)}")
    print()
    
    # Run comparison
    result = await orchestrator.compare_countries(countries)
    
    # Save complete result to JSON
    output_file = Path(__file__).parent / "country_comparison_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Complete result saved to: {output_file}")
    
    # Display summary
    print("\n" + "="*70)
    print("🏆 AI-POWERED RANKING")
    print("="*70)
    print()
    
    ranking = result['ranking']
    for country in ranking['ranked_countries']:
        print(f"{country['rank']}. {country['country_name']} (Score: {country['overall_score']})")
        print(f"   {country['justification']}")
        print()
    
    # Display verification
    print("="*70)
    print("🔍 VERIFICATION RESULTS")
    print("="*70)
    print()
    
    verification = result['verification']
    status_icon = "✅" if verification.get('verified', False) else "❌"
    print(f"Status: {status_icon} {'PASSED' if verification.get('verified') else 'FAILED'}")
    print(f"Summary: {verification.get('summary', 'N/A')}")
    print()
    
    # Display checks
    if 'checks_performed' in verification:
        print("Checks Performed:")
        for check in verification['checks_performed']:
            status_icon = "✓" if check['status'] == 'passed' else "✗"
            print(f"  {status_icon} {check['check_type']}: {check['finding']}")
    
    # Display issues
    if verification.get('issues_found'):
        print(f"\n⚠️  Issues Found ({len(verification['issues_found'])}):")
        for issue in verification['issues_found']:
            severity_icon = "🔴" if issue['severity'] == 'critical' else "🟡"
            print(f"  {severity_icon} [{issue['severity'].upper()}] {issue['issue']}")
            print(f"    → Recommendation: {issue['recommendation']}")
    
    # Display strengths
    if verification.get('strengths'):
        print(f"\n💪 Strengths:")
        for strength in verification['strengths']:
            print(f"  • {strength}")
    
    # Display overall assessment
    if verification.get('overall_assessment'):
        print(f"\n📋 Overall Assessment:")
        print(f"   {verification['overall_assessment']}")
    
    # Display iteration statistics
    print("\n" + "="*70)
    print("📊 ITERATION STATISTICS")
    print("="*70)
    print()
    
    stats = result.get('ranking_statistics', {})
    print(f"Total Iterations: {stats.get('total_iterations', 0)}")
    print(f"Final Verified: {'✓ Yes' if stats.get('final_verified') else '✗ No'}")
    print(f"Total Time: {stats.get('total_time_seconds', 0):.2f}s")
    
    if stats.get('iterations_until_success'):
        print(f"Success on Iteration: {stats['iterations_until_success']}")
    
    # Display improvement summary
    if 'improvement_summary' in result:
        summary = result['improvement_summary']
        print(f"\nConclusion: {summary.get('conclusion', 'N/A')}")
    
    print("\n" + "="*70)
    print(f"📁 Full details saved to: {output_file}")
    print("="*70)
    
    return result


if __name__ == "__main__":
    asyncio.run(test_country_comparison())
