"""
Test Enhanced LLM Strategy with Week 1-6 ML Data
Phase 1 Implementation Test
"""
import asyncio
import json
import os
from application.services.ai_promotion_service import AIPromotionService

async def test_enhanced_strategy():
    """Test enhanced strategy generation"""
    print("="*70)
    print("🧪 TESTING PHASE 1: ENHANCED LLM STRATEGY")
    print("="*70)
    
    try:
        # Get Gemini API key
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            print("\n⚠️ GEMINI_API_KEY not found in environment")
            print("   Attempting to load from .env file...")
            
            # Try to load from .env
            try:
                from dotenv import load_dotenv
                load_dotenv()
                gemini_api_key = os.getenv('GEMINI_API_KEY')
                
                if gemini_api_key:
                    print("✅ Loaded GEMINI_API_KEY from .env")
                else:
                    print("❌ GEMINI_API_KEY not found in .env")
                    print("\n💡 Please set GEMINI_API_KEY in .env file or environment")
                    return None
            except ImportError:
                print("❌ python-dotenv not installed")
                print("\n💡 Run: pip install python-dotenv")
                print("   Or set GEMINI_API_KEY environment variable")
                return None
        
        # Initialize service
        print("\n1️⃣ Initializing AI Promotion Service...")
        service = AIPromotionService(gemini_api_key=gemini_api_key)
        print("✅ Service initialized")
        
        # Generate traditional recommendations first
        print("\n2️⃣ Generating traditional ML results...")
        ml_results = service.generate_recommendations()
        print(f"✅ ML Results generated:")
        print(f"   - Business Health: {list(ml_results.get('business_health', {}).keys())}")
        print(f"   - Product Combos: {len(ml_results.get('product_combos', {}).get('rules', []))} rules")
        print(f"   - Top Products: {len(ml_results.get('recommendations', {}).get('top_products', []))} products")
        
        # Generate enhanced insights
        print("\n3️⃣ Generating enhanced insights with Week 1-6 data...")
        print("   Fetching:")
        print("   - Week 1: Price Elasticity")
        print("   - Week 2: Customer Segmentation")
        print("   - Week 3-4: Personalized Pricing")
        print("   - Week 5: Simulation Results")
        print("   - Week 6: Active Promotions")
        
        enhanced_insights = await service.generate_enhanced_llm_insights(ml_results)
        
        print("\n✅ Enhanced insights generated!")
        
        # Display results
        print("\n" + "="*70)
        print("📊 ENHANCED STRATEGY RESULTS")
        print("="*70)
        
        if "error" in enhanced_insights:
            print(f"❌ Error: {enhanced_insights['error']}")
            print(f"   Fallback: {enhanced_insights.get('fallback', 'N/A')}")
        else:
            # Check data sources
            data_sources = enhanced_insights.get("data_sources", {})
            if data_sources:
                print("\n✅ Data Sources Included:")
                for source, status in data_sources.items():
                    icon = "✅" if status == "included" else "❌"
                    print(f"   {icon} {source}: {status}")
            
            # Display key sections
            print("\n📋 Strategy Components:")
            
            if "executive_summary" in enhanced_insights:
                summary = enhanced_insights["executive_summary"]
                print(f"\n🎯 Executive Summary:")
                print(f"   Overview: {summary.get('overview', 'N/A')}")
                print(f"   Health Score: {summary.get('overall_health_score', 'N/A')}/100")
                print(f"   Key Findings:")
                for finding in summary.get("key_findings", [])[:3]:
                    print(f"      - {finding}")
            
            if "pricing_strategy_analysis" in enhanced_insights:
                pricing = enhanced_insights["pricing_strategy_analysis"]
                print(f"\n💰 Pricing Strategy:")
                print(f"   Products to increase: {len(pricing.get('products_to_increase_price', []))}")
                print(f"   Products to decrease: {len(pricing.get('products_to_decrease_price', []))}")
                print(f"   Products to maintain: {len(pricing.get('products_to_maintain', []))}")
                
                # Show first recommendation
                if pricing.get('products_to_increase_price'):
                    first = pricing['products_to_increase_price'][0]
                    print(f"\n   Example (Increase):")
                    print(f"      Product: {first.get('product_name', 'N/A')}")
                    print(f"      Current: {first.get('current_price', 0):,.0f} VND")
                    print(f"      Recommended: {first.get('recommended_price', 0):,.0f} VND")
                    print(f"      Elasticity: {first.get('elasticity', 'N/A')}")
                    print(f"      Reasoning: {first.get('reasoning', 'N/A')[:80]}...")
                    print(f"      Expected Revenue Increase: +{first.get('expected_revenue_increase_pct', 0)}%")
            
            if "segment_strategy_recommendations" in enhanced_insights:
                segments = enhanced_insights["segment_strategy_recommendations"]
                print(f"\n👥 Customer Segment Strategies:")
                for segment_name, strategy in list(segments.items())[:3]:
                    print(f"\n   {segment_name}:")
                    print(f"      Count: {strategy.get('count', 0)} customers")
                    print(f"      Strategy: {strategy.get('strategy', 'N/A')}")
                    print(f"      Action: {strategy.get('action', 'N/A')}")
                    print(f"      Expected Impact: {strategy.get('expected_impact', 'N/A')}")
            
            if "promotion_recommendations" in enhanced_insights:
                promotions = enhanced_insights["promotion_recommendations"]
                print(f"\n🎁 Promotion Recommendations:")
                for i, promo in enumerate(promotions[:3], 1):
                    print(f"\n   Priority {promo.get('priority', i)}:")
                    print(f"      Type: {promo.get('type', 'N/A')}")
                    print(f"      Action: {promo.get('action', 'N/A')}")
                    print(f"      ML Backing: {promo.get('ml_backing', 'N/A')}")
                    print(f"      Timeline: {promo.get('timeline', 'N/A')}")
                    print(f"      Expected Outcome: {promo.get('expected_outcome', 'N/A')}")
                    print(f"      Risk Level: {promo.get('risk_level', 'N/A')}")
            
            if "action_plan" in enhanced_insights:
                action_plan = enhanced_insights["action_plan"]
                print(f"\n📅 Action Plan:")
                
                if action_plan.get('immediate_actions'):
                    print(f"   Immediate:")
                    for action in action_plan['immediate_actions'][:3]:
                        print(f"      • {action}")
                
                if action_plan.get('this_week'):
                    print(f"   This Week:")
                    for action in action_plan['this_week'][:3]:
                        print(f"      • {action}")
            
            if "kpis_to_track" in enhanced_insights:
                kpis = enhanced_insights["kpis_to_track"]
                print(f"\n📈 KPIs to Track:")
                for kpi in kpis[:3]:
                    print(f"\n   {kpi.get('metric', 'N/A')}:")
                    print(f"      Baseline: {kpi.get('baseline', 'N/A')}")
                    print(f"      Target: {kpi.get('target', 'N/A')}")
                    print(f"      Frequency: {kpi.get('tracking_frequency', 'N/A')}")
            
            # If raw response
            if "raw_response" in enhanced_insights:
                print(f"\n📝 Raw LLM Response (first 500 chars):")
                print(f"{enhanced_insights['raw_response'][:500]}...")
        
        # Save full results
        print("\n" + "="*70)
        print("💾 Saving full results to file...")
        with open("enhanced_strategy_results.json", "w", encoding="utf-8") as f:
            json.dump(enhanced_insights, f, ensure_ascii=False, indent=2)
        print("✅ Saved to: enhanced_strategy_results.json")
        
        print("\n" + "="*70)
        print("🎉 TEST COMPLETED SUCCESSFULLY")
        print("="*70)
        
        return enhanced_insights
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    print("\n🚀 Starting Phase 1 Enhanced Strategy Test...\n")
    result = asyncio.run(test_enhanced_strategy())
    
    if result:
        print("\n✅ Test passed - Enhanced strategy generated successfully!")
        print("📄 Check enhanced_strategy_results.json for full details")
    else:
        print("\n❌ Test failed - Please check errors above")
