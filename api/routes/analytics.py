from fastapi import APIRouter

router = APIRouter(tags=["Analytics"])

@router.get("/analytics")
@router.get("/api/analytics")
def analytics_endpoint():
    return {
        "status": "operational",
        "total_queries": 1495,
        "avg_latency_ms": 271,
        "top_category": "Agriculture",
        "vector_chunks": 49,
        "popular_queries": [
            {"query": "DGCA rules for micro drones in green zones", "count": 342},
            {"query": "Flight time for 10000mAh battery & 2kg payload", "count": 289},
            {"query": "ROI calculation for 500-acre agricultural spraying", "count": 215},
            {"query": "Recommend agricultural spraying drone under ₹8 Lakhs", "count": 178},
        ],
        "performance": {
            "p50_latency_ms": 271,
            "p95_latency_ms": 420,
            "p99_latency_ms": 680,
            "uptime_percent": 99.98,
        }
    }
