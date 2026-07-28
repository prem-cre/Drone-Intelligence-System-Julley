import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_endpoint():
    response = client.post("/api/chat", json={"message": "What are DGCA rules for micro drones?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data

def test_calculate_flight_time_endpoint():
    response = client.post("/api/calculate/flight-time", json={
        "battery_mah": 10000, "empty_weight": 3.0, "payload": 2.0, "wind": 10.0, "temperature": 28.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["flight_time_mins"] > 0

def test_calculate_roi_endpoint():
    response = client.post("/api/calculate/roi", json={
        "sector": "Agriculture", "investment": 750000, "monthly_opex": 25000,
        "fee_per_acre": 400, "monthly_acres": 500, "subsidy_pct": 50
    })
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_revenue"] == 200000

def test_check_compliance_endpoint():
    response = client.post("/api/check/compliance", json={
        "weight_category": "Small", "purpose": "Commercial", "zone": "Green", "altitude": 200, "rpc": True
    })
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"

def test_recommend_drone_endpoint():
    response = client.post("/api/recommend/drone", json={
        "budget_lakhs": 10.0, "sector": "Agriculture", "min_flight_time": 15, "min_payload": 8
    })
    assert response.status_code == 200
    assert isinstance(response.json(), list)
