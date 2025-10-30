"""Check order structure"""
from configs.database import mongodb_config

client = mongodb_config.get_sync_client()
db = mongodb_config.get_database(client)

order = db['orders'].find_one({'orderItems': {'$exists': True, '$ne': []}})
if order:
    print("Order fields:")
    for key in order.keys():
        print(f"  - {key}: {type(order[key]).__name__}")
    
    if 'orderItems' in order and order['orderItems']:
        print("\nFirst orderItem structure:")
        item = order['orderItems'][0]
        for key in item.keys():
            print(f"  - {key}: {type(item[key]).__name__} = {item[key]}")
else:
    print("No orders with items!")
