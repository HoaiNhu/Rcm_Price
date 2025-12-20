"""
Script để clear Redis cache cũ (chứa serialization lỗi)
"""
import asyncio
import os
from dotenv import load_dotenv

try:
    import redis.asyncio as redis
except ImportError:
    import redis

load_dotenv()

async def clear_cache():
    """Clear tất cả cache promotion trong Redis"""
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("❌ REDIS_URL not found in .env")
        return
    
    r = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    
    # Lấy tất cả keys có pattern promotion:*
    keys = await r.keys("*")
    
    if not keys:
        print("✅ No cache keys found")
        await r.close()
        return
    
    print(f"🔍 Found {len(keys)} cache keys:")
    for key in keys:
        print(f"  - {key}")
    
    # Xóa tất cả keys
    deleted = await r.delete(*keys)
    print(f"\n✅ Deleted {deleted} cache keys")
    
    await r.close()

if __name__ == "__main__":
    asyncio.run(clear_cache())
