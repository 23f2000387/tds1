# api/analytics.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load telemetry data from telemetry.json
telemetry_file = os.path.join(os.path.dirname(__file__), "telemetry.json")
with open(telemetry_file, "r") as f:
    telemetry_data = json.load(f)

@app.post("/analytics")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)

    response = {"regions": []}

    for region in regions:
        data = telemetry_data.get(region, [])
        if not data:
            response["regions"].append({
                "region": region,
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            })
            continue

        latencies = [d["latency_ms"] for d in data]
        uptimes = [d["uptime"] for d in data]
        breaches = sum(1 for l in latencies if l > threshold_ms)

        response["regions"].append({
            "region": region,
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 4),
            "breaches": breaches
        })

    return JSONResponse(content=response)
