"""Debug pricing strategy issue"""
from infrastructure.db.mongodb_access import mongodb_data
from infrastructure.ml_models.dynamic_pricing import DynamicPricingModel
import pandas as pd

print("\n" + "="*60)
print("🔍 DEBUG PRICING STRATEGY ISSUE")
print("="*60)

# Get data
print("\n1️⃣ Loading data from MongoDB...")
orders_df = mongodb_data.get_orders_data()
products_df = mongodb_data.get_products_data()

print(f"   Orders: {len(orders_df)}")
print(f"   Products: {len(products_df)}")

# Create pricing model
print("\n2️⃣ Creating Dynamic Pricing Model...")
pricing_model = DynamicPricingModel()
print(f"   is_trained: {pricing_model.is_trained}")

# Prepare pricing data
print("\n3️⃣ Preparing pricing data...")
pricing_df = pricing_model.prepare_pricing_data(orders_df, products_df)
print(f"   Pricing records: {len(pricing_df)}")

if not pricing_df.empty:
    print(f"   Columns: {list(pricing_df.columns)}")
    print(f"\n   Sample data:")
    print(pricing_df.head(3))
else:
    print("   ❌ Pricing data is EMPTY!")

# Train models
print("\n4️⃣ Training pricing models...")
if not pricing_df.empty:
    success = pricing_model.train_models(pricing_df)
    print(f"   Training success: {success}")
    print(f"   is_trained: {pricing_model.is_trained}")
else:
    print("   ⚠️ Skipped (no data)")

# Try to get strategy
print("\n5️⃣ Getting promotion strategy...")
strategy = pricing_model.get_promotion_strategy(products_df, pricing_df)

print(f"\n📊 STRATEGY RESULT:")
print(f"   increase_price: {len(strategy.get('increase_price', []))} products")
print(f"   decrease_price: {len(strategy.get('decrease_price', []))} products")
print(f"   keep_price: {len(strategy.get('keep_price', []))} products")
print(f"   promotion_candidates: {len(strategy.get('promotion_candidates', []))} products")

if not strategy or all(len(v) == 0 for v in strategy.values()):
    print("\n❌ PROBLEM: Strategy is empty!")
    print(f"   is_trained: {pricing_model.is_trained}")
    print(f"   pricing_df empty: {pricing_df.empty}")
    
    # Check products with price
    products_with_price = products_df[products_df['productPrice'] > 0]
    print(f"   Products with price > 0: {len(products_with_price)}/{len(products_df)}")
    
print("\n" + "="*60)
