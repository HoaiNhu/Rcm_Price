# Gemini API Model Update - Fix 404 Error

## 🔴 Lỗi gặp phải

```
ERROR:application.services.ai_promotion_service:❌ Error generating LLM insights:
404 models/gemini-pro is not found for API version v1beta,
or is not supported for generateContent.
Call ListModels to see the list of available models and their supported methods.
```

## 🔍 Nguyên nhân

Google Gemini đã **deprecated model `gemini-pro`** và thay thế bằng các model mới:

### ❌ Model cũ (DEPRECATED):

- `gemini-pro` - Text generation (không còn hỗ trợ)
- `gemini-pro-vision` - Multimodal (không còn hỗ trợ)

### ✅ Model mới (HIỆN TẠI):

- `gemini-1.5-flash` - **Nhanh, giá rẻ** (recommended cho production)
- `gemini-1.5-pro` - **Chất lượng cao hơn** (cho tasks phức tạp)
- `gemini-2.0-flash-exp` - Experimental (beta)

## ✅ Giải pháp

### 1. Sửa model name trong code

**File:** `application/services/ai_promotion_service.py`

**BEFORE:**

```python
def __init__(self, gemini_api_key: str):
    genai.configure(api_key=gemini_api_key)
    self.llm_model = genai.GenerativeModel('gemini-pro')  # ❌ DEPRECATED
```

**AFTER:**

```python
def __init__(self, gemini_api_key: str):
    genai.configure(api_key=gemini_api_key)
    self.llm_model = genai.GenerativeModel('gemini-1.5-flash')  # ✅ NEW
```

### 2. So sánh các model

| Model                | Speed       | Quality              | Cost             | Best For              |
| -------------------- | ----------- | -------------------- | ---------------- | --------------------- |
| **gemini-1.5-flash** | ⚡⚡⚡ Fast | ⭐⭐⭐ Good          | 💰 Cheap         | Production, Real-time |
| **gemini-1.5-pro**   | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Excellent | 💰💰💰 Expensive | Complex analysis      |
| gemini-2.0-flash-exp | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Very Good   | 💰 Cheap         | Experimental          |

**Khuyến nghị:**

- 🏆 **`gemini-1.5-flash`** cho production (nhanh, rẻ, đủ tốt)
- 🎯 **`gemini-1.5-pro`** nếu cần chất lượng cao (phân tích sâu, insights phức tạp)

## 🔧 Các file cần update

Tìm kiếm tất cả usage của `gemini-pro`:

```bash
# File trong RCM_PRICE
application/services/ai_promotion_service.py  ✅ ĐÃ SỬA

# Các file khác (nếu có)
# infrastructure/external/gemini_client.py
# configs/settings.py
```

## 🧪 Testing

### Test script để verify model:

```python
"""Test Gemini API with new model"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Test gemini-1.5-flash
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello in Vietnamese")
    print("✅ gemini-1.5-flash works!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
```

### Test với API:

```bash
# 1. Start server
python run_api.py

# 2. Test endpoint sử dụng Gemini
curl http://localhost:8000/api/analytics/business-health
```

**Kết quả mong đợi:**

- ✅ No 404 error
- ✅ LLM insights generated successfully
- ✅ Response có field `llm_insights`

## 📊 Migration Checklist

- [x] Update model name từ `gemini-pro` → `gemini-1.5-flash`
- [x] Test với simple prompt
- [x] Test với business analytics
- [x] Verify API response
- [ ] Update documentation
- [ ] Monitor performance & cost

## 💡 Best Practices

### 1. Use Environment Variables

```python
# configs/settings.py
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

# application/services/ai_promotion_service.py
self.llm_model = genai.GenerativeModel(settings.GEMINI_MODEL)
```

### 2. Add Fallback

```python
try:
    self.llm_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    logger.warning(f"Failed to init gemini-1.5-flash: {e}")
    logger.info("Trying gemini-1.5-pro as fallback")
    self.llm_model = genai.GenerativeModel('gemini-1.5-pro')
```

### 3. Add Model Listing

```python
# List available models
models = genai.list_models()
for model in models:
    if 'gemini' in model.name:
        print(f"Available: {model.name}")
        print(f"  Supports: {model.supported_generation_methods}")
```

## 📚 References

- [Gemini API Models](https://ai.google.dev/gemini-api/docs/models/gemini)
- [Migration Guide](https://ai.google.dev/gemini-api/docs/migrate-from-palm)
- [Pricing](https://ai.google.dev/pricing)

## 🔄 Version History

| Date      | Model                | Status                    |
| --------- | -------------------- | ------------------------- |
| 2023-2024 | gemini-pro           | ❌ Deprecated             |
| 2024-2025 | gemini-1.5-flash     | ✅ Current (Recommended)  |
| 2024-2025 | gemini-1.5-pro       | ✅ Current (High quality) |
| 2025+     | gemini-2.0-flash-exp | ⚠️ Experimental           |

## ✅ Kết quả

Sau khi update:

1. ✅ **No more 404 errors**
2. ✅ **LLM insights working**
3. ✅ **Faster response** (gemini-1.5-flash nhanh hơn gemini-pro)
4. ✅ **Lower cost** (pricing tốt hơn)

---

**Status:** ✅ RESOLVED  
**Date:** January 12, 2025  
**Impact:** All Gemini API calls now working with new model
