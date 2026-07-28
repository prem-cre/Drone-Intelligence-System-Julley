"""Quick smoke test for all 5 FastAPI endpoints the frontend calls."""
import json
import urllib.request

BASE = "http://localhost:8000"

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

print("=" * 60)
print("1. POST /api/chat")
r = post("/api/chat", {"message": "What are DGCA rules for micro drones in green zones?"})
print(f"   answer length: {len(r['answer'])} chars")
print(f"   citations: {len(r['citations'])}")
print(f"   tool_calls: {len(r['tool_calls'])}")
print(f"   PASS")

print("=" * 60)
print("2. POST /api/calculate/flight-time")
r = post("/api/calculate/flight-time", {
    "battery_mah": 10000, "empty_weight": 3, "payload": 2, "wind": 10, "temperature": 28
})
print(f"   flight_time_mins: {r['flight_time_mins']}")
print(f"   max_range_km: {r['max_range_km']}")
print(f"   power_curve points: {len(r['power_curve'])}")
print(f"   PASS")

print("=" * 60)
print("3. POST /api/calculate/roi")
r = post("/api/calculate/roi", {
    "sector": "Agriculture", "investment": 750000, "monthly_opex": 25000,
    "fee_per_acre": 400, "monthly_acres": 500, "subsidy_pct": 50
})
print(f"   monthly_revenue: {r['monthly_revenue']}")
print(f"   payback_months: {r['payback_months']}")
print(f"   projection years: {len(r['projection'])}")
print(f"   PASS")

print("=" * 60)
print("4. POST /api/check/compliance")
r = post("/api/check/compliance", {
    "weight_category": "Small", "purpose": "Commercial", "zone": "Yellow",
    "altitude": 200, "rpc": False
})
print(f"   status: {r['status']}")
print(f"   zone: {r['zone']}")
print(f"   permits: {len(r['permits'])}")
print(f"   workflow steps: {len(r['workflow'])}")
print(f"   PASS")

print("=" * 60)
print("5. POST /api/recommend/drone")
r = post("/api/recommend/drone", {
    "budget_lakhs": 8, "sector": "Agriculture", "min_flight_time": 15, "min_payload": 8
})
print(f"   drones matched: {len(r)}")
for d in r:
    print(f"   - {d['model_name']} (score: {d['match_score']}, Rs {d['price_lakhs']}L)")
print(f"   PASS")

print("=" * 60)
print("ALL 5 ENDPOINTS PASS -- Frontend <-> Backend connection is ready!")
