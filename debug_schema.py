"""Debug script to check actual MongoDB schema"""
import asyncio
from configs.database import mongodb_config

async def check_schema():
    client = mongodb_config.get_async_client()
    db = mongodb_config.get_database(async_client=True)
    
    print("=== ORDERS Schema ===\n")
    orders = await db['orders'].find({}).limit(2).to_list(None)
    
    if orders:
        print("Sample Order #1:")
        for key, value in orders[0].items():
            print(f"  {key}: {value} (type: {type(value).__name__})")
    
    print("\n=== PRODUCTS Schema ===\n")
    products = await db['products'].find({}).limit(2).to_list(None)
    
    if products:
        print("Sample Product #1:")
        for key, value in products[0].items():
            print(f"  {key}: {value} (type: {type(value).__name__})")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_schema())
