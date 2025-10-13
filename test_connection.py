"""
Test MongoDB Connection and Data Availability
Run this before starting the API server
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("🔍 MONGODB CONNECTION TEST")
print("=" * 70)

# Check environment variables
mongodb_url = os.getenv("MONGODB_URL", "NOT_SET")
database_name = os.getenv("DATABASE_NAME", "NOT_SET")
gemini_key = os.getenv("GEMINI_API_KEY", "NOT_SET")

print(f"\n📝 Environment Variables:")
print(f"  MONGODB_URL: {mongodb_url[:50]}..." if len(mongodb_url) > 50 else f"  MONGODB_URL: {mongodb_url}")
print(f"  DATABASE_NAME: {database_name}")
print(f"  GEMINI_API_KEY: {'✅ Set' if gemini_key != 'NOT_SET' else '❌ Not set'}")

# Test MongoDB connection
print(f"\n{'=' * 70}")
print("🔌 Testing MongoDB Connection...")
print("=" * 70)

try:
    from configs.database import mongodb_config
    
    # Get client
    client = mongodb_config.get_sync_client()
    db = client[mongodb_config.DATABASE_NAME]
    
    # List collections
    collections = db.list_collection_names()
    print(f"\n✅ Connected to MongoDB Atlas")
    print(f"📊 Database: {mongodb_config.DATABASE_NAME}")
    print(f"📁 Collections ({len(collections)}): {', '.join(collections[:10])}")
    
    # Count documents
    print(f"\n{'=' * 70}")
    print("📈 Data Availability:")
    print("=" * 70)
    
    counts = {
        'products': db.products.count_documents({}),
        'orders': db.orders.count_documents({}),
        'users': db.users.count_documents({}),
        'categories': db.categories.count_documents({}),
        'ratings': db.ratings.count_documents({}) if 'ratings' in collections else 0,
        'discounts': db.discounts.count_documents({}) if 'discounts' in collections else 0,
    }
    
    for collection, count in counts.items():
        status = "✅" if count > 0 else "⚠️"
        print(f"  {status} {collection:20s}: {count:5d} documents")
    
    # Sample data
    print(f"\n{'=' * 70}")
    print("📦 Sample Product:")
    print("=" * 70)
    
    sample_product = db.products.find_one()
    if sample_product:
        print(f"  ID: {sample_product.get('_id')}")
        print(f"  Name: {sample_product.get('productName', 'N/A')}")
        print(f"  Price: {sample_product.get('productPrice', 'N/A')}")
        print(f"  Category: {sample_product.get('categoryId', 'N/A')}")
    
    print(f"\n{'=' * 70}")
    print("📦 Sample Order:")
    print("=" * 70)
    
    sample_order = db.orders.find_one()
    if sample_order:
        print(f"  ID: {sample_order.get('_id')}")
        print(f"  User: {sample_order.get('userId', 'N/A')}")
        print(f"  Total: {sample_order.get('totalPrice', 'N/A')}")
        print(f"  Status: {sample_order.get('status', 'N/A')}")
    
    # Close connection
    client.close()
    
    print(f"\n{'=' * 70}")
    print("✅ MongoDB Connection Test: SUCCESS")
    print("=" * 70)
    print("\n🚀 You can now start the API server:")
    print("   python app/main.py")
    print("   or")
    print("   uvicorn app.main:app --reload")
    print("=" * 70 + "\n")
    
except Exception as e:
    print(f"\n{'=' * 70}")
    print("❌ MongoDB Connection Test: FAILED")
    print("=" * 70)
    print(f"\nError: {str(e)}")
    print(f"\n💡 Troubleshooting:")
    print("   1. Check MONGODB_URL in .env file")
    print("   2. Verify MongoDB Atlas is accessible")
    print("   3. Check network/firewall settings")
    print("   4. Verify database name is correct")
    print("=" * 70 + "\n")
