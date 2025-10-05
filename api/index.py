from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import json
import os

app = FastAPI()

# Enable CORS globally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry data from JSON file
telemetry_file_path = os.path.join(os.path.dirname(__file__), "telemetry.json")
try:
    with open(telemetry_file_path, "r") as f:
        telemetry_list = json.load(f)
except Exception as e:
    telemetry_list = []
    print("Error loading telemetry.json:", e)

# Group telemetry by region
telemetry_by_region = {}
for record in telemetry_list:
    region = record["region"]
    if region not in telemetry_by_region:
        telemetry_by_region[region] = []
    telemetry_by_region[region].append(record)

# Health check
@app.get("/")
def home():
    return {"message": "FastAPI running successfully on Vercel"}

# Handle preflight OPTIONS request for CORS
@app.options("/analytics")
def analytics_options():
    response = JSONResponse({"message": "CORS preflight OK"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# POST endpoint
@app.post("/analytics")
async def analytics(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 0)

    results = {}
    for region in regions:
        region_data = telemetry_by_region.get(region, [])
        if not region_data:
            results[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": None
            }
            continue

        latencies = [x["latency_ms"] for x in region_data]
        uptimes = [x["uptime_pct"] for x in region_data]

        results[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    response = JSONResponse(content=results)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
