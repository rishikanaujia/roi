import asyncio
from src.llm.factory import LLMProviderFactory


async def test_ai_ranking():
    # Create OpenAI provider
    llm_provider = LLMProviderFactory.create('openai', model='gpt-4o')

    # Create orchestrator with LLM
    from src.orchestration.country_comparison_orchestrator import CountryComparisonOrchestrator
    orchestrator = CountryComparisonOrchestrator(llm_provider=llm_provider)

    # Run comparison
    result = await orchestrator.compare_countries(['USA', 'DEU', 'IND'])

    # Print ranking
    print("\n" + "=" * 70)
    print("🏆 AI-POWERED RANKING")
    print("=" * 70)
    for c in result['ranking']['ranked_countries']:
        print(f"\n{c['rank']}. {c['country_name']} (Score: {c['overall_score']})")
        print(f"   {c['justification']}\n")

    # Print verification results
    print("\n" + "=" * 70)
    print("🔍 VERIFICATION RESULTS")
    print("=" * 70)

    verification = result['verification']
    status = "✅ PASSED" if verification['verified'] else "❌ FAILED"
    print(f"\nStatus: {status}")
    print(f"Summary: {verification['summary']}\n")

    if 'checks_performed' in verification:
        print("Checks Performed:")
        for check in verification['checks_performed']:
            icon = "✓" if check['status'] == 'passed' else "⚠" if check['status'] == 'warning' else "✗"
            print(f"  {icon} {check['check_type'].upper()}: {check['finding']}")

    if verification.get('issues_found'):
        print(f"\n⚠️  Issues Found ({len(verification['issues_found'])}):")
        for issue in verification['issues_found']:
            print(f"  • [{issue['severity'].upper()}] {issue['issue']}")
            print(f"    → Recommendation: {issue['recommendation']}")

    if verification.get('strengths'):
        print(f"\n💪 Strengths:")
        for strength in verification['strengths']:
            print(f"  • {strength}")

    print(f"\n📋 Overall Assessment:")
    print(f"   {verification['overall_assessment']}")

    print("\n" + "=" * 70)


asyncio.run(test_ai_ranking())