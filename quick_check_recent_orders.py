"""Simple check: Do orders have items in last 30 days?"""
from configs.database import mongodb_config
from datetime import datetime, timedelta

client = mongodb_config.get_sync_client()
db = mongodb_config.get_database(client)

cutoff = datetime.now() - timedelta(days=30)

# Count recent orders
recent_count = db['orders'].count_documents({'createdAt': {'$gte': cutoff}})
print(f"Recent orders (30 days): {recent_count}")

# Get one order with items
order = db['orders'].find_one({
    'createdAt': {'$gte': cutoff},
    'orderItems': {'$exists': True, '$ne': []}
})

if order:
    print(f"\nSample order:")
    print(f"  - Created: {order['createdAt']}")
    print(f"  - Items: {len(order['orderItems'])}")
    
    for i, item in enumerate(order['orderItems'][:3], 1):
        print(f"\n  Item #{i}:")
        print(f"    - Product ID: {item.get('product')}")
        print(f"    - Quantity: {item.get('quantity')}")
        print(f"    - Total: {item.get('total')}")
else:
    print("\nNo recent orders with items!")
