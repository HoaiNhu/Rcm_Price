"""
Router-level cache for Event Promotions
Caches the final API response (after serialization) để tránh issues với domain objects
"""
import os
import json
import hashlib
from typing import Optional, Any, List
from dotenv import load_dotenv
from functools import wraps
from fastapi.encoders import jsonable_encoder

try:
    import redis.asyncio as redis
except ImportError:
    import redis

# Load environment variables
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

class ResponseCache:
    """Cache for API responses (JSON-serializable data)"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or REDIS_URL
        self.redis = None

    async def connect(self):
        """Kết nối đến Redis"""
        if not self.redis:
            self.redis = redis.from_url(
                self.redis_url, 
                encoding="utf-8", 
                decode_responses=True
            )

    def _make_key(self, prefix: str, **params) -> str:
        """Tạo cache key từ params"""
        # Sort params để đảm bảo key consistent
        sorted_params = sorted(params.items())
        param_str = json.dumps(sorted_params)
        key = f"{prefix}:{param_str}"
        return hashlib.sha256(key.encode()).hexdigest()

    async def get(self, prefix: str, **params) -> Optional[List[dict]]:
        """Lấy dữ liệu từ cache"""
        await self.connect()
        key = self._make_key(prefix, **params)
        data = await self.redis.get(key)
        if data:
            try:
                parsed = json.loads(data)
            except Exception:
                # If stored data is not valid JSON (possible old caches using str()),
                # return None so the caller regenerates and overwrites the cache.
                return None

            # Defensive: if parsed is a list of strings that look like Python repr of
            # Pydantic models (e.g. "promotion_id='...' promotion_name='...'") treat as corrupt
            if isinstance(parsed, list) and parsed and isinstance(parsed[0], str):
                sample = parsed[0]
                if "promotion_id=" in sample or "ProductAnalysisResponse" in sample:
                    return None

            return parsed
        return None

    async def set(self, prefix: str, value: List[dict], expire: int = 3600, **params):
        """Lưu dữ liệu vào cache"""
        await self.connect()
        key = self._make_key(prefix, **params)
        # Use FastAPI's jsonable_encoder to properly convert Pydantic models,
        # datetimes and other complex objects to JSON-serializable types before dumping.
        serializable = jsonable_encoder(value)
        await self.redis.set(key, json.dumps(serializable, default=str), ex=expire)

# Singleton instance
_cache_instance = None

def get_response_cache() -> ResponseCache:
    """Get singleton cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ResponseCache()
    return _cache_instance
