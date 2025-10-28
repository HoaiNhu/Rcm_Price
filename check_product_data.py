"""Quick check for product data in MongoDB"""
import asyncio
from configs.database import mongodb_config

async def check_products():
    # Get async client
    client = mongodb_config.get_async_client()
    db = mongodb_config.get_database(async_client=True)
    
    print("=== Checking Products Collection ===\n")
    
    # Get products
    products = await db['products'].find({}).to_list(None)
    print(f"Total products: {len(products)}\n")
    
    if len(products) > 0:
        print("Sample products:")
        for i, prod in enumerate(products[:5], 1):
            print(f"{i}. ID: {prod['_id']}")
            print(f"   Name: {prod.get('productName', 'N/A')}")
            print(f"   Price: {prod.get('productPrice', 'N/A'):,} VND")
            print()
    
    print("\n=== Checking Orders Collection ===\n")
    
    # Get orders
    orders = await db['orders'].find({}).to_list(None)
    print(f"Total orders: {len(orders)}\n")
    
    if len(orders) > 0:
        print("Sample orders:")
        for i, order in enumerate(orders[:3], 1):
            print(f"{i}. Order: {order.get('orderCode', 'N/A')}")
            print(f"   Status: {order.get('status', 'N/A')}")
            print(f"   Items: {len(order.get('orderItems', []))}")
            print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_products())
