import pytest
from mcp_server.tools.flight_calculator import calculate_flight_time
from mcp_server.tools.roi_calculator import calculate_roi
from mcp_server.tools.compliance_checker import check_compliance
from mcp_server.tools.drone_recommender import recommend_drone

def test_flight_time_calculator():
    res = calculate_flight_time(battery_mah=10000, empty_weight=3.0, payload=2.0, wind=10.0, temperature=28.0)
    assert "flight_time_mins" in res
    assert res["flight_time_mins"] > 0
    assert "max_range_km" in res
    assert len(res["power_curve"]) == 12

def test_roi_calculator():
    res = calculate_roi(sector="Agriculture", investment=750000, monthly_opex=25000, fee_per_acre=400, monthly_acres=500, subsidy_pct=50)
    assert res["monthly_revenue"] == 200000
    assert res["net_monthly_profit"] == 175000
    assert res["payback_months"] > 0
    assert len(res["projection"]) == 3

def test_compliance_checker_green_zone():
    res = check_compliance(weight_category="Micro", purpose="Commercial", zone="Green", altitude=200, rpc=True)
    assert res["status"] == "APPROVED"
    assert "Green Zone" in res["zone"]

def test_compliance_checker_red_zone():
    res = check_compliance(weight_category="Micro", purpose="Commercial", zone="Red", altitude=200, rpc=True)
    assert res["status"] == "PROHIBITED"
    assert "Rule 24" in res["penalties"]

def test_drone_recommender():
    recs = recommend_drone(budget_lakhs=10.0, sector="Agriculture", min_flight_time=15, min_payload=8)
    assert isinstance(recs, list)
    assert len(recs) > 0
    assert recs[0]["match_score"] > 0
