"""
Test Event-Driven Promotion System
Test toàn bộ flow từ phân tích đến tạo khuyến mãi
"""

import asyncio
import json
from datetime import datetime
import logging

from application.services.event_promotion_service import get_event_promotion_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_sales_performance_analysis():
    """Test 1: Phân tích hiệu suất bán hàng"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Sales Performance Analysis")
    logger.info("="*80)
    
    service = get_event_promotion_service()
    analyses = await service.analyze_product_performance(analysis_period_days=30)
    
    logger.info(f"\n📊 Tổng số sản phẩm phân tích: {len(analyses)}")
    
    # Phân loại
    slow_movers = [a for a in analyses if a.status.value == "SLOW_MOVING"]
    best_sellers = [a for a in analyses if a.status.value == "BEST_SELLER"]
    combo_potential = [a for a in analyses if a.status.value == "COMBO_POTENTIAL"]
    
    logger.info(f"\n🐌 Slow Movers: {len(slow_movers)}")
    for prod in slow_movers[:3]:
        logger.info(f"  - {prod.product_name}: {prod.total_sold} sold, {prod.recommended_discount}% discount")
        logger.info(f"    Lý do: {prod.reason}")
    
    logger.info(f"\n🔥 Best Sellers: {len(best_sellers)}")
    for prod in best_sellers[:3]:
        logger.info(f"  - {prod.product_name}: {prod.total_sold} sold, contribution {prod.revenue_contribution:.1f}%")
    
    logger.info(f"\n🎁 Combo Potential: {len(combo_potential)}")
    for prod in combo_potential[:3]:
        logger.info(f"  - {prod.product_name}: Rating {prod.avg_rating}, {prod.total_sold} sold")
    
    return analyses


async def test_combo_discovery():
    """Test 2: Phát hiện combo sản phẩm"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Product Combo Discovery")
    logger.info("="*80)
    
    service = get_event_promotion_service()
    combos = await service.discover_product_combos(
        min_support=0.05,
        min_confidence=0.3
    )
    
    logger.info(f"\n🎁 Tìm thấy {len(combos)} combo suggestions")
    
    for i, combo in enumerate(combos[:5], 1):
        logger.info(f"\nCombo #{i}:")
        logger.info(f"  Product 1: {combo.product_1_name} - {combo.product_1_price:,.0f} VND")
        logger.info(f"  Product 2: {combo.product_2_name} - {combo.product_2_price:,.0f} VND")
        logger.info(f"  Frequency: {combo.frequency_together} times bought together")
        logger.info(f"  Confidence: {combo.confidence*100:.1f}%")
        logger.info(f"  Recommended bundle discount: {combo.recommended_bundle_discount:.1f}%")
        
        total_price = combo.product_1_price + combo.product_2_price
        discount_amount = total_price * combo.recommended_bundle_discount / 100
        final_price = total_price - discount_amount
        logger.info(f"  Total: {total_price:,.0f} VND → {final_price:,.0f} VND (save {discount_amount:,.0f})")
    
    return combos


def test_event_detection():
    """Test 3: Phát hiện sự kiện sắp tới"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Upcoming Events Detection")
    logger.info("="*80)
    
    service = get_event_promotion_service()
    upcoming_events = service.event_detector.get_upcoming_events(
        reference_date=datetime.now(),
        days_ahead=60
    )
    
    logger.info(f"\n🎪 Tìm thấy {len(upcoming_events)} sự kiện sắp tới")
    
    for event in upcoming_events[:5]:
        logger.info(f"\nEvent: {event.event_type.value}")
        logger.info(f"  Date: {event.event_date.strftime('%Y-%m-%d')}")
        logger.info(f"  Days until: {event.days_until_event} days")
        logger.info(f"  Duration: {event.duration_days} days")
        logger.info(f"  Recommended discount: {event.recommended_discount_range}%")
        logger.info(f"  Target categories: {', '.join(event.target_categories)}")
    
    return upcoming_events


async def test_event_based_promotion():
    """Test 4: Tạo khuyến mãi dựa trên sự kiện"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Event-Based Promotion Generation")
    logger.info("="*80)
    
    service = get_event_promotion_service()
    promotions = await service.generate_event_promotion(
        event_type=None,  # All events
        days_ahead=60
    )
    
    logger.info(f"\n🎯 Tạo được {len(promotions)} promotion recommendations")
    
    for i, promo in enumerate(promotions[:3], 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"PROMOTION #{i}: {promo.promotion_name}")
        logger.info(f"{'='*60}")
        logger.info(f"\nStrategy: {promo.strategy.value}")
        logger.info(f"Primary Goal: {promo.primary_goal}")
        
        if promo.event_info:
            logger.info(f"\nEvent: {promo.event_info.event_type.value}")
            logger.info(f"Event Date: {promo.event_info.event_date.strftime('%Y-%m-%d')}")
            logger.info(f"Days until event: {promo.event_info.days_until_event}")
        
        logger.info(f"\nDiscount Details:")
        logger.info(f"  Type: {promo.discount_type}")
        logger.info(f"  Value: {promo.discount_value}%")
        if promo.min_order_value:
            logger.info(f"  Min Order: {promo.min_order_value:,.0f} VND")
        if promo.max_discount_amount:
            logger.info(f"  Max Discount: {promo.max_discount_amount:,.0f} VND")
        
        logger.info(f"\nTiming:")
        logger.info(f"  Start: {promo.start_date.strftime('%Y-%m-%d')}")
        logger.info(f"  End: {promo.end_date.strftime('%Y-%m-%d')}")
        logger.info(f"  Duration: {promo.duration_days} days")
        
        logger.info(f"\nTarget Products: {len(promo.target_products)}")
        for prod in promo.target_products[:5]:
            logger.info(f"  - {prod.product_name} ({prod.status.value})")
        
        if promo.combo_suggestions:
            logger.info(f"\nCombo Suggestions: {len(promo.combo_suggestions)}")
            for combo in promo.combo_suggestions[:3]:
                logger.info(f"  - {combo.product_1_name} + {combo.product_2_name}")
        
        logger.info(f"\nExpected Impact:")
        logger.info(f"  Revenue Impact: {promo.estimated_revenue_impact:+.1f}%")
        logger.info(f"  Order Increase: +{promo.estimated_order_increase} orders")
        logger.info(f"  Risk Level: {promo.risk_level}")
        
        logger.info(f"\nDescription:")
        logger.info(f"  {promo.description}")
    
    return promotions


async def test_smart_promotion_balanced():
    """Test 5: Tạo khuyến mãi thông minh - Balanced"""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: Smart Promotion - Balanced Focus")
    logger.info("="*80)
    
    service = get_event_promotion_service()
    promo = await service.generate_smart_promotion(focus="balanced")
    
    logger.info(f"\n🎯 {promo.promotion_name}")
    logger.info(f"{'='*60}")
    logger.info(f"Strategy: {promo.strategy.value}")
    logger.info(f"Primary Goal: {promo.primary_goal}")
    logger.info(f"Discount: {promo.discount_value}%")
    logger.info(f"Duration: {promo.duration_days} days")
    logger.info(f"\nTarget Products: {len(promo.target_products)}")
    
    slow = [p for p in promo.target_products if p.status.value == "SLOW_MOVING"]
    best = [p for p in promo.target_products if p.status.value == "BEST_SELLER"]
    
    logger.info(f"  - Slow Movers: {len(slow)}")
    logger.info(f"  - Best Sellers: {len(best)}")
    
    logger.info(f"\nExpected Impact:")
    logger.info(f"  Revenue: {promo.estimated_revenue_impact:+.1f}%")
    logger.info(f"  Orders: +{promo.estimated_order_increase}")
    logger.info(f"  Risk: {promo.risk_level}")
    
    return promo


async def test_smart_promotion_clearance():
    """Test 6: Tạo khuyến mãi thông minh - Clearance"""
    logger.info("\n" + "="*80)
    logger.info("TEST 6: Smart Promotion - Clearance Focus")
    logger.info("="*80)
    
    service = get_event_promotion_service()
    promo = await service.generate_smart_promotion(focus="clearance")
    
    logger.info(f"\n🎯 {promo.promotion_name}")
    logger.info(f"{'='*60}")
    logger.info(f"Strategy: {promo.strategy.value}")
    logger.info(f"Primary Goal: {promo.primary_goal}")
    logger.info(f"Discount: {promo.discount_value}% (aggressive)")
    logger.info(f"\nTarget Products (Slow Movers): {len(promo.target_products)}")
    
    for prod in promo.target_products[:10]:
        logger.info(f"  - {prod.product_name}: {prod.total_sold} sold, stock {prod.stock_level}")
    
    logger.info(f"\nExpected Impact:")
    logger.info(f"  Revenue: {promo.estimated_revenue_impact:+.1f}%")
    logger.info(f"  Orders: +{promo.estimated_order_increase}")
    
    return promo


async def test_smart_promotion_revenue():
    """Test 7: Tạo khuyến mãi thông minh - Revenue"""
    logger.info("\n" + "="*80)
    logger.info("TEST 7: Smart Promotion - Revenue Focus")
    logger.info("="*80)
    
    service = get_event_promotion_service()
    promo = await service.generate_smart_promotion(focus="revenue")
    
    logger.info(f"\n🎯 {promo.promotion_name}")
    logger.info(f"{'='*60}")
    logger.info(f"Strategy: {promo.strategy.value}")
    logger.info(f"Primary Goal: {promo.primary_goal}")
    logger.info(f"Discount: {promo.discount_value}% (moderate)")
    logger.info(f"\nTarget Products (High Revenue Contribution):")
    
    for prod in promo.target_products[:10]:
        logger.info(f"  - {prod.product_name}: {prod.revenue_contribution:.1f}% contribution")
    
    logger.info(f"\nExpected Impact:")
    logger.info(f"  Revenue: {promo.estimated_revenue_impact:+.1f}%")
    logger.info(f"  Orders: +{promo.estimated_order_increase}")
    
    return promo


async def main():
    """Run all tests"""
    logger.info("\n" + "🚀"*40)
    logger.info("EVENT-DRIVEN PROMOTION SYSTEM - FULL TEST")
    logger.info("🚀"*40)
    
    try:
        # Test 1: Sales Performance
        analyses = await test_sales_performance_analysis()
        
        # Test 2: Combo Discovery
        combos = await test_combo_discovery()
        
        # Test 3: Event Detection
        events = test_event_detection()
        
        # Test 4: Event-Based Promotion
        event_promotions = await test_event_based_promotion()
        
        # Test 5-7: Smart Promotions
        balanced_promo = await test_smart_promotion_balanced()
        clearance_promo = await test_smart_promotion_clearance()
        revenue_promo = await test_smart_promotion_revenue()
        
        # Summary
        logger.info("\n" + "="*80)
        logger.info("SUMMARY")
        logger.info("="*80)
        logger.info(f"✅ Products Analyzed: {len(analyses)}")
        logger.info(f"✅ Combos Discovered: {len(combos)}")
        logger.info(f"✅ Upcoming Events: {len(events)}")
        logger.info(f"✅ Event-Based Promotions: {len(event_promotions)}")
        logger.info(f"✅ Smart Promotions: 3 (balanced, clearance, revenue)")
        
        logger.info("\n🎉 ALL TESTS PASSED!")
        
        # Save summary to JSON
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_products": len(analyses),
            "slow_movers": len([a for a in analyses if a.status.value == "SLOW_MOVING"]),
            "best_sellers": len([a for a in analyses if a.status.value == "BEST_SELLER"]),
            "combos_found": len(combos),
            "upcoming_events": len(events),
            "event_promotions_generated": len(event_promotions),
            "test_status": "PASSED"
        }
        
        with open("event_promotion_test_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📝 Test results saved to: event_promotion_test_results.json")
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
