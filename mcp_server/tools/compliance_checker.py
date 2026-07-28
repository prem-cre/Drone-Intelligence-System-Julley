from typing import Dict, Any, List

def check_compliance(
    weight_category: str,
    purpose: str,
    zone: str,
    altitude: float = 200.0,
    rpc: bool = False
) -> Dict[str, Any]:
    """
    Verifies flight operation compliance under India DGCA Drone Rules 2021.
    """
    status = "APPROVED"
    permits: List[str] = []
    penalties = "No penalties expected under Drone Rules 2021."

    if zone == "Red":
        status = "PROHIBITED"
        penalties = "Flying in Red Zone attracts fines up to ₹1,00,000 + drone seizure under Rule 24, Drone Rules 2021."
    elif zone == "Yellow":
        status = "RESTRICTED"
        permits.append("ATC Clearance via DigitalSky")
        permits.append("Prior flight plan filing (24h notice)")
        penalties = "Unauthorized Yellow Zone flight: ₹25,000 – ₹50,000 penalty."

    if altitude > 400:
        if status == "APPROVED":
            status = "RESTRICTED"
        permits.append("Altitude Exemption from DGCA")

    if weight_category in ("Small", "Medium", "Large") and not rpc:
        status = "RESTRICTED"
        permits.append("Remote Pilot Certificate (RPC) from approved RPTO")

    if weight_category != "Nano":
        permits.append("UIN Registration on DigitalSky")
        permits.append("NPNT-Compliant Drone Hardware")

    workflow = [
        "Register drone on DigitalSky Platform",
        "Obtain UIN (Unique Identification Number)",
        "Complete Remote Pilot Certification (if applicable)",
        "File flight plan & obtain airspace clearance",
        "Ensure NPNT firmware compliance",
        "Conduct pre-flight safety check"
    ]

    return {
        "status": status,
        "zone": f"{zone} Zone",
        "permits": list(set(permits)),
        "penalties": penalties,
        "workflow": workflow
    }
