"""
Test script to verify ObjectId serialization fix
"""
import sys
import json
from bson import ObjectId
from utils.numpy_serializer import convert_numpy_types

# Test data mimicking MongoDB structure
test_data = {
    '_id': ObjectId('67643c2411d943b7bdecb7d3'),
    'productName': 'Bánh hoa xuân',
    'productPrice': 260000,
    'productCategory': ObjectId('6762afc337b12f4ea0bb0187'),
    'orderItems': [
        {
            'product': ObjectId('67643c2411d943b7bdecb7d3'),
            'quantity': 3,
            'total': 750000,
            '_id': ObjectId('676d7cce4d065cdde8cce2c7')
        }
    ],
    'userId': ObjectId('6756e4441df899603742e267'),
    'status': ObjectId('6770a84d0ec3917f0a7c9559')
}

print("=" * 60)
print("Testing ObjectId Serialization Fix")
print("=" * 60)

print("\n1. Original data structure:")
print(f"Type of _id: {type(test_data['_id'])}")
print(f"Type of productCategory: {type(test_data['productCategory'])}")
print(f"Type of orderItems[0]['product']: {type(test_data['orderItems'][0]['product'])}")

print("\n2. Converting with convert_numpy_types()...")
cleaned_data = convert_numpy_types(test_data)

print("\n3. Cleaned data structure:")
print(f"Type of _id: {type(cleaned_data['_id'])}")
print(f"Type of productCategory: {type(cleaned_data['productCategory'])}")
print(f"Type of orderItems[0]['product']: {type(cleaned_data['orderItems'][0]['product'])}")

print("\n4. Attempting JSON serialization...")
try:
    json_str = json.dumps(cleaned_data, indent=2, ensure_ascii=False)
    print("✅ JSON serialization successful!")
    print("\nFirst 500 characters of JSON:")
    print(json_str[:500])
    print("\n✅ All ObjectId values converted to strings!")
except Exception as e:
    print(f"❌ JSON serialization failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Test completed successfully!")
print("=" * 60)
