"""
TAIFA-FIALA Data Collection Pipeline Runner
==========================================

Quick test runner for the enhanced data collection pipeline.
"""

import asyncio
import os
import json
from datetime import datetime
from backend.etl.intelligence import DataCollectionOrchestrator


async def run_test_collection():
    """Run a test collection cycle"""
    
    # Get API keys from environment variables
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not perplexity_key or not openai_key:
        print("❌ Missing API keys. Please set PERPLEXITY_API_KEY and OPENAI_API_KEY environment variables.")
        return
    
    print("🚀 Starting TAIFA-FIALA Data Collection Pipeline Test")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        async with DataCollectionOrchestrator(perplexity_key, openai_key) as orchestrator:
            
            print("\n📊 Running intelligence-driven collection cycle...")
            
            # Run collection cycle
            result = await orchestrator.run_collection_cycle()
            
            print(f"\n✅ Collection cycle completed: {result.cycle_id}")
            print(f"🎯 Targets discovered: {result.targets_discovered}")
            print(f"⚡ Targets processed: {result.targets_processed}")
            print(f"🏆 Innovations extracted: {result.innovations_extracted}")
            print(f"💾 Database records created: {result.database_records_created}")
            
            if result.errors_encountered:
                print(f"⚠️  Errors encountered: {len(result.errors_encountered)}")
                for error in result.errors_encountered:
                    print(f"   - {error}")
            
            if result.recommendations:
                print(f"\n💡 Recommendations for next cycle:")
                for rec in result.recommendations:
                    print(f"   - {rec}")
            
            # Get overall stats
            stats = orchestrator.get_stats()
            print(f"\n📈 Collection Statistics:")
            print(json.dumps(stats, indent=2, default=str))
            
            # Save results
            results_file = f"collection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump({
                    'cycle_result': result.__dict__,
                    'stats': stats
                }, f, indent=2, default=str)
            
            print(f"\n💾 Results saved to: {results_file}")
            
    except Exception as e:
        print(f"❌ Collection pipeline failed: {e}")
        import traceback
        traceback.print_exc()


async def test_individual_modules():
    """Test individual modules separately"""
    
    from backend.etl.intelligence import PerplexityAfricanAIModule, IntelligenceType
    
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    if not perplexity_key:
        print("❌ Missing PERPLEXITY_API_KEY for module testing")
        return
    
    print("\n🧪 Testing Perplexity Intelligence Module...")
    
    try:
        async with PerplexityAfricanAIModule(perplexity_key) as intel_module:
            
            # Test intelligence synthesis
            reports = await intel_module.synthesize_intelligence(
                intelligence_types=[IntelligenceType.INNOVATION_DISCOVERY],
                time_period='last_7_days'
            )
            
            print(f"✅ Generated {len(reports)} intelligence reports")
            
            for report in reports:
                print(f"📋 Report: {report.report_type.value}")
                print(f"   Summary: {report.summary[:100]}...")
                print(f"   Innovations mentioned: {len(report.innovations_mentioned)}")
                print(f"   Confidence: {report.confidence_score:.2f}")
    
    except Exception as e:
        print(f"❌ Module testing failed: {e}")


def main():
    """Main entry point"""
    
    print("🌍 TAIFA-FIALA Enhanced Data Collection Pipeline")
    print("=" * 50)
    
    # Check for required dependencies
    try:
        import crawl4ai
        import aiohttp
        print("✅ Dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install crawl4ai aiohttp")
        return
    
    # Run tests
    asyncio.run(run_test_collection())
    
    # Test individual modules
    print("\n" + "=" * 50)
    asyncio.run(test_individual_modules())
    
    print("\n🎉 Testing completed!")


if __name__ == "__main__":
    main()
