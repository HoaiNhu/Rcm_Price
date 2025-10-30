"""Debug items_df"""
import pandas as pd
from datetime import datetime, timedelta
from application.services.data_access_layer import DataAccessLayer

dal = DataAccessLayer()
orders_df = dal.get_orders_data()

print(f"Total orders: {len(orders_df)}")

# Filter recent
orders_df['createdAt'] = pd.to_datetime(orders_df['createdAt'])
cutoff = datetime.now() - timedelta(days=30)
recent = orders_df[orders_df['createdAt'] >= cutoff]
print(f"Recent orders (30 days): {len(recent)}")

# Flatten
items = []
for _, order in recent.iterrows():
    if 'orderItems' in order and isinstance(order['orderItems'], list):
        for item in order['orderItems']:
            if isinstance(item, dict):
                items.append({
                    'product_id': str(item.get('product', '')),
                    'quantity': item.get('quantity', 0),
                    'total': item.get('total', 0)
                })

print(f"Flattened items: {len(items)}")

if items:
    items_df = pd.DataFrame(items)
    print(f"\nItems DataFrame shape: {items_df.shape}")
    print(f"\nSample items:")
    print(items_df.head())
    
    print(f"\nUnique products: {items_df['product_id'].nunique()}")
    print(f"Total quantity sold: {items_df['quantity'].sum()}")
else:
    print("No items found!")
