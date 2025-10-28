"""
Script to print MongoDB data from all collections
Author: HoaiNhu
Date: 2025-10-28
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb+srv://hnhu:hoainhu1234@webbuycake.asd8v.mongodb.net/?retryWrites=true&w=majority&appName=WebBuyCake')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'test')

def print_separator(title, char='='):
    """Print a separator line with title"""
    print(f"\n{'=' * 80}")
    print(f"{title.center(80)}")
    print(f"{'=' * 80}\n")

def format_value(value):
    """Format value for pretty printing"""
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, default=str)
    return str(value)

def print_collection_data(db, collection_name, limit=None):
    """
    Print data from a MongoDB collection
    
    Args:
        db: MongoDB database instance
        collection_name: Name of the collection to print
        limit: Maximum number of documents to print (None = all)
    """
    try:
        collection = db[collection_name]
        
        # Get collection stats
        total_count = collection.count_documents({})
        
        print_separator(f"Collection: {collection_name}")
        print(f"📊 Total documents: {total_count}")
        
        if total_count == 0:
            print("⚠️  Collection is empty!")
            return
        
        # Get documents
        documents = collection.find().limit(limit) if limit else collection.find()
        
        print(f"\n{'─' * 80}")
        
        for idx, doc in enumerate(documents, 1):
            print(f"\n📄 Document #{idx}")
            print(f"{'─' * 80}")
            
            for key, value in doc.items():
                if key == '_id':
                    print(f"  {key}: {value}")
                else:
                    formatted_value = format_value(value)
                    # Handle multi-line values
                    if '\n' in formatted_value:
                        print(f"  {key}:")
                        for line in formatted_value.split('\n'):
                            print(f"    {line}")
                    else:
                        print(f"  {key}: {formatted_value}")
            
            print(f"{'─' * 80}")
        
        if limit and total_count > limit:
            print(f"\n⚠️  Showing {limit} of {total_count} documents")
        
    except Exception as e:
        print(f"❌ Error reading collection '{collection_name}': {str(e)}")

def print_all_collections(db, limit_per_collection=10):
    """
    Print data from all collections in the database
    
    Args:
        db: MongoDB database instance
        limit_per_collection: Maximum documents to print per collection
    """
    try:
        # Get all collection names
        collection_names = db.list_collection_names()
        
        print_separator(f"Database: {db.name}", '=')
        print(f"📚 Total collections: {len(collection_names)}")
        print(f"📋 Collections: {', '.join(collection_names)}\n")
        
        # Print each collection
        for collection_name in collection_names:
            print_collection_data(db, collection_name, limit_per_collection)
        
    except Exception as e:
        print(f"❌ Error listing collections: {str(e)}")

def main():
    """Main function to connect to MongoDB and print data"""
    print_separator("MongoDB Data Viewer", '═')
    print(f"🔗 Connecting to MongoDB...")
    print(f"📍 Database: {DATABASE_NAME}")
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Test connection
        client.server_info()
        print(f"✅ Connected successfully!\n")
        
        # Print all collections with limit
        print("📖 Showing up to 10 documents per collection")
        print("   (Edit 'limit_per_collection' parameter to show more)\n")
        print_all_collections(db, limit_per_collection=10)
        
        # Summary
        print_separator("Summary", '═')
        collection_stats = []
        for coll_name in db.list_collection_names():
            count = db[coll_name].count_documents({})
            collection_stats.append((coll_name, count))
        
        print("📊 Collection Statistics:")
        for coll_name, count in sorted(collection_stats, key=lambda x: x[1], reverse=True):
            print(f"   • {coll_name}: {count} documents")
        
        print(f"\n{'═' * 80}")
        print("✅ Done!")
        
    except Exception as e:
        print(f"\n❌ Connection Error: {str(e)}")
        print("\n💡 Tips:")
        print("   1. Check your MONGODB_URL in .env file")
        print("   2. Verify network connection")
        print("   3. Ensure MongoDB Atlas whitelist includes your IP")
    
    finally:
        if 'client' in locals():
            client.close()
            print("🔌 Connection closed.")

# Alternative functions for specific use cases
def print_specific_collections(collection_names, limit=None):
    """Print specific collections only"""
    try:
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        print_separator(f"Specific Collections: {', '.join(collection_names)}")
        
        for coll_name in collection_names:
            print_collection_data(db, coll_name, limit)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def export_to_file(collection_name, output_file='output.txt', limit=None):
    """Export collection data to text file"""
    try:
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        collection = db[collection_name]
        
        documents = collection.find().limit(limit) if limit else collection.find()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Collection: {collection_name}\n")
            f.write(f"{'=' * 80}\n\n")
            
            for idx, doc in enumerate(documents, 1):
                f.write(f"Document #{idx}\n")
                f.write(json.dumps(doc, indent=2, default=str, ensure_ascii=False))
                f.write(f"\n{'-' * 80}\n\n")
        
        print(f"✅ Exported to {output_file}")
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Run main function
    main()
    
    # Examples of alternative usage (uncomment to use):
    
    # Print specific collections only
    # print_specific_collections(['products', 'orders'], limit=5)
    
    # Export to file
    # export_to_file('products', 'products_data.txt', limit=20)
