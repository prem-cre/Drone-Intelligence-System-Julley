import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def chunk_text(text, chunk_size=1000, overlap=150):
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        if end < text_len:
            # Snap to last space or newline to avoid cutting words
            space_pos = text.rfind(' ', start + 100, end)
            if space_pos != -1:
                end = space_pos
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_len:
            break
        start = max(start + 1, end - overlap)
    return chunks

def process_all_raw_data():
    all_chunks = []
    chunk_id_counter = 1
    
    # 1. Process Markdown documents
    md_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".md")]
    for md_file in md_files:
        path = os.path.join(RAW_DIR, md_file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        sections = content.split("\n## ")
        for section in sections:
            lines = section.strip().split("\n")
            title = lines[0].replace("#", "").strip() if lines else md_file
            body = "\n".join(lines[1:]) if len(lines) > 1 else section
            
            sub_chunks = chunk_text(body, chunk_size=1200, overlap=150)
            for chunk in sub_chunks:
                all_chunks.append({
                    "id": f"chunk-{chunk_id_counter}",
                    "content": f"{title}\n{chunk}",
                    "metadata": {
                        "source": md_file,
                        "title": title,
                        "category": "handbook" if "handbook" in md_file else "case_study"
                    }
                })
                chunk_id_counter += 1
                
    # 2. Process JSON datasets
    # Drone models
    drone_models_path = os.path.join(RAW_DIR, "drone_models.json")
    if os.path.exists(drone_models_path):
        with open(drone_models_path, "r", encoding="utf-8") as f:
            drones = json.load(f)
            for d in drones:
                text = (
                    f"Drone Model: {d['model_name']} by {d['manufacturer']}. Category: {d['category']}. "
                    f"Weight: {d['weight_kg']} kg. Battery: {d['battery_capacity_mah']} mAh. "
                    f"Max Payload: {d['max_payload_kg']} kg. Flight Time: {d['max_flight_time_mins']} mins. "
                    f"Max Range: {d['max_range_km']} km. Price: ₹{d['price_inr_lakhs']} Lakhs. "
                    f"Primary Use: {d['primary_use_case']}. Key Features: {', '.join(d['features'])}."
                )
                all_chunks.append({
                    "id": f"chunk-{chunk_id_counter}",
                    "content": text,
                    "metadata": {
                        "source": "drone_models.json",
                        "title": f"Specification: {d['model_name']}",
                        "category": "specifications"
                    }
                })
                chunk_id_counter += 1
                
    # Rules regulations
    rules_path = os.path.join(RAW_DIR, "rules_regulations.json")
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            rules_data = json.load(f)
            
            for cat in rules_data.get("drone_categories", []):
                text = (
                    f"DGCA Category: {cat['category']}. Weight: {cat['weight_range']}. Max Speed: {cat['max_speed_m_s']} m/s. "
                    f"UIN Required: {cat['uin_required']}. Pilot License Required: {cat['pilot_license_required']}. "
                    f"NPNT Required: {cat['npnt_required']}. Rules: {cat['operating_rules']}"
                )
                all_chunks.append({
                    "id": f"chunk-{chunk_id_counter}",
                    "content": text,
                    "metadata": {
                        "source": "rules_regulations.json",
                        "title": f"DGCA Category {cat['category']} Rules",
                        "category": "regulations"
                    }
                })
                chunk_id_counter += 1
                
            for zone in rules_data.get("airspace_zones", []):
                text = f"Airspace Zone: {zone['zone']}. Description: {zone['description']}. Requirements: {zone['permission_needed']}"
                all_chunks.append({
                    "id": f"chunk-{chunk_id_counter}",
                    "content": text,
                    "metadata": {
                        "source": "rules_regulations.json",
                        "title": f"Airspace Zone {zone['zone']}",
                        "category": "regulations"
                    }
                })
                chunk_id_counter += 1

            for pen in rules_data.get("penalties_and_fines", []):
                text = f"DGCA Fine & Penalty: Violation '{pen['violation']}'. Fine: ₹{pen['penalty_inr']}. Action: {pen['legal_action']}."
                all_chunks.append({
                    "id": f"chunk-{chunk_id_counter}",
                    "content": text,
                    "metadata": {
                        "source": "rules_regulations.json",
                        "title": f"Penalty: {pen['violation']}",
                        "category": "regulations"
                    }
                })
                chunk_id_counter += 1

    # Indian drone ecosystem
    eco_path = os.path.join(RAW_DIR, "indian_drone_ecosystem.json")
    if os.path.exists(eco_path):
        with open(eco_path, "r", encoding="utf-8") as f:
            eco = json.load(f)
            overview = eco.get("market_overview", {})
            text = (
                f"Indian Drone Market Overview: 2030 market size projected at ₹{overview.get('projected_market_size_2030_inr_crores')} Crores. "
                f"CAGR: {overview.get('cagr_percent')}%. Major Initiatives: {', '.join(overview.get('key_government_initiatives', []))}."
            )
            all_chunks.append({
                "id": f"chunk-{chunk_id_counter}",
                "content": text,
                "metadata": {
                    "source": "indian_drone_ecosystem.json",
                    "title": "Indian Drone Market Overview",
                    "category": "market_trends"
                }
            })
            chunk_id_counter += 1

            for comp in eco.get("top_indian_drone_companies", []):
                text = (
                    f"Indian Drone Company: {comp['name']} located in {comp['headquarters']}. Status: {comp['valuation_status']}. "
                    f"Focus: {comp['focus']}. Flagship Models: {', '.join(comp['flagship_products'])}."
                )
                all_chunks.append({
                    "id": f"chunk-{chunk_id_counter}",
                    "content": text,
                    "metadata": {
                        "source": "indian_drone_ecosystem.json",
                        "title": f"Company Profile: {comp['name']}",
                        "category": "startups"
                    }
                })
                chunk_id_counter += 1

    output_path = os.path.join(PROCESSED_DIR, "chunked_rag_docs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
        
    print(f"Preprocessed {len(all_chunks)} chunks -> {output_path}")

if __name__ == "__main__":
    process_all_raw_data()
