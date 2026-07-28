# API Documentation — Drone Intelligence System for India

## Endpoints

### 1. POST `/api/chat`
Routes user messages to RAG knowledge retrieval or MCP tools.

**Request**:
```json
{
  "message": "What are DGCA rules for micro drones in green zones?"
}
```

**Response**:
```json
{
  "answer": "Markdown answer text...",
  "citations": [
    {
      "title": "DGCA Category Micro Rules",
      "source": "rules_regulations.json",
      "score": 0.96,
      "snippet": "Micro category..."
    }
  ],
  "tool_calls": []
}
```

---

### 2. POST `/api/calculate/flight-time`
**Request**:
```json
{
  "battery_mah": 10000,
  "empty_weight": 3.0,
  "payload": 2.0,
  "wind": 10.0,
  "temperature": 28.0
}
```

---

### 3. POST `/api/calculate/roi`
**Request**:
```json
{
  "sector": "Agriculture",
  "investment": 750000,
  "monthly_opex": 25000,
  "fee_per_acre": 400,
  "monthly_acres": 500,
  "subsidy_pct": 50
}
```

---

### 4. POST `/api/check/compliance`
**Request**:
```json
{
  "weight_category": "Small",
  "purpose": "Commercial",
  "zone": "Green",
  "altitude": 200,
  "rpc": true
}
```

---

### 5. POST `/api/recommend/drone`
**Request**:
```json
{
  "budget_lakhs": 10.0,
  "sector": "Agriculture",
  "min_flight_time": 15,
  "min_payload": 8
}
```
