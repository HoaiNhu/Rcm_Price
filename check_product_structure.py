"""Check product structure"""
from configs.database import mongodb_config

client = mongodb_config.get_sync_client()
db = mongodb_config.get_database(client)

product = db['products'].find_one({})
if product:
    print("Product fields:")
    for key in product.keys():
        print(f"  - {key}: {type(product[key]).__name__}")
    
    print("\nSample product:")
    print(product)
else:
    print("No products!")
