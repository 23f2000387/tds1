# api/index.py
from fastapi import FastAPI, Request
import os
import json
import numpy as np
from starlette.responses import PlainTextResponse

app = FastAPI()

# Load telemetry.json
telemetry_file = os.path.join(os.path.dirname(__file__), "telemetry.json")
with open(telemetry_file, "r") as f:
    telemetry_list = json.load(f)

telemetry_by_region = {}
for record in telemetry_list:
    telemetry_by_region.setdefault(record["region"], []).append(record)

# CORS headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "*"
}

# Handle OPTIONS preflight
@app.options("/analytics")
async def analytics_options():
    return PlainTextResponse("", status_code=200, headers=CORS_HEADERS)

# POST endpoint
@app.post("/analytics")
async def analytics(request: Request):
    try:
        data = await request.json()
    except:
        return {"error": "Invalid JSON"}, 400, CORS_HEADERS

    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 0)
    results = {}

    for region in regions:
        region_data = telemetry_by_region.get(region, [])
        if not region_data:
            results[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": None}
            continue

        latencies = [x["latency_ms"] for x in region_data]
        uptimes = [x["uptime_pct"] for x in region_data]

        results[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return results, 200, CORS_HEADERS

# Health check
@app.get("/")
def home():
    return {"message": "FastAPI running successfully on Vercel"}
