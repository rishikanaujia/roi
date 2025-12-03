"""
View iteration history from saved JSON file.
Shows how ranking improved across iterations.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def load_result(filepath: str) -> Dict[str, Any]:
    """Load result from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def display_iteration_details(iterations: List[Dict[str, Any]]) -> None:
    """Display detailed iteration history."""
    
    print("="*70)
    print("🔄 ITERATION-BY-ITERATION ANALYSIS")
    print("="*70)
    
    for i, iteration in enumerate(iterations, 1):
        print(f"\n{'='*70}")
        print(f"ITERATION {i}")
        print(f"{'='*70}")
        
        # Status
        status = iteration.get('status', 'unknown')
        status_icon = "✅" if status == 'passed' else "❌"
        print(f"\nStatus: {status_icon} {status.upper()}")
        
        # Timing
        timing = iteration.get('timing', {})
        print(f"Ranking Time: {timing.get('ranking_seconds', 0):.2f}s")
        print(f"Verification Time: {timing.get('verification_seconds', 0):.2f}s")
        print(f"Total Time: {timing.get('total_seconds', 0):.2f}s")
        
        # Ranking
        ranking = iteration.get('ranking', {})
        ranked_countries = ranking.get('ranked_countries', [])
        
        print(f"\n📊 RANKING:")
        for country in ranked_countries:
            print(f"  {country['rank']}. {country['country_name']} "
                  f"(Score: {country['overall_score']})")
            
            # Component scores
            if 'component_scores' in country:
                scores = country['component_scores']
                print(f"     Financial: {scores.get('financial_performance', 0)}, "
                      f"Resource: {scores.get('resource_quality', 0)}, "
                      f"Policy: {scores.get('policy_stability', 0)}, "
                      f"Market: {scores.get('market_maturity', 0)}")
            
            # Key differentiators
            if 'key_differentiators' in country:
                print(f"     Key: {', '.join(country['key_differentiators'][:2])}")
        
        # Verification Issues
        verification = iteration.get('verification', {})
        issues = verification.get('issues_found', [])
        
        if issues:
            print(f"\n⚠️  ISSUES FOUND ({len(issues)}):")
            for issue in issues:
                severity_icon = "🔴" if issue['severity'] == 'critical' else "🟡"
                print(f"  {severity_icon} [{issue['severity'].upper()}] {issue['issue']}")
        
        # Feedback addressed (if iteration > 1)
        if i > 1 and 'feedback_addressed' in ranked_countries[0]:
            print(f"\n✏️  FEEDBACK ADDRESSED:")
            for country in ranked_countries:
                if country.get('feedback_addressed'):
                    print(f"  • {country['country_name']}: {country['feedback_addressed']}")


def display_ranking_evolution(iterations: List[Dict[str, Any]]) -> None:
    """Show how country rankings changed across iterations."""
    
    print("\n" + "="*70)
    print("📈 RANKING EVOLUTION")
    print("="*70)
    
    # Extract country rankings per iteration
    country_ranks = {}
    
    for i, iteration in enumerate(iterations, 1):
        ranking = iteration.get('ranking', {})
        for country in ranking.get('ranked_countries', []):
            country_name = country['country_name']
            if country_name not in country_ranks:
                country_ranks[country_name] = []
            country_ranks[country_name].append({
                'iteration': i,
                'rank': country['rank'],
                'score': country['overall_score']
            })
    
    # Display evolution for each country
    for country_name, ranks in country_ranks.items():
        print(f"\n{country_name}:")
        rank_str = " → ".join([f"#{r['rank']} ({r['score']})" for r in ranks])
        print(f"  {rank_str}")
        
        # Check if rank changed
        ranks_only = [r['rank'] for r in ranks]
        if len(set(ranks_only)) > 1:
            print(f"  ⚠️  Rank changed across iterations!")


def display_verification_trends(iterations: List[Dict[str, Any]]) -> None:
    """Show verification trends across iterations."""
    
    print("\n" + "="*70)
    print("🔍 VERIFICATION TRENDS")
    print("="*70)
    
    print(f"\n{'Iteration':<12} {'Status':<12} {'Critical':<12} {'Moderate':<12}")
    print("-" * 50)
    
    for i, iteration in enumerate(iterations, 1):
        verification = iteration.get('verification', {})
        status = "PASSED" if verification.get('verified', False) else "FAILED"
        
        issues = verification.get('issues_found', [])
        critical = len([iss for iss in issues if iss['severity'] == 'critical'])
        moderate = len([iss for iss in issues if iss['severity'] == 'moderate'])
        
        status_icon = "✅" if status == "PASSED" else "❌"
        print(f"{i:<12} {status_icon} {status:<10} {critical:<12} {moderate:<12}")


def display_improvement_summary(result: Dict[str, Any]) -> None:
    """Display improvement summary."""
    
    summary = result.get('improvement_summary', {})
    
    print("\n" + "="*70)
    print("💡 IMPROVEMENT SUMMARY")
    print("="*70)
    
    print(f"\nTotal Attempts: {summary.get('total_attempts', 0)}")
    print(f"Successful: {'✓ Yes' if summary.get('successful') else '✗ No'}")
    print(f"\nConclusion: {summary.get('conclusion', 'N/A')}")
    
    # Details per iteration
    if 'iterations_detail' in summary:
        print("\n" + "-"*70)
        for detail in summary['iterations_detail']:
            print(f"\nIteration {detail['iteration']}: {detail['status'].upper()}")
            print(f"  Issues: {detail['issues_found']}")
            print(f"  Time: {detail['timing']:.2f}s")
            
            if 'changes_from_previous' in detail:
                print(f"  Changes: {detail['changes_from_previous']}")


def main():
    """Main function."""
    
    # Find result file
    result_file = Path(__file__).parent / "country_comparison_result.json"
    
    if not result_file.exists():
        print(f"❌ Result file not found: {result_file}")
        print("Run 'python tests/test_ai_ranking.py' first!")
        sys.exit(1)
    
    print("="*70)
    print("📂 LOADING ITERATION HISTORY")
    print("="*70)
    print(f"\nFile: {result_file}")
    
    # Load result
    result = load_result(result_file)
    
    # Display analysis
    iterations = result.get('ranking_iterations', [])
    
    if not iterations:
        print("\n❌ No iterations found in result!")
        sys.exit(1)
    
    print(f"Total Iterations: {len(iterations)}")
    
    # Display details
    display_iteration_details(iterations)
    display_ranking_evolution(iterations)
    display_verification_trends(iterations)
    display_improvement_summary(result)
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
