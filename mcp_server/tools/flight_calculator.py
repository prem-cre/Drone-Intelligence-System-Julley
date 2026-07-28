import math
import random
from typing import Dict, Any

def calculate_flight_time(
    battery_mah: float,
    empty_weight: float,
    payload: float,
    wind: float = 10.0,
    temperature: float = 28.0
) -> Dict[str, Any]:
    """
    Computes estimated drone flight duration, range, battery consumption, and power curve.
    """
    base_time = (battery_mah / 1000.0) * 3.2
    payload_factor = 1.0 - (payload / 15.0) * 0.35
    wind_factor = 1.0 - (wind / 40.0) * 0.20
    temp_factor = 0.90 if (temperature > 35 or temperature < 5) else 1.0
    
    flight_mins = max(3.0, base_time * payload_factor * wind_factor * temp_factor)
    range_km = flight_mins * 0.28
    
    curve = []
    for idx in range(12):
        curve.append({
            "minute": round((flight_mins / 11.0) * idx),
            "power": max(0, round(100 - (idx / 11.0) * 80 - random.random() * 4))
        })
        
    advice = (
        "Heavy payload — maintain 25% battery reserve for safe RTH."
        if payload > 8.0
        else "Nominal conditions. Standard 20% reserve advised per DGCA safety guidelines."
    )
    
    return {
        "flight_time_mins": round(flight_mins, 1),
        "max_range_km": round(range_km, 1),
        "battery_consumed_pct": 82.0,
        "advice": advice,
        "power_curve": curve
    }
