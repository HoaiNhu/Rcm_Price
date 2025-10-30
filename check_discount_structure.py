"""
Check Discount Collection Structure
"""
from infrastructure.db.mongodb_access import mongodb_data
import json
from bson import ObjectId

print("="*70)
print("📊 DISCOUNT COLLECTION ANALYSIS")
print("="*70)

db = mongodb_data.db
discounts = list(db['discounts'].find().limit(5))

print(f"\n📦 Total discounts: {db['discounts'].count_documents({})}")

if discounts:
    print(f"\n💳 Sample Discount Structure:")
    sample = discounts[0]
    
    # Convert ObjectId to string for display
    for key, value in sample.items():
        if isinstance(value, ObjectId):
            sample[key] = str(value)
    
    print(json.dumps(sample, indent=2, ensure_ascii=False, default=str))
    
    print(f"\n📋 All Fields Available:")
    for field in sample.keys():
        print(f"   - {field}: {type(sample[field]).__name__}")
else:
    print("\n⚠️ No discount data found")

print("\n" + "="*70)
