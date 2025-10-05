from fastapi import FastAPI, Request
from fastapi.responses import Response
import json
import os
import numpy as np

app = FastAPI()

# Load telemetry data
telemetry_file = os.path.join(os.path.dirname(__file__), "telemetry.json")
with open(telemetry_file, "r") as f:
    telemetry_list = json.load(f)

# Group by region
telemetry_by_region = {}
for record in telemetry_list:
    telemetry_by_region.setdefault(record["region"], []).append(record)

@app.api_route("/analytics", methods=["POST", "OPTIONS"])
async def analytics(request: Request):
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }

    if request.method == "OPTIONS":
        return Response(content="", status_code=200, headers=cors_headers)

    try:
        data = await request.json()
    except:
        return Response(content='{"error":"Invalid JSON"}', status_code=400, media_type="application/json", headers=cors_headers)

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

    return Response(content=json.dumps(results), status_code=200, media_type="application/json", headers=cors_headers)

@app.get("/")
def home():
    return {"message": "FastAPI running successfully on Vercel"}
