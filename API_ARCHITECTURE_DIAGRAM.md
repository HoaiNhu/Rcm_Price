# 🎨 API ARCHITECTURE & FLOW DIAGRAM

## 📐 SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATIONS                      │
│  (Website, Mobile App, Admin Dashboard, Marketing Tools)        │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                         │
│                         (Port 8000)                              │
├─────────────────────────────────────────────────────────────────┤
│  📋 Basic Endpoints              💾 Data Access                 │
│  ├─ GET /                        ├─ GET /api/data/orders        │
│  └─ GET /health                  ├─ GET /api/data/products      │
│                                   ├─ GET /api/data/users         │
│  🤖 Hybrid System                ├─ GET /api/data/ratings       │
│  ├─ POST /initialize             └─ GET /api/data/discounts     │
│  ├─ GET /user-recommendations                                   │
│  ├─ GET /product-recommendations  📊 Analytics                  │
│  └─ GET /promotion-strategy      ├─ GET /business-health        │
│                                   ├─ GET /product-performance    │
│  🧠 Individual Models             ├─ GET /customer-insights     │
│  ├─ GET /tf-recommenders/*       └─ GET /trends                 │
│  ├─ GET /huggingface/*                                          │
│  └─ GET /pricing/*                                              │
└──────────────┬──────────────────────────────────┬───────────────┘
               │                                  │
               ▼                                  ▼
┌──────────────────────────────┐   ┌─────────────────────────────┐
│   APPLICATION LAYER          │   │   INFRASTRUCTURE LAYER      │
├──────────────────────────────┤   ├─────────────────────────────┤
│ • AI Promotion Service       │   │ • MongoDB Data Access       │
│ • Hybrid Recommender         │   │ • TensorFlow Recommenders   │
│   - User Recommendations     │   │ • HuggingFace Filter        │
│   - Product Recommendations  │   │ • Dynamic Pricing Model     │
│   - Promotion Strategy       │   │ • Gemini LLM Integration    │
└──────────────┬───────────────┘   └─────────────┬───────────────┘
               │                                  │
               └──────────────┬───────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │          EXTERNAL SERVICES                  │
        ├─────────────────────────────────────────────┤
        │ 🗄️  MongoDB Atlas (Database)               │
        │     - products (31 docs)                   │
        │     - orders (111 docs)                    │
        │     - users (22 docs)                      │
        │     - ratings (26 docs)                    │
        │     - discounts (3 docs)                   │
        │                                             │
        │ 🤖  Google Gemini AI (LLM)                 │
        │     - Strategy generation                  │
        │     - Business insights                    │
        │     - Recommendations                      │
        └─────────────────────────────────────────────┘
```

---

## 🔄 REQUEST FLOW DIAGRAMS

### Flow 1: Initialize Hybrid System

```
┌────────┐                                                    ┌─────────┐
│ Client │                                                    │ MongoDB │
└───┬────┘                                                    └────┬────┘
    │                                                              │
    │ POST /api/hybrid/initialize                                 │
    ├────────────────────────────────────────────────┐            │
    │                                                 │            │
    │                                    ┌────────────▼──────┐    │
    │                                    │  Hybrid           │    │
    │                                    │  Recommender      │    │
    │  200 OK                            │  System           │    │
    │  {status: "processing"}            └────────┬──────────┘    │
    ◄────────────────────────────────────         │               │
    │                                              │               │
    │                                              │ Load data     │
    │                                              ├──────────────►│
    │                                              │               │
    │                                              │ 111 orders    │
    │                                              │ 31 products   │
    │                                              │ 22 users      │
    │                                              ◄───────────────┤
    │                                              │               │
    │                                    ┌─────────▼──────────┐    │
    │                                    │ TensorFlow         │    │
    │                                    │ prepare_data()     │    │
    │                                    │ build_model()      │    │
    │                                    │ train_model()      │    │
    │                                    └─────────┬──────────┘    │
    │                                              │               │
    │                                    ┌─────────▼──────────┐    │
    │                                    │ HuggingFace        │    │
    │                                    │ load_model()       │    │
    │                                    │ create_embeddings()│    │
    │                                    └─────────┬──────────┘    │
    │                                              │               │
    │                                    ┌─────────▼──────────┐    │
    │                                    │ Dynamic Pricing    │    │
    │                                    │ prepare_data()     │    │
    │                                    │ train_models()     │    │
    │                                    └─────────┬──────────┘    │
    │                                              │               │
    │                                              │ ✅ Done       │
    │                                              │ is_initialized│
    │                                              │ = True        │
    │                                              │               │
```

---

### Flow 2: Get User Recommendations

```
┌────────┐                                    ┌──────────┐         ┌─────────┐
│ Client │                                    │  Hybrid  │         │ MongoDB │
└───┬────┘                                    │  System  │         └────┬────┘
    │                                         └────┬─────┘              │
    │ GET /api/hybrid/user-recommendations        │                    │
    │     /676eaf5c?top_k=10                      │                    │
    ├────────────────────────────────────────────►│                    │
    │                                              │                    │
    │                                              │ Check initialized  │
    │                                              │ is_initialized?    │
    │                                              │                    │
    │                         ┌────────────────────┴─────────┐          │
    │                         │ If NOT initialized:          │          │
    │  400 Bad Request        │ Return error                 │          │
    │  {detail: "Not init"}   │                              │          │
    ◄─────────────────────────┴──────────────────────────────┘          │
    │                                              │                    │
    │                         ┌────────────────────▼─────────┐          │
    │                         │ If initialized:              │          │
    │                         │                              │          │
    │                         │ 1. TensorFlow Recommendations│          │
    │                         │    tf_recommender.get_recs() │          │
    │                         │    → 5 products              │          │
    │                         │                              │          │
    │                         │ 2. HuggingFace Content-based │          │
    │                         │    hf_filter.get_recs()      │          │
    │                         │    → 3 products              │          │
    │                         │                              │          │
    │                         │ 3. Gemini LLM Insights       │          │
    │                         │    gemini.analyze_user()     │          │
    │                         │    → 2 products              │          │
    │                         │                              │          │
    │                         │ 4. Merge & Rank              │          │
    │                         │    combine_scores()          │          │
    │                         │    deduplicate()             │          │
    │                         │    sort_by_score()           │          │
    │                         │    take top_k=10             │          │
    │                         └────────────┬─────────────────┘          │
    │                                      │                            │
    │  200 OK                              │                            │
    │  {recommendations: [...]}            │                            │
    ◄──────────────────────────────────────┘                            │
```

---

### Flow 3: Semantic Search

```
┌────────┐                                    ┌────────────┐
│ Client │                                    │ HuggingFace│
└───┬────┘                                    │   Filter   │
    │                                         └─────┬──────┘
    │ GET /api/huggingface/search-products         │
    │     ?query=bánh sinh nhật&top_k=5            │
    ├─────────────────────────────────────────────►│
    │                                               │
    │                             ┌─────────────────▼──────────┐
    │                             │ 1. Encode query            │
    │                             │    model.encode(           │
    │                             │      "bánh sinh nhật"      │
    │                             │    )                       │
    │                             │    → query_embedding       │
    │                             │                            │
    │                             │ 2. Compare with products   │
    │                             │    cosine_similarity(      │
    │                             │      query_embedding,      │
    │                             │      product_embeddings    │
    │                             │    )                       │
    │                             │                            │
    │                             │ 3. Rank by similarity      │
    │                             │    scores.argsort()        │
    │                             │    take top_k=5            │
    │                             └─────────────┬──────────────┘
    │                                           │
    │  200 OK                                   │
    │  {results: [                              │
    │    {product: "Bánh Tiramisu L",           │
    │     score: 0.88},                         │
    │    {product: "Bánh Mousse",               │
    │     score: 0.82},                         │
    │    ...                                    │
    │  ]}                                       │
    ◄───────────────────────────────────────────┘
```

---

### Flow 4: Price Optimization

```
┌────────┐                                    ┌──────────┐         ┌─────────┐
│ Client │                                    │ Dynamic  │         │ MongoDB │
└───┬────┘                                    │ Pricing  │         └────┬────┘
    │                                         └────┬─────┘              │
    │ GET /api/pricing/optimize/67643c24          │                    │
    │     ?target_date=2025-10-15                 │                    │
    ├────────────────────────────────────────────►│                    │
    │                                              │                    │
    │                                              │ Get product data   │
    │                                              ├───────────────────►│
    │                                              │                    │
    │                                              │ Product info       │
    │                                              ◄────────────────────┤
    │                                              │                    │
    │                             ┌────────────────▼─────────────┐      │
    │                             │ 1. Prepare features          │      │
    │                             │    - price: 250000           │      │
    │                             │    - weekday: 2 (Tuesday)    │      │
    │                             │    - is_weekend: False       │      │
    │                             │    - month: 10               │      │
    │                             │    - is_holiday: False       │      │
    │                             │    - product_rating: 4.8     │      │
    │                             │    - lag features            │      │
    │                             │    - moving averages         │      │
    │                             │                              │      │
    │                             │ 2. Test price range          │      │
    │                             │    prices = [200k - 300k]    │      │
    │                             │    step = 5k                 │      │
    │                             │                              │      │
    │                             │ 3. For each price:           │      │
    │                             │    demand = model.predict()  │      │
    │                             │    revenue = price * demand  │      │
    │                             │                              │      │
    │                             │ 4. Find optimal              │      │
    │                             │    max_revenue_price         │      │
    │                             │    = 230k                    │      │
    │                             │    predicted_demand = 45     │      │
    │                             │    revenue = 10.35M          │      │
    │                             └────────────┬─────────────────┘      │
    │                                          │                        │
    │  200 OK                                  │                        │
    │  {                                       │                        │
    │    current_price: 250000,                │                        │
    │    optimal_price: 230000,                │                        │
    │    price_change: -8%,                    │                        │
    │    predicted_revenue: 10350000,          │                        │
    │    recommendation: "Giảm giá nhẹ"        │                        │
    │  }                                       │                        │
    ◄──────────────────────────────────────────┘                        │
```

---

## 🎯 DATA FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                         MONGODB DATABASE                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Products │  │  Orders  │  │  Users   │  │ Ratings  │       │
│  │ (31)     │  │  (111)   │  │  (22)    │  │  (26)    │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │   MongoDB Data Access Layer     │
        │   • get_orders_data()           │
        │   • get_products_data()         │
        │   • get_users_data()            │
        │   • get_ratings_data()          │
        └──────────────┬──────────────────┘
                       │
        ┏━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━┓
        ▼                                         ▼
┌───────────────────┐                   ┌──────────────────┐
│ TensorFlow Model  │                   │ HuggingFace Model│
│ • prepare_data()  │                   │ • load_model()   │
│ • build_model()   │                   │ • encode()       │
│ • train_model()   │                   │ • similarity()   │
│ • get_recs()      │                   │ • search()       │
└────────┬──────────┘                   └────────┬─────────┘
         │                                       │
         └───────────────┬───────────────────────┘
                         ▼
             ┌───────────────────────┐
             │ Hybrid Recommender    │
             │ • Combine results     │
             │ • Rank & deduplicate  │
             │ • Filter by score     │
             └───────────┬───────────┘
                         │
                         ▼
             ┌───────────────────────┐
             │   API Response        │
             │   JSON format         │
             └───────────────────────┘
```

---

## 🔐 ERROR HANDLING FLOW

```
Request
  │
  ├─► Is server running?
  │   ├─ NO → 503 Service Unavailable
  │   └─ YES ▼
  │
  ├─► Is MongoDB connected?
  │   ├─ NO → 500 Internal Server Error
  │   └─ YES ▼
  │
  ├─► Is endpoint valid?
  │   ├─ NO → 404 Not Found
  │   └─ YES ▼
  │
  ├─► Are parameters valid?
  │   ├─ NO → 400 Bad Request
  │   └─ YES ▼
  │
  ├─► Is hybrid system initialized? (for ML endpoints)
  │   ├─ NO → 400 "Hybrid system not initialized"
  │   └─ YES ▼
  │
  ├─► Does resource exist?
  │   ├─ NO → 404 "Resource not found"
  │   └─ YES ▼
  │
  └─► Process request
      ├─ SUCCESS → 200 OK
      └─ ERROR → 500 Internal Server Error
```

---

## 📊 PERFORMANCE METRICS

```
┌──────────────────────────────────────────────────────────────┐
│                    Response Time Targets                     │
├────────────────────────┬─────────────┬──────────────────────┤
│ Endpoint Type          │ Target Time │ Optimization         │
├────────────────────────┼─────────────┼──────────────────────┤
│ Health Check           │ < 100ms     │ In-memory cache      │
│ Data Access            │ < 200ms     │ MongoDB indexes      │
│ Analytics              │ < 500ms     │ Redis cache (5min)   │
│ Search                 │ < 1s        │ Pre-computed vectors │
│ Recommendations        │ < 2s        │ Model warm-up        │
│ Initialize             │ 10-30s      │ Background job       │
│ Complete Strategy      │ 30-60s      │ Async processing     │
└────────────────────────┴─────────────┴──────────────────────┘
```

---

**Visual Guide Version:** 1.0  
**Last Updated:** 2025-10-11
