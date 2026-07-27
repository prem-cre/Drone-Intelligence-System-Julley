import os
import csv
import json
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SYNTHETIC_DIR = os.path.join(DATA_DIR, "synthetic")
os.makedirs(SYNTHETIC_DIR, exist_ok=True)

DRONE_MODELS = [
    {"name": "NETRA v4", "battery": 12000, "weight": 2.2},
    {"name": "Agribot MX", "battery": 22000, "weight": 14.5},
    {"name": "AG30", "battery": 30000, "weight": 28.0},
    {"name": "A410", "battery": 9500, "weight": 1.8},
    {"name": "Kisan Drone 2.0", "battery": 16000, "weight": 12.0},
    {"name": "Defender VTOL", "battery": 18000, "weight": 6.5},
    {"name": "Viper 25", "battery": 14000, "weight": 8.0}
]

CROPS = ["Paddy", "Cotton", "Sugarcane", "Chilli", "Wheat", "Soybean", "Tea"]
STATES = ["Telangana", "Andhra Pradesh", "Punjab", "Maharashtra", "Karnataka", "Tamil Nadu", "Haryana", "Uttar Pradesh"]

def generate_flight_telemetry(num_records=500):
    output_path = os.path.join(SYNTHETIC_DIR, "flight_telemetry.csv")
    headers = [
        "flight_id", "timestamp", "drone_model", "battery_capacity_mah", 
        "payload_weight_kg", "altitude_m", "wind_speed_kmh", 
        "temperature_c", "flight_duration_mins", "battery_consumed_percent", "status"
    ]
    
    base_time = datetime.now() - timedelta(days=30)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(1, num_records + 1):
            flight_id = f"FLG-{1000 + i}"
            timestamp = (base_time + timedelta(hours=i * 1.5, minutes=random.randint(0, 50))).strftime("%Y-%m-%d %H:%M:%S")
            model = random.choice(DRONE_MODELS)
            
            payload = round(random.uniform(0.0, 10.0), 2)
            altitude = round(random.uniform(15.0, 120.0), 1)
            wind_speed = round(random.uniform(2.0, 28.0), 1)
            temp = round(random.uniform(18.0, 42.0), 1)
            
            # Simulated physics calculation
            base_duration = 35.0
            weight_factor = 1.0 - (payload / 15.0) * 0.35
            wind_factor = 1.0 - (wind_speed / 40.0) * 0.20
            temp_factor = 1.0 - (max(0, temp - 30) / 30.0) * 0.15
            
            duration = max(5.0, round(base_duration * weight_factor * wind_factor * temp_factor + random.uniform(-3, 3), 1))
            battery_consumed = min(100.0, round(random.uniform(65.0, 95.0), 1))
            
            status = "COMPLETED"
            if wind_speed > 24.0 or temp > 40.0:
                if random.random() < 0.25:
                    status = "ABORTED_HIGH_WIND_OR_TEMP"
            
            writer.writerow([
                flight_id, timestamp, model["name"], model["battery"],
                payload, altitude, wind_speed, temp, duration, battery_consumed, status
            ])
            
    print(f"Generated {num_records} flight telemetry records -> {output_path}")

def generate_farm_roi_simulations(num_records=100):
    output_path = os.path.join(SYNTHETIC_DIR, "farm_roi_simulations.csv")
    headers = [
        "farm_id", "state", "crop_type", "farm_acres", "initial_investment_inr",
        "subsidy_percent", "net_investment_inr", "spraying_rate_per_acre_inr",
        "monthly_acres_covered", "monthly_revenue_inr", "monthly_op_cost_inr",
        "payback_period_months", "roi_3yr_percent"
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(1, num_records + 1):
            farm_id = f"FARM-{200 + i}"
            state = random.choice(STATES)
            crop = random.choice(CROPS)
            acres = random.randint(15, 300)
            
            initial_inv = random.choice([450000, 650000, 800000, 1000000])
            subsidy = random.choice([0, 40, 50, 80])
            net_inv = int(initial_inv * (1.0 - subsidy / 100.0))
            
            rate = random.choice([400, 450, 500, 550])
            monthly_acres = min(600, random.randint(150, 500))
            
            monthly_rev = monthly_acres * rate
            monthly_op_cost = int(monthly_rev * random.uniform(0.30, 0.45))
            monthly_profit = max(10000, monthly_rev - monthly_op_cost)
            
            payback_months = round(net_inv / monthly_profit, 1)
            
            total_profit_3yr = (monthly_profit * 36) - net_inv
            roi_3yr = round((total_profit_3yr / net_inv) * 100, 1)
            
            writer.writerow([
                farm_id, state, crop, acres, initial_inv, subsidy, net_inv,
                rate, monthly_acres, monthly_rev, monthly_op_cost,
                payback_months, roi_3yr
            ])
            
    print(f"Generated {num_records} farm ROI simulations -> {output_path}")

def generate_logistics_scenarios():
    output_path = os.path.join(SYNTHETIC_DIR, "logistics_scenarios.json")
    routes = []
    
    locations = [
        ("Shillong Hub", "Cherrapunji PHC", 48.5, 1200),
        ("Dehradun Hub", "Uttarkashi Hospital", 72.0, 1800),
        ("Shimla Hub", "Kinnaur Medical Center", 95.0, 2200),
        ("Imphal Hub", "Karang Island PHC", 32.0, 450),
        ("Guwahati Hub", "Barpeta Rural Clinic", 60.0, 850)
    ]
    
    for origin, dest, distance_km, terrain_alt in locations:
        routes.append({
            "route_id": f"RT-{random.randint(100,999)}",
            "origin": origin,
            "destination": dest,
            "distance_km": distance_km,
            "road_travel_time_mins": int(distance_km * 4.5),
            "drone_flight_time_mins": int(distance_km * 1.1),
            "time_saved_percent": round((1 - (1.1 / 4.5)) * 100, 1),
            "terrain_elevation_m": terrain_alt,
            "recommended_payload_kg": 2.5,
            "temperature_control_required": True,
            "digital_sky_permission": "GREEN_ZONE_PERMITTED"
        })
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(routes, f, indent=2)
        
    print(f"Generated logistics scenarios -> {output_path}")

if __name__ == "__main__":
    generate_flight_telemetry()
    generate_farm_roi_simulations()
    generate_logistics_scenarios()
