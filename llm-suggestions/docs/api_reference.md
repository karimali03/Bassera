# Baseera LLM Suggestions Service — API Reference

Base URL: `http://localhost:8000` (dev) / `https://your-deployed-url` (prod)

All endpoints use JSON. Protected endpoints require `Authorization: Bearer <SERVICE_API_KEY>`.

---

## GET /v1/health

Liveness check. No auth required.

**Response 200**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "development"
}
```

---

## POST /v1/suggestions

Generate AI-powered saving suggestions from a list of bank transactions.

**Headers**
```
Content-Type: application/json
Authorization: Bearer <SERVICE_API_KEY>
```

**Request body**
```json
{
  "transactions": [
    {
      "transaction_id": "ebf90783-868a-4980-97d3-9893231589b8",
      "timestamp": "2025-01-01 06:08",
      "merchant": "Orange Egypt",
      "category": "Services_and_Utilities",
      "amount": 676.10,
      "currency": "EGP",
      "type": "DEBIT",
      "note": "Subscription — twice_monthly"
    }
  ]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `transactions` | array | ✅ | 1–500 items. At least one DEBIT required. |
| `transaction_id` | string | ✅ | Unique identifier |
| `timestamp` | string | ✅ | `YYYY-MM-DD HH:mm` or ISO 8601 |
| `merchant` | string | ✅ | — |
| `category` | string | ✅ | Pre-tagged by bank API |
| `amount` | float | ✅ | Must be > 0 |
| `currency` | string | ✅ | ISO 4217 (e.g. `EGP`) |
| `type` | string | ✅ | `DEBIT` or `CREDIT` |
| `note` | string | ❌ | Optional context |

**Response 200**
```json
{
  "analysis_period": {
    "from": "2025-01-01",
    "to": "2025-01-08",
    "total_debits": 2469.23,
    "total_credits": 15000.00,
    "net_cashflow": 12530.77,
    "currency": "EGP"
  },
  "spending_breakdown": [
    {
      "category": "Services_and_Utilities",
      "total": 676.10,
      "percentage_of_debits": 27.38,
      "transaction_count": 1
    }
  ],
  "suggestions": [
    {
      "id": "sug_001",
      "priority": "HIGH",
      "type": "CONSOLIDATE",
      "title": "Merge your streaming subscriptions",
      "body": "You're paying EGP 299 across Netflix and Shahid separately. Picking one and sharing a family plan could save you EGP 150–200 per month without losing much content.",
      "estimated_monthly_saving_egp": 175.0,
      "affected_categories": ["Entertainment"],
      "action_label": "Compare streaming plans"
    }
  ],
  "savings_potential": {
    "conservative_egp": 350.0,
    "moderate_egp": 650.0,
    "summary": "Modest adjustments to subscriptions and food delivery could free up EGP 350–650 monthly."
  },
  "insight_of_the_day": {
    "text": "Your salary comfortably exceeds your spending — you're in a strong position to start building a savings habit.",
    "icon_hint": "trend_up"
  }
}
```

**Error responses**

| Status | Reason |
|---|---|
| 401 | Invalid API key |
| 403 | Missing Authorization header |
| 422 | Invalid request body (see `detail` field) |
| 502 | AI engine unavailable or returned bad output |
