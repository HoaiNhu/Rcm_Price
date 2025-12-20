import os
import json
import hashlib
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

try:
    import redis.asyncio as redis
except ImportError:
    import redis

# Load environment variables
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")


def json_serializer(obj):
    """Custom JSON serializer cho Pydantic models, datetime, ObjectId"""
    if hasattr(obj, 'model_dump'):  # Pydantic v2
        return obj.model_dump()
    elif hasattr(obj, 'dict'):  # Pydantic v1
        return obj.dict()
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)


class PromotionCache:
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

    def _make_key(self, event_type: str, days_ahead: int) -> str:
        """Tạo cache key duy nhất"""
        key = f"promotion:{event_type}:{days_ahead}"
        return hashlib.sha256(key.encode()).hexdigest()

    async def get(self, event_type: str, days_ahead: int) -> Optional[Any]:
        """Lấy dữ liệu từ cache"""
        await self.connect()
        key = self._make_key(event_type, days_ahead)
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, event_type: str, days_ahead: int, value: Any, expire: int = 3600):
        """Lưu dữ liệu vào cache (với Pydantic model serialization)"""
        await self.connect()
        key = self._make_key(event_type, days_ahead)
        # ✅ Sử dụng custom serializer để convert Pydantic models → dict
        await self.redis.set(key, json.dumps(value, default=json_serializer), ex=expire)
