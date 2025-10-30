"""Quick check: Database"""
from configs.database import mongodb_config

client = mongodb_config.get_sync_client()
db = mongodb_config.get_database(client)

orders = db['orders'].count_documents({})
products = db['products'].count_documents({})

print(f"Orders: {orders}")
print(f"Products: {products}")

if products > 0:
    sample = list(db['products'].find().limit(3))
    print(f"\nSample products:")
    for p in sample:
        print(f"  - {p.get('name', 'N/A')}: {p.get('price', 0):,.0f}đ")
