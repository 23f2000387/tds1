# api/analytics.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow any origin
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Sample telemetry data
telemetry_data = {
    "emea": [
        {"latency_ms": 150, "uptime": 0.99},
        {"latency_ms": 170, "uptime": 0.98},
        {"latency_ms": 160, "uptime": 0.97},
    ],
    "apac": [
        {"latency_ms": 200, "uptime": 0.95},
        {"latency_ms": 180, "uptime": 0.96},
        {"latency_ms": 175, "uptime": 0.97},
    ],
    # Add more regions if needed
}

@app.post("/analytics")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)
    result = {}

    for region in regions:
        data = telemetry_data.get(region, [])
        if not data:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        latencies = [d["latency_ms"] for d in data]
        uptimes = [d["uptime"] for d in data]
        breaches = sum(1 for l in latencies if l > threshold_ms)

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 4),
            "breaches": breaches
        }

    return JSONResponse(content=result)
