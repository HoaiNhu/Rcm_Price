# Fix: StubTensorFlowRecommender Missing Methods

## Vấn Đề (Problem)

Khi chạy API server mà không cài TensorFlow, server báo lỗi:

```
ERROR:application.services.hybrid_recommender:❌ Error initializing hybrid system: 'StubTensorFlowRecommender' object has no attribute 'prepare_data'
```

API endpoints trả về 400 Bad Request:

```
INFO: 127.0.0.1:51048 - "GET /api/hybrid/user-recommendations/676eaf5cbf34ce78983409c3?top_k=10 HTTP/1.1" 400 Bad Request
INFO: 127.0.0.1:64327 - "GET /api/hybrid/promotion-strategy HTTP/1.1" 400 Bad Request
```

## Nguyên Nhân (Root Cause)

Class `StubTensorFlowRecommender` trong `infrastructure/ml_models/tf_recommenders.py` thiếu các methods cần thiết:

- `prepare_data()`
- `build_model()`
- `train_model()`
- `get_similar_products()`

Khi hybrid recommender system gọi các methods này, Python báo lỗi AttributeError.

## Giải Pháp (Solution)

Thêm đầy đủ các methods vào class `StubTensorFlowRecommender`:

```python
class StubTensorFlowRecommender:
    """Stub class when TensorFlow is not available"""

    def __init__(self):
        self.is_trained = False
        self.user_model = None
        self.product_model = None
        self.task = None
        self.model = None
        logger.info("⚠️ Using stub TF Recommender (TensorFlow not installed)")

    def prepare_data(self, orders_df: pd.DataFrame, products_df: pd.DataFrame, users_df: pd.DataFrame):
        """No-op prepare_data method"""
        logger.warning("TensorFlow not available - skipping data preparation")
        return None

    def build_model(self, dataset):
        """No-op build_model method"""
        logger.warning("TensorFlow not available - skipping model building")
        return False

    def train_model(self, dataset, epochs=3):
        """No-op train_model method"""
        logger.warning("TensorFlow not available - skipping model training")
        return False

    def get_recommendations(self, user_id: str, top_k: int = 10) -> List[Dict]:
        """Return empty recommendations"""
        logger.warning("TensorFlow not available - no collaborative filtering recommendations")
        return []

    def get_similar_products(self, product_id: str, top_k: int = 5) -> List[Dict]:
        """Return empty similar products"""
        logger.warning("TensorFlow not available - no similar products")
        return []

    def train(self, *args, **kwargs):
        """No-op train method"""
        logger.warning("TensorFlow not available - skipping training")
        return False
```

## File Đã Sửa (Modified Files)

- `infrastructure/ml_models/tf_recommenders.py`

## Kết Quả (Result)

✅ Server khởi động thành công không lỗi:

```
INFO:application.services.hybrid_recommender:✅ Hybrid Recommendation System initialized
INFO:__main__:✅ All AI services initialized successfully
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ Hybrid system khởi động OK (dù không có TensorFlow):

```
WARNING:infrastructure.ml_models.tf_recommenders:⚠️ TensorFlow not available - returning stub recommender
INFO:infrastructure.ml_models.tf_recommenders:⚠️ Using stub TF Recommender (TensorFlow not installed)
```

✅ API endpoints giờ có thể gọi được (không còn 400 Bad Request)

## Lưu Ý (Notes)

1. **Stub class** chỉ trả về empty results, không có recommendation thực sự từ TensorFlow
2. Để có full functionality, cài TensorFlow: `pip install tensorflow==2.15.0 tensorflow-recommenders`
3. Hệ thống vẫn hoạt động với:
   - HuggingFace Content Filter (semantic search)
   - Dynamic Pricing Model
   - Gemini LLM recommendations

## Cách Test (How to Test)

1. **Start server:**

   ```powershell
   $env:PYTHONPATH="c:\Users\Lenovo\STUDY\RCM_PRICE"
   python app\main.py
   ```

2. **Test health endpoint:**

   ```powershell
   python test_health.py
   ```

   hoặc

   ```powershell
   curl http://localhost:8000/health
   ```

3. **Test hybrid endpoints:**
   ```
   GET http://localhost:8000/api/hybrid/initialize
   GET http://localhost:8000/api/hybrid/user-recommendations/676eaf5cbf34ce78983409c3?top_k=10
   GET http://localhost:8000/api/hybrid/promotion-strategy
   ```

## Tài Liệu Liên Quan (Related Documentation)

- `FIX_MONGODB_CONNECTION.md` - Fix MongoDB connection issue
- `INSTALLATION_GUIDE.md` - Dependencies installation guide
- `requirements-minimal.txt` - Minimal dependencies (no TensorFlow)
- `requirements-full.txt` - Full dependencies (with TensorFlow)

---

**Ngày sửa:** 11/10/2025
**Status:** ✅ RESOLVED
