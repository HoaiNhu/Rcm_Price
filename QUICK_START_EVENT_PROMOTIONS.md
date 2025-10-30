# 🚀 QUICK START GUIDE - RCM_PRICE Event Promotion System

## ⚡ 30-Second Setup

```bash
# 1. Start server
cd c:\Users\Lenovo\STUDY\RCM_PRICE
uvicorn app.main:app --reload --port 8000

# 2. Open browser
http://localhost:8000/docs
```

**That's it!** 🎉

---

## 📌 Most Useful Endpoints

### 1. Find Product Combos (High ROI 💰)

```bash
GET http://localhost:8000/api/event-promotions/discover-combos
```

**Expected Output:**

```
Top Combo: Bánh Sắc Hoa + Bánh hoa xuân
- Confidence: 100%
- Save: 102,000 VND
- Recommended: Implement combo deal NOW
```

**Why Use This:** Instant revenue boost from existing sales patterns

---

### 2. Check Upcoming Events (Plan Ahead 📅)

```bash
GET http://localhost:8000/api/event-promotions/upcoming-events?days_ahead=60
```

**Expected Output:**

```
Next Event: Weekend (in 3 days)
- Discount: 5-15%
- Categories: All

Christmas (in 56 days)
- Discount: 15-30%
- Categories: Bánh Kem, Bánh Ngọt
```

**Why Use This:** Never miss promotional opportunities

---

### 3. Auto-Generate Smart Promotion (AI-Powered 🤖)

```bash
POST http://localhost:8000/api/event-promotions/generate-smart-promotion?focus=balanced
```

**Expected Output:**

```json
{
  "promotion_name": "Khuyến Mãi Thông Minh - Balanced",
  "discount_value": 12.0,
  "target_products": 5,
  "expected_revenue_impact": -3.0,
  "estimated_order_increase": 10,
  "risk_level": "LOW",
  "start_date": "2025-10-29",
  "end_date": "2025-11-05"
}
```

**Why Use This:** Automated promotion strategy in 1 API call

---

## 🎯 Common Use Cases

### Use Case 1: "Need to clear slow-selling products"

```bash
POST http://localhost:8000/api/event-promotions/generate-smart-promotion?focus=clearance
```

**Result:** 20% discount on all slow movers, expected +44 orders

---

### Use Case 2: "Want to boost revenue this weekend"

```bash
POST http://localhost:8000/api/event-promotions/generate-event-promotion?event_type=Cuối Tuần
```

**Result:** Weekend promotion with optimal timing and products

---

### Use Case 3: "Need Christmas promotion ideas"

```bash
POST http://localhost:8000/api/event-promotions/generate-event-promotion?event_type=Giáng Sinh
```

**Result:** Complete Christmas campaign with 22.5% discount, +11.2% revenue impact

---

## 📊 Quick Performance Check

### Test Full System

```bash
cd c:\Users\Lenovo\STUDY\RCM_PRICE
python test_event_promotion_system.py
```

**Expected:** All tests pass in ~5 seconds

---

## 🐛 Quick Troubleshooting

### Problem: "NaN value" warnings

**Solution:** Expected behavior, 10 products have missing data but system handles gracefully

### Problem: "All products are slow movers"

**Solution:** Normal for bakery shop, focus on clearance + combo strategies

### Problem: "API not responding"

**Check:**

```bash
# MongoDB connection
python -c "from infrastructure.db.mongodb_access import MongoDBAccess; db = MongoDBAccess(); print('OK')"

# Server running
curl http://localhost:8000/api/event-promotions/health
```

---

## 📈 Recommended Workflow

```
1. Check upcoming events
   ↓
2. Analyze product performance
   ↓
3. Discover combos
   ↓
4. Generate smart promotion
   ↓
5. Review & approve
   ↓
6. Launch campaign
   ↓
7. Track results
```

---

## 🔥 Hot Tips

1. **Best time to check:** Every Monday morning (plan for week ahead)
2. **Most profitable:** Combo deals (100% confidence = guaranteed)
3. **Safest strategy:** Clearance (low risk, high volume)
4. **Highest revenue:** Event-based (Christmas, Tết)
5. **Quick win:** Weekend promotions (3-day campaigns)

---

## 🎓 Learning Resources

- **Full API Docs:** http://localhost:8000/docs
- **Event System Docs:** `EVENT_PROMOTION_SYSTEM_README.md`
- **Complete Overview:** `RCM_PRICE_COMPLETE_SUMMARY.md`
- **Test Examples:** `test_event_promotion_system.py`

---

## 📞 Need Help?

1. Check logs: Look for emoji symbols (✅ ❌ ⚠️)
2. Run health check: `GET /api/event-promotions/health`
3. Test connection: `python test_event_promotion_system.py`

---

**Last Updated:** 2025-10-29  
**Version:** 2.0.0  
**Status:** ✅ Production Ready

🚀 **Start using the system NOW!**
