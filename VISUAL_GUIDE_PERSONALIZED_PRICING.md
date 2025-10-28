# 🎨 VISUAL GUIDE - Personalized Dynamic Pricing Architecture

## 🏗️ SYSTEM ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────┐
│                        FRONTEND / CLIENT                        │
│         (Web App, Mobile App, Admin Dashboard)                 │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             │ HTTP Request
                             │ GET /api/products/{id}/price?userId={userId}
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                        FASTAPI SERVER                          │
│                    (app/routers/*.py)                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  /api/personalized-pricing/calculate-price               │ │
│  │  /api/personalized-pricing/customer-segment              │ │
│  │  /api/personalized-pricing/simulate                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│              PERSONALIZED PRICING ENGINE                       │
│      (application/services/personalized_pricing.py)            │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  STEP 1: Get Customer Segment                          │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │  Customer Segmentation Service                 │    │  │
│  │  │  (infrastructure/ml_models/                    │    │  │
│  │  │   customer_segmentation.py)                    │    │  │
│  │  │                                                │    │  │
│  │  │  INPUT:  userId                                │    │  │
│  │  │  PROCESS:                                      │    │  │
│  │  │  ├─ Get user's order history                  │    │  │
│  │  │  ├─ Calculate RFM metrics                     │    │  │
│  │  │  │  ├─ Recency (days since last order)       │    │  │
│  │  │  │  ├─ Frequency (# of orders)               │    │  │
│  │  │  │  └─ Monetary (total spend)                │    │  │
│  │  │  ├─ Run K-Means clustering (n=4)             │    │  │
│  │  │  └─ Assign segment label                     │    │  │
│  │  │                                                │    │  │
│  │  │  OUTPUT: "VIP" | "REGULAR" | "OCCASIONAL" |  │    │  │
│  │  │          "NEW"                                 │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│                             │                                  │
│                             ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  STEP 2: Get Price Sensitivity                         │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │  Price Elasticity Calculator                   │    │  │
│  │  │  (infrastructure/ml_models/                    │    │  │
│  │  │   price_elasticity.py)                         │    │  │
│  │  │                                                │    │  │
│  │  │  INPUT:  productId                             │    │  │
│  │  │  PROCESS:                                      │    │  │
│  │  │  ├─ Get historical price & quantity data      │    │  │
│  │  │  ├─ Calculate % changes                       │    │  │
│  │  │  ├─ Run linear regression                     │    │  │
│  │  │  │  Elasticity = % Qty Change / % Price Change│    │  │
│  │  │  └─ Classify sensitivity                      │    │  │
│  │  │                                                │    │  │
│  │  │  OUTPUT: {                                     │    │  │
│  │  │    elasticity: -1.2,                           │    │  │
│  │  │    sensitivity: "SENSITIVE",                   │    │  │
│  │  │    can_increase: false,                        │    │  │
│  │  │    max_safe_increase: 5%                       │    │  │
│  │  │  }                                             │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│                             │                                  │
│                             ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  STEP 3: Apply Pricing Rules                          │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │  Pricing Rules Engine                          │    │  │
│  │  │                                                │    │  │
│  │  │  RULES BY SEGMENT:                             │    │  │
│  │  │  ┌─────────────────────────────────────────┐  │    │  │
│  │  │  │ VIP:                                    │  │    │  │
│  │  │  │  • Max increase: 0%                     │  │    │  │
│  │  │  │  • Discount: 5-15%                      │  │    │  │
│  │  │  │  • Strategy: Always best price          │  │    │  │
│  │  │  │  • Protection: MAXIMUM                  │  │    │  │
│  │  │  └─────────────────────────────────────────┘  │    │  │
│  │  │  ┌─────────────────────────────────────────┐  │    │  │
│  │  │  │ REGULAR:                                │  │    │  │
│  │  │  │  • Max increase: 5%                     │  │    │  │
│  │  │  │  • Discount: 3-10%                      │  │    │  │
│  │  │  │  • Strategy: Loyalty rewards            │  │    │  │
│  │  │  │  • Protection: HIGH                     │  │    │  │
│  │  │  └─────────────────────────────────────────┘  │    │  │
│  │  │  ┌─────────────────────────────────────────┐  │    │  │
│  │  │  │ OCCASIONAL:                             │  │    │  │
│  │  │  │  • Max increase: 10%                    │  │    │  │
│  │  │  │  • Discount: 0-5%                       │  │    │  │
│  │  │  │  • Strategy: Conversion focus           │  │    │  │
│  │  │  │  • Protection: MEDIUM                   │  │    │  │
│  │  │  └─────────────────────────────────────────┘  │    │  │
│  │  │  ┌─────────────────────────────────────────┐  │    │  │
│  │  │  │ NEW:                                    │  │    │  │
│  │  │  │  • Max increase: 15%                    │  │    │  │
│  │  │  │  • Discount: 10-20%                     │  │    │  │
│  │  │  │  • Strategy: Acquisition                │  │    │  │
│  │  │  │  • Protection: LOW                      │  │    │  │
│  │  │  └─────────────────────────────────────────┘  │    │  │
│  │  │                                                │    │  │
│  │  │  CALCULATION:                                  │    │  │
│  │  │  ├─ Start with base_price                     │    │  │
│  │  │  ├─ Check elasticity constraint               │    │  │
│  │  │  ├─ Apply segment-specific rules              │    │  │
│  │  │  ├─ Consider event context (optional)         │    │  │
│  │  │  └─ Calculate final personalized_price        │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────┘  │
│                             │                                  │
│                             ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  STEP 4: Generate Response                             │  │
│  │  {                                                      │  │
│  │    "user_id": "user_123",                              │  │
│  │    "product_id": "product_456",                        │  │
│  │    "segment": "VIP",                                   │  │
│  │    "base_price": 20000,                                │  │
│  │    "personalized_price": 18000,                        │  │
│  │    "discount_amount": 2000,                            │  │
│  │    "discount_percentage": 10,                          │  │
│  │    "pricing_strategy": "loyalty_premium_protection",   │  │
│  │    "explanation": "Giá ưu đãi dành riêng cho VIP",    │  │
│  │    "price_locked": true,                               │  │
│  │    "valid_until": "2025-10-27T23:59:59"               │  │
│  │  }                                                      │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                      MONGODB ATLAS                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   orders     │  │    users     │  │   products   │        │
│  │  collection  │  │  collection  │  │  collection  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ customer     │  │   pricing    │  │   vouchers   │        │
│  │  segments    │  │   history    │  │  collection  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔄 DATA FLOW - Real Example

### Example: Khách hàng A mua Bánh Su

```
┌─────────────────────────────────────────────────────────────┐
│  USER A visits product page: "Bánh Su Kem"                  │
│  Frontend sends request:                                     │
│  GET /api/personalized-pricing/calculate-price              │
│      ?productId=banh_su_001&userId=user_a_123               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Segment Customer                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Query MongoDB orders for user_a_123                   │ │
│  │  Found:                                                 │ │
│  │    • 20 orders total                                   │ │
│  │    • Last order: 5 days ago (Recency = 5)             │ │
│  │    • Total spent: 1,200,000đ (Monetary)               │ │
│  │    • Avg order value: 60,000đ                         │ │
│  │                                                         │ │
│  │  Calculate RFM:                                         │ │
│  │    R = 5  (excellent - bought recently)                │ │
│  │    F = 20 (excellent - frequent buyer)                 │ │
│  │    M = 1,200,000 (excellent - high value)              │ │
│  │                                                         │ │
│  │  K-Means Clustering:                                    │ │
│  │    → Assigned to Cluster 0                             │ │
│  │    → Mapped to Segment: "VIP"                          │ │
│  └────────────────────────────────────────────────────────┘ │
│  Result: segment = "VIP"                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Check Price Sensitivity                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Query historical data for product banh_su_001         │ │
│  │  Found 150 orders over last 3 months                   │ │
│  │                                                         │ │
│  │  Price history:                                         │ │
│  │    20,000đ → 21,000đ (+5%)                             │ │
│  │      → Quantity: 100 → 85 (-15%)                       │ │
│  │                                                         │ │
│  │  Calculate elasticity:                                  │ │
│  │    E = -15% / 5% = -3.0                                │ │
│  │                                                         │ │
│  │  Classification:                                        │ │
│  │    E = -3.0 → "VERY_SENSITIVE"                         │ │
│  │                                                         │ │
│  │  Recommendation:                                        │ │
│  │    • DO NOT increase price                             │ │
│  │    • Max safe increase: 0%                             │ │
│  │    • Consider discounts instead                        │ │
│  └────────────────────────────────────────────────────────┘ │
│  Result: sensitivity = "VERY_SENSITIVE"                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Apply Pricing Rules                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Input:                                                 │ │
│  │    • segment = "VIP"                                   │ │
│  │    • sensitivity = "VERY_SENSITIVE"                    │ │
│  │    • base_price = 20,000đ                              │ │
│  │                                                         │ │
│  │  VIP Pricing Rules:                                     │ │
│  │    • Max increase: 0%  ✓ (respects elasticity)        │ │
│  │    • Discount range: 5-15%                             │ │
│  │    • Protection: MAXIMUM                               │ │
│  │                                                         │ │
│  │  Decision Logic:                                        │ │
│  │    IF segment == "VIP" AND sensitivity == "SENSITIVE"  │ │
│  │       THEN give generous discount                      │ │
│  │                                                         │ │
│  │  Calculate discount:                                    │ │
│  │    • Random in range [5%, 15%]                         │ │
│  │    • Selected: 10%                                     │ │
│  │    • Discount amount: 20,000 * 0.10 = 2,000đ          │ │
│  │                                                         │ │
│  │  Final price:                                           │ │
│  │    20,000 - 2,000 = 18,000đ                            │ │
│  └────────────────────────────────────────────────────────┘ │
│  Result: personalized_price = 18,000đ                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Generate Response                                   │
│  {                                                           │
│    "user_id": "user_a_123",                                 │
│    "product_id": "banh_su_001",                             │
│    "product_name": "Bánh Su Kem",                           │
│    "segment": "VIP",                                        │
│    "base_price": 20000,                                     │
│    "personalized_price": 18000,                             │
│    "discount_amount": 2000,                                 │
│    "discount_percentage": 10.0,                             │
│    "pricing_strategy": "loyalty_premium_protection",        │
│    "explanation": "🌟 Giá ưu đãi đặc biệt dành cho khách   │
│                    hàng VIP. Giảm 10% - Cảm ơn sự ủng hộ   │
│                    của bạn!",                               │
│    "elasticity": -3.0,                                      │
│    "sensitivity": "VERY_SENSITIVE",                         │
│    "price_locked": true,                                    │
│    "valid_until": "2025-10-28T23:59:59Z",                  │
│    "timestamp": "2025-10-27T10:30:00Z"                     │
│  }                                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND DISPLAYS                                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  🍰 Bánh Su Kem                                        │ │
│  │                                                         │ │
│  │  ̶2̶0̶,̶0̶0̶0̶đ̶   →   18,000đ   (-10%)                    │ │
│  │                                                         │ │
│  │  🌟 Giá VIP đặc biệt dành cho bạn!                    │ │
│  │  💝 Cảm ơn sự ủng hộ của khách hàng thân thiết        │ │
│  │                                                         │ │
│  │  [  Thêm vào giỏ hàng  ]                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Meanwhile, for an OCCASIONAL customer (User B):

```
User B (OCCASIONAL segment):
  • 3 orders total
  • Last order: 45 days ago
  • Total spent: 200,000đ

Same product (Bánh Su Kem):
  • Base price: 20,000đ
  • Elasticity: -3.0 (VERY_SENSITIVE)
  • BUT segment = "OCCASIONAL"

Pricing Decision:
  • OCCASIONAL rules: can increase up to 10%
  • BUT elasticity is VERY_SENSITIVE
  • Compromise: Keep base price (no increase)
  • Give small discount: 2% = 400đ

Final price for User B: 19,600đ

Result:
  ✅ User A (VIP): 18,000đ (10% off)
  ✅ User B (Occasional): 19,600đ (2% off)
  ✅ Both get discounts (respecting elasticity)
  ✅ VIP gets BETTER price (loyalty reward)
  ✅ Revenue optimized across segments
```

---

## 📊 DECISION TREE - Pricing Logic

```
Start: Calculate Personalized Price
│
├─ Get Customer Segment
│  │
│  ├─ VIP?
│  │  └─ YES → Max increase = 0%, Discount = 5-15%
│  │          └─ ALWAYS give best price
│  │          └─ Priority: PROTECT AT ALL COST
│  │
│  ├─ REGULAR?
│  │  └─ YES → Max increase = 5%, Discount = 3-10%
│  │          └─ Check elasticity
│  │          │  ├─ Sensitive? → Give discount
│  │          │  └─ Not sensitive? → Small increase OK
│  │
│  ├─ OCCASIONAL?
│  │  └─ YES → Max increase = 10%, Discount = 0-5%
│  │          └─ Check elasticity
│  │          │  ├─ Insensitive? → Can increase
│  │          │  └─ Sensitive? → Keep base or small discount
│  │
│  └─ NEW?
│     └─ YES → Max increase = 15%, Discount = 10-20%
│             └─ Aggressive discount to acquire
│
├─ Get Product Elasticity
│  │
│  ├─ Calculate from historical data
│  │  └─ E = % Qty Change / % Price Change
│  │
│  └─ Classify Sensitivity
│     ├─ E < -1.5  → VERY_SENSITIVE (don't increase)
│     ├─ E < -1.0  → SENSITIVE (careful)
│     ├─ E < -0.5  → MODERATE (can increase slightly)
│     └─ E >= -0.5 → INSENSITIVE (can increase freely)
│
├─ Apply Constraints
│  │
│  ├─ Check: segment.max_increase vs elasticity.max_safe_increase
│  └─ Use: MIN(segment.max, elasticity.max)
│
├─ Consider Event Context (optional)
│  │
│  ├─ Valentine's Day?
│  │  └─ Apply event-specific discounts
│  │
│  ├─ Christmas?
│  │  └─ Apply holiday pricing
│  │
│  └─ Regular day?
│     └─ Use standard rules
│
└─ Calculate Final Price
   │
   ├─ Start with base_price
   ├─ Apply increase/decrease based on rules
   ├─ Ensure: personalized_price >= cost_price + margin
   └─ Generate explanation message
```

---

## 🎯 SEGMENT CHARACTERISTICS - Visual Breakdown

```
┌─────────────────────────────────────────────────────────────┐
│                    CUSTOMER SEGMENTS                         │
└─────────────────────────────────────────────────────────────┘

🌟 VIP SEGMENT (10-20% of customers, 60-80% of revenue)
┌─────────────────────────────────────────────────────────────┐
│  Characteristics:                                            │
│  • High Frequency (≥10 orders)                              │
│  • High Monetary (≥500,000đ)                                │
│  • Low Recency (recent purchases)                           │
│  • Avg Order Value: High                                    │
│                                                              │
│  Pricing Strategy:                                           │
│  • 🔒 NEVER increase prices                                 │
│  • 💰 Always offer 5-15% discount                          │
│  • 🎁 Exclusive early access to new products               │
│  • 💝 Special birthday/anniversary offers                  │
│  • 🚚 Free shipping always                                 │
│                                                              │
│  Why Protect?                                                │
│  • They are your most valuable customers                    │
│  • High lifetime value (CLV)                                │
│  • Brand advocates (word of mouth)                          │
│  • Expensive to replace                                     │
│                                                              │
│  Example Messaging:                                          │
│  "🌟 Giá VIP đặc biệt - Cảm ơn sự ủng hộ của bạn!"        │
└─────────────────────────────────────────────────────────────┘

💝 REGULAR SEGMENT (30-40% of customers, 20-30% of revenue)
┌─────────────────────────────────────────────────────────────┐
│  Characteristics:                                            │
│  • Medium Frequency (5-9 orders)                            │
│  • Medium Monetary (200,000-500,000đ)                       │
│  • Low Recency (bought within 60 days)                     │
│  • Potential to become VIP                                  │
│                                                              │
│  Pricing Strategy:                                           │
│  • ✅ Small increases OK (max 5%)                          │
│  • 💰 Loyalty discounts 3-10%                              │
│  • 🎯 Targeted offers to increase frequency                │
│  • 📧 Personalized recommendations                         │
│                                                              │
│  Why Important?                                              │
│  • Pipeline to VIP status                                   │
│  • Stable revenue base                                      │
│  • Worth investing in retention                             │
│                                                              │
│  Example Messaging:                                          │
│  "💝 Ưu đãi khách quen - Giá tốt nhất dành cho bạn!"      │
└─────────────────────────────────────────────────────────────┘

🎯 OCCASIONAL SEGMENT (30-40% of customers, 10-15% of revenue)
┌─────────────────────────────────────────────────────────────┐
│  Characteristics:                                            │
│  • Low Frequency (2-4 orders)                               │
│  • Low Monetary (<200,000đ)                                 │
│  • Medium/High Recency (bought 60-180 days ago)            │
│  • Price sensitive                                          │
│                                                              │
│  Pricing Strategy:                                           │
│  • ✅ Can increase prices (max 10%)                        │
│  • 💰 Targeted promotions to convert                       │
│  • 📧 Re-engagement campaigns                              │
│  • 🎁 Special offers to increase frequency                 │
│                                                              │
│  Why Convert?                                                │
│  • Potential to move up                                     │
│  • Respond well to promotions                               │
│  • Can fill demand gaps                                     │
│                                                              │
│  Example Messaging:                                          │
│  "🎁 Ưu đãi đặc biệt hôm nay - Đừng bỏ lỡ!"              │
└─────────────────────────────────────────────────────────────┘

🎁 NEW SEGMENT (10-20% of customers, 5-10% of revenue)
┌─────────────────────────────────────────────────────────────┐
│  Characteristics:                                            │
│  • First order or very few orders (1-2)                     │
│  • Unknown loyalty                                          │
│  • Trial phase                                              │
│  • High churn risk                                          │
│                                                              │
│  Pricing Strategy:                                           │
│  • 💰 Aggressive acquisition discounts (10-20%)            │
│  • 🎁 First order special offers                           │
│  • 🚚 Free shipping on first order                         │
│  • 📧 Welcome series campaigns                             │
│                                                              │
│  Why Invest?                                                 │
│  • Potential future VIPs                                    │
│  • Growing customer base                                    │
│  • Competitive acquisition                                  │
│                                                              │
│  Example Messaging:                                          │
│  "🎉 Chào mừng! Giảm 15% đơn hàng đầu tiên"               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 SIMULATION FLOW

```
┌─────────────────────────────────────────────────────────────┐
│  BEFORE APPLYING NEW PRICING: RUN SIMULATION                │
└─────────────────────────────────────────────────────────────┘

Input:
  • Product: Bánh Su Kem
  • Current Price: 20,000đ
  • Proposed Price: 25,000đ (+25%)

Step 1: Get Product Data
┌─────────────────────────────────────────────────────────────┐
│  Historical Performance:                                     │
│  • Average units sold: 100 per week                         │
│  • Current revenue: 2,000,000đ per week                     │
│  • Customers buying this: 50                                │
│  • Price elasticity: -1.2                                   │
└─────────────────────────────────────────────────────────────┘

Step 2: Predict Demand Change
┌─────────────────────────────────────────────────────────────┐
│  Using Price Elasticity:                                     │
│  • Price change: +25%                                       │
│  • Elasticity: -1.2                                         │
│  • Demand change: -1.2 × 25% = -30%                        │
│  • Predicted units: 100 × 0.70 = 70 units                  │
└─────────────────────────────────────────────────────────────┘

Step 3: Calculate Revenue Impact
┌─────────────────────────────────────────────────────────────┐
│  New Revenue:                                                │
│  • Units: 70                                                │
│  • Price: 25,000đ                                           │
│  • Revenue: 70 × 25,000 = 1,750,000đ                       │
│  • Change: -250,000đ (-12.5%)                               │
│                                                              │
│  ⚠️ WARNING: Revenue DECREASED!                            │
└─────────────────────────────────────────────────────────────┘

Step 4: Analyze Customer Impact
┌─────────────────────────────────────────────────────────────┐
│  Customers Affected:                                         │
│  • VIP: 10 customers (20%)                                  │
│  • REGULAR: 20 customers (40%)                              │
│  • OCCASIONAL: 15 customers (30%)                           │
│  • NEW: 5 customers (10%)                                   │
│                                                              │
│  ⚠️ RISK: 10 VIP customers see 25% increase!               │
│            May lose loyal customers!                         │
└─────────────────────────────────────────────────────────────┘

Step 5: Risk Assessment
┌─────────────────────────────────────────────────────────────┐
│  Risk Factors:                                               │
│  • ❌ Revenue decrease: -12.5%                             │
│  • ❌ High VIP impact: 10 customers                        │
│  • ❌ Elastic product: E = -1.2                            │
│  • ❌ Large price increase: +25%                           │
│                                                              │
│  RISK LEVEL: 🔴 HIGH                                        │
│                                                              │
│  Recommendation:                                             │
│  ⛔ DO NOT PROCEED with this pricing change!               │
│                                                              │
│  Alternative Strategies:                                     │
│  1. Keep price at 20,000đ                                  │
│  2. Increase to 22,000đ (+10%) instead                     │
│  3. Give VIPs voucher to offset increase                    │
│  4. Test with A/B test first                                │
└─────────────────────────────────────────────────────────────┘

Step 6: Run Alternative Simulation
┌─────────────────────────────────────────────────────────────┐
│  ALTERNATIVE: Personalized Pricing                           │
│                                                              │
│  Instead of blanket 25,000đ for everyone:                  │
│                                                              │
│  VIP (10 customers):                                         │
│    • Price: 18,000đ (-10%)                                 │
│    • Units: Same (10 × 5 = 50)                             │
│    • Revenue: 50 × 18,000 = 900,000đ                       │
│                                                              │
│  REGULAR (20 customers):                                     │
│    • Price: 19,000đ (-5%)                                  │
│    • Units: Same (20 × 2 = 40)                             │
│    • Revenue: 40 × 19,000 = 760,000đ                       │
│                                                              │
│  OCCASIONAL (15 customers):                                  │
│    • Price: 23,000đ (+15%)                                 │
│    • Units: Decrease (15 × 1 × 0.82 = 12)                 │
│    • Revenue: 12 × 23,000 = 276,000đ                       │
│                                                              │
│  NEW (5 customers):                                          │
│    • Price: 17,000đ (-15% acquisition)                     │
│    • Units: Increase (5 × 1 × 1.18 = 6)                   │
│    • Revenue: 6 × 17,000 = 102,000đ                        │
│                                                              │
│  TOTAL REVENUE: 2,038,000đ                                  │
│  vs CURRENT: 2,000,000đ                                     │
│  CHANGE: +38,000đ (+1.9%)                                   │
│                                                              │
│  BENEFITS:                                                   │
│  ✅ Revenue increase (not decrease!)                        │
│  ✅ VIP customers protected                                 │
│  ✅ Customer satisfaction maintained                         │
│  ✅ Balanced approach                                        │
│                                                              │
│  RISK LEVEL: 🟢 LOW                                         │
│                                                              │
│  Recommendation:                                             │
│  ✅ PROCEED with personalized pricing!                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 UI/UX EXAMPLES

### Frontend Display - Different Segments See Different Prices

```
┌─────────────────────────────────────────────────────────────┐
│  VIP CUSTOMER VIEW                                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  🍰 Bánh Su Kem                        [❤️ Yêu thích]  │ │
│  │                                                         │ │
│  │  [   Image of Bánh Su   ]                              │ │
│  │                                                         │ │
│  │  ̶2̶0̶,̶0̶0̶0̶đ̶                                              │ │
│  │  18,000đ                             🌟 Giá VIP        │ │
│  │  Tiết kiệm: 2,000đ (-10%)                              │ │
│  │                                                         │ │
│  │  💝 Giá đặc biệt dành cho khách VIP                   │ │
│  │  🎁 Miễn phí giao hàng                                 │ │
│  │  ⭐ Tích điểm x2                                       │ │
│  │                                                         │ │
│  │  [ Thêm vào giỏ hàng ]  [ Mua ngay ]                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  REGULAR CUSTOMER VIEW                                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  🍰 Bánh Su Kem                        [🤍 Thích]      │ │
│  │                                                         │ │
│  │  [   Image of Bánh Su   ]                              │ │
│  │                                                         │ │
│  │  ̶2̶0̶,̶0̶0̶0̶đ̶                                              │ │
│  │  19,000đ                             💝 Ưu đãi         │ │
│  │  Tiết kiệm: 1,000đ (-5%)                               │ │
│  │                                                         │ │
│  │  💝 Giá ưu đãi cho khách quen                          │ │
│  │  🚚 Miễn phí ship cho đơn >100k                       │ │
│  │  ⭐ Tích điểm x1.5                                     │ │
│  │                                                         │ │
│  │  [ Thêm vào giỏ hàng ]  [ Mua ngay ]                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  OCCASIONAL CUSTOMER VIEW                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  🍰 Bánh Su Kem                        [🤍 Thích]      │ │
│  │                                                         │ │
│  │  [   Image of Bánh Su   ]                              │ │
│  │                                                         │ │
│  │  20,000đ                              💰 Giá tốt       │ │
│  │                                                         │ │
│  │  🎁 Giảm thêm 10% khi mua 2 hộp                       │ │
│  │  🚚 Miễn phí ship cho đơn >200k                       │ │
│  │  ⭐ Tích điểm x1                                       │ │
│  │                                                         │ │
│  │  [ Thêm vào giỏ hàng ]  [ Mua ngay ]                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  NEW CUSTOMER VIEW                                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  🍰 Bánh Su Kem                        [🤍 Thích]      │ │
│  │                                                         │ │
│  │  [   Image of Bánh Su   ]                              │ │
│  │                                                         │ │
│  │  ̶2̶0̶,̶0̶0̶0̶đ̶                                              │ │
│  │  17,000đ                             🎉 Chào mừng      │ │
│  │  Tiết kiệm: 3,000đ (-15%)                              │ │
│  │                                                         │ │
│  │  🎉 Ưu đãi chào mừng khách hàng mới!                  │ │
│  │  🎁 Tặng voucher 20k cho đơn tiếp theo                │ │
│  │  🚚 Miễn phí ship đơn đầu tiên                        │ │
│  │                                                         │ │
│  │  [ Thêm vào giỏ hàng ]  [ Mua ngay ]                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 KEY TAKEAWAYS

### 1. Segmentation is Foundation

```
MUST identify customer segments BEFORE pricing
→ VIP, REGULAR, OCCASIONAL, NEW
→ Based on RFM (Recency, Frequency, Monetary)
→ Use K-Means clustering (proven method)
```

### 2. Elasticity Prevents Disasters

```
MUST know product price sensitivity
→ VERY_SENSITIVE products: Don't increase
→ MODERATE products: Small increases OK
→ INSENSITIVE products: Can increase freely
```

### 3. Protection Rules are Critical

```
NEVER show VIP customers price increases
→ They are 20% of customers, 80% of revenue
→ Cost 5x-10x more to acquire new customers
→ Protect them AT ALL COST
```

### 4. Simulation Saves Money

```
ALWAYS simulate before deploying
→ Predict revenue impact
→ Assess customer churn risk
→ Test alternatives
→ Make data-driven decisions
```

### 5. Communication Matters

```
Don't just change prices silently
→ Explain the value
→ Show appreciation
→ Personalize messages
→ Build trust
```

---

**This visual guide complements the technical documents.**

For implementation details, see:

- [CUSTOMER_LOYALTY_PRICING_STRATEGY.md](./CUSTOMER_LOYALTY_PRICING_STRATEGY.md)
- [IMPLEMENTATION_PLAN_PERSONALIZED_PRICING.md](./IMPLEMENTATION_PLAN_PERSONALIZED_PRICING.md)
- [EXECUTIVE_SUMMARY_PERSONALIZED_PRICING.md](./EXECUTIVE_SUMMARY_PERSONALIZED_PRICING.md)

🚀 **Ready to implement? Start with the Implementation Plan!**
