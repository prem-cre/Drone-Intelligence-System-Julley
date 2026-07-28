import math
from typing import Dict, Any

def calculate_roi(
    sector: str,
    investment: float,
    monthly_opex: float,
    fee_per_acre: float,
    monthly_acres: float,
    subsidy_pct: float = 0.0
) -> Dict[str, Any]:
    """
    Computes agricultural & commercial drone operations ROI and payback timeline.
    """
    monthly_revenue = fee_per_acre * monthly_acres
    net_monthly_profit = monthly_revenue - monthly_opex
    effective_investment = investment * (1.0 - subsidy_pct / 100.0)
    
    payback_months = math.ceil(effective_investment / net_monthly_profit) if net_monthly_profit > 0 else 999
    roi_3yr_pct = (
        round(((net_monthly_profit * 36 - effective_investment) / effective_investment) * 100)
        if net_monthly_profit > 0 else 0
    )
    
    projection = []
    for year in range(1, 4):
        projection.append({
            "year": f"Year {year}",
            "revenue": monthly_revenue * 12 * year,
            "profit": net_monthly_profit * 12 * year - (effective_investment if year == 1 else 0)
        })
        
    return {
        "monthly_revenue": round(monthly_revenue),
        "net_monthly_profit": round(net_monthly_profit),
        "payback_months": payback_months,
        "roi_3yr_pct": roi_3yr_pct,
        "projection": projection
    }
