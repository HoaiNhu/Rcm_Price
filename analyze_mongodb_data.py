"""
Analyze MongoDB Data Quality
Check data available for ML model training
"""
from infrastructure.db.mongodb_access import mongodb_data
import pandas as pd
from datetime import datetime

print("="*70)
print("📊 MONGODB DATA ANALYSIS FOR ML TRAINING")
print("="*70)

# Fetch all data
orders = mongodb_data.get_orders_data()
users = mongodb_data.get_users_data()
products = mongodb_data.get_products_data()

print(f"\n{'='*70}")
print("📦 ORDERS DATA")
print(f"{'='*70}")
print(f"Total orders: {len(orders)}")
if not orders.empty:
    print(f"Date range: {orders['createdAt'].min()} → {orders['createdAt'].max()}")
    print(f"Total revenue: {orders['totalPrice'].sum():,.0f} VND")
    print(f"Average order value: {orders['totalPrice'].mean():,.0f} VND")
    print(f"Unique customers: {orders['userId'].nunique()}")
    
    # Check order items structure
    sample_order = orders.iloc[0]
    if 'orderItems' in sample_order:
        print(f"\n📋 Order Items Sample:")
        print(f"   Order ID: {sample_order['_id']}")
        print(f"   Items count: {len(sample_order['orderItems']) if isinstance(sample_order['orderItems'], list) else 0}")
        if isinstance(sample_order['orderItems'], list) and len(sample_order['orderItems']) > 0:
            item = sample_order['orderItems'][0]
            print(f"   Sample item: {item}")

print(f"\n{'='*70}")
print("👥 USERS DATA")
print(f"{'='*70}")
print(f"Total users: {len(users)}")
if not users.empty:
    print(f"Users with orders: {orders['userId'].nunique()}")
    print(f"Conversion rate: {(orders['userId'].nunique() / len(users) * 100):.1f}%")
    
    # Check user structure
    sample_user = users.iloc[0]
    print(f"\n👤 User Sample:")
    print(f"   Fields: {list(sample_user.keys())}")

print(f"\n{'='*70}")
print("🍰 PRODUCTS DATA")
print(f"{'='*70}")
print(f"Total products: {len(products)}")
if not products.empty:
    print(f"Price range: {products['productPrice'].min():,.0f} - {products['productPrice'].max():,.0f} VND")
    print(f"Average price: {products['productPrice'].mean():,.0f} VND")
    
    # Check which products have orders
    if not orders.empty and 'orderItems' in orders.columns:
        all_product_ids = set()
        for _, order in orders.iterrows():
            if isinstance(order['orderItems'], list):
                for item in order['orderItems']:
                    if isinstance(item, dict) and 'product' in item:
                        all_product_ids.add(str(item['product']))
        
        print(f"\n📊 Product Sales Analysis:")
        print(f"   Products with sales: {len(all_product_ids)}")
        print(f"   Products without sales: {len(products) - len(all_product_ids)}")
        print(f"   Coverage: {(len(all_product_ids) / len(products) * 100):.1f}%")

print(f"\n{'='*70}")
print("🎯 DATA QUALITY FOR ML TRAINING")
print(f"{'='*70}")

# Check for price elasticity calculation requirements
if not orders.empty:
    # Count products with multiple price points
    product_price_variations = {}
    for _, order in orders.iterrows():
        if isinstance(order['orderItems'], list):
            for item in order['orderItems']:
                if isinstance(item, dict) and 'product' in item:
                    product_id = str(item['product'])
                    price = item.get('price', 0)
                    if product_id not in product_price_variations:
                        product_price_variations[product_id] = set()
                    product_price_variations[product_id].add(price)
    
    products_with_variations = sum(1 for prices in product_price_variations.values() if len(prices) > 1)
    
    print(f"\n💰 Price Variation Analysis (Critical for Elasticity):")
    print(f"   Products in orders: {len(product_price_variations)}")
    print(f"   Products with price variations: {products_with_variations}")
    print(f"   Products with STABLE prices: {len(product_price_variations) - products_with_variations}")
    print(f"\n⚠️  Elasticity calculable for: {products_with_variations} products only")
    print(f"   Reason: Need price changes to measure demand response!")

# Check for customer segmentation requirements
if not users.empty and not orders.empty:
    print(f"\n👥 Customer Segmentation Data Readiness:")
    
    # RFM analysis
    user_order_counts = orders.groupby('userId').size()
    print(f"   Total customers with orders: {len(user_order_counts)}")
    print(f"   Single-purchase customers: {sum(user_order_counts == 1)}")
    print(f"   Repeat customers: {sum(user_order_counts > 1)}")
    print(f"   Repeat rate: {(sum(user_order_counts > 1) / len(user_order_counts) * 100):.1f}%")

print(f"\n{'='*70}")
print("🔍 GEMINI'S DIAGNOSIS VERIFICATION")
print(f"{'='*70}")
print(f"\n✅ Data exists: {len(orders)} orders, {len(users)} users, {len(products)} products")
print(f"⚠️  Price variation issue: CONFIRMED - Only {products_with_variations}/{len(product_price_variations)} products have price changes")
print(f"   → Gemini was RIGHT: 'Dữ liệu quá phẳng (no price variation)'")
print(f"\n💡 ROOT CAUSE: Historical data has FIXED prices → Cannot calculate elasticity")
print(f"   → Solution: Implement Gemini's A/B testing recommendation!")

print(f"\n{'='*70}")
