"""Debug script to check orders structure"""
from infrastructure.db.mongodb_access import mongodb_data
import json

print("\n" + "="*60)
print("🔍 CHECKING ORDERS DATA STRUCTURE")
print("="*60)

orders_df = mongodb_data.get_orders_data()

if orders_df.empty:
    print("❌ No orders data found")
else:
    print(f"\n✅ Found {len(orders_df)} orders")
    print(f"\n📋 Available columns ({len(orders_df.columns)}):")
    for col in sorted(orders_df.columns):
        print(f"   - {col}")
    
    print(f"\n📊 Sample order data (first record):")
    first_order = orders_df.iloc[0].to_dict()
    print(json.dumps(first_order, indent=2, default=str))
    
    # Check for orderItems columns
    orderItems_cols = [col for col in orders_df.columns if 'orderItems' in col or 'items' in col.lower()]
    print(f"\n🛒 OrderItems related columns ({len(orderItems_cols)}):")
    for col in orderItems_cols:
        print(f"   - {col}")
        print(f"     Sample value: {orders_df[col].iloc[0]}")

print("\n" + "="*60)
