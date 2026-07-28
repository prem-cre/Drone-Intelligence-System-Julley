from typing import Dict, Any, List

DRONES_CATALOGUE: List[Dict[str, Any]] = [
    {
        "model_name": "Agribot MX",
        "manufacturer": "IoTechWorld Avigation",
        "price_lakhs": 7.5,
        "flight_time": 22,
        "payload": 10,
        "sector": "Agriculture",
        "pros": ["DGCA Type-Certified", "10L tank", "Namo Drone Didi eligible"],
        "cons": ["Heavy transport", "Requires RPC pilot"]
    },
    {
        "model_name": "AG365",
        "manufacturer": "Marut Drones",
        "price_lakhs": 9.2,
        "flight_time": 25,
        "payload": 10,
        "sector": "Agriculture",
        "pros": ["Made in India", "Precision spraying", "Subsidy eligible"],
        "cons": ["Premium pricing"]
    },
    {
        "model_name": "NETRA v4",
        "manufacturer": "ideaForge",
        "price_lakhs": 45,
        "flight_time": 90,
        "payload": 1.5,
        "sector": "Defense",
        "pros": ["VTOL", "Long endurance", "Battle-tested"],
        "cons": ["Restricted to defense/enterprise"]
    },
    {
        "model_name": "A410",
        "manufacturer": "Asteria Aerospace",
        "price_lakhs": 12,
        "flight_time": 40,
        "payload": 2,
        "sector": "Survey",
        "pros": ["High-res mapping", "SVAMITVA ready"],
        "cons": ["Not for spraying"]
    },
    {
        "model_name": "Kisan Drone 2.0",
        "manufacturer": "Garuda Aerospace",
        "price_lakhs": 6.8,
        "flight_time": 20,
        "payload": 10,
        "sector": "Agriculture",
        "pros": ["Affordable", "PLI beneficiary", "Rural service network"],
        "cons": ["Shorter flight time"]
    },
    {
        "model_name": "Defender VTOL",
        "manufacturer": "Throttle Aerospace",
        "price_lakhs": 28,
        "flight_time": 75,
        "payload": 3,
        "sector": "Logistics",
        "pros": ["VTOL cargo", "BVLOS capable"],
        "cons": ["Regulatory heavy"]
    }
]

def recommend_drone(
    budget_lakhs: float,
    sector: str = "Agriculture",
    min_flight_time: float = 15.0,
    min_payload: float = 8.0
) -> List[Dict[str, Any]]:
    """
    Matches and ranks Indian drone models by budget, sector, payload, and endurance.
    """
    results = []
    for d in DRONES_CATALOGUE:
        if d["price_lakhs"] > budget_lakhs:
            continue
        if sector != "Any" and d["sector"] != sector:
            continue
        if d["flight_time"] < min_flight_time:
            continue
        if d["payload"] < min_payload:
            continue

        score = min(
            99,
            round(
                70
                + (budget_lakhs - d["price_lakhs"]) * 2
                + (d["flight_time"] - min_flight_time) * 0.4
                + (d["payload"] - min_payload) * 0.6
            )
        )
        res = dict(d)
        res["match_score"] = score
        results.append(res)

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results
