"""
Check order date ranges in MongoDB
"""
from infrastructure.db.mongodb_access import mongodb_data
import pandas as pd

print("=" * 60)
print("Checking Order Date Ranges in MongoDB")
print("=" * 60)

# Get all orders without date filter
df = mongodb_data.get_orders_data()

if df.empty:
    print("❌ No orders found in database!")
else:
    print(f"\n✅ Total orders in DB: {len(df)}")
    
    if 'createdAt' in df.columns:
        # Convert to datetime if needed
        if df['createdAt'].dtype != 'datetime64[ns]':
            df['createdAt'] = pd.to_datetime(df['createdAt'])
        
        print(f"\n📅 Date Range:")
        print(f"   Earliest order: {df['createdAt'].min()}")
        print(f"   Latest order:   {df['createdAt'].max()}")
        
        # Group by month
        df['month'] = df['createdAt'].dt.to_period('M')
        monthly_counts = df.groupby('month').size().sort_index()
        
        print(f"\n📊 Orders by Month:")
        for month, count in monthly_counts.items():
            print(f"   {month}: {count} orders")
        
        # Show sample orders
        print(f"\n📋 Sample Orders (first 5):")
        sample = df[['orderCode', 'createdAt', 'totalPrice']].head(5)
        print(sample.to_string(index=False))
    else:
        print("⚠️ No 'createdAt' column found in orders data")

print("\n" + "=" * 60)
print("💡 Suggestion:")
print("   Use date range from the actual data above")
print("   Example: start_date=2024-12-01&end_date=2025-01-31")
print("=" * 60)
