from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import numpy as np

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Allow all headers
)

# Load telemetry data from JSON
with open("vercel.json", "r") as f:
    telemetry_list = json.load(f)

# Preprocess: group data by region
telemetry_by_region = {}
for record in telemetry_list:
    region = record["region"]
    if region not in telemetry_by_region:
        telemetry_by_region[region] = []
    telemetry_by_region[region].append(record)

@app.get("/")
def home():
    return {"message": "FastAPI running successfully on Vercel"}

@app.options("/analytics")
def analytics_options():
    """Handle preflight OPTIONS request for CORS"""
    response = JSONResponse({"message": "CORS preflight OK"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

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

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = sum(1 for x in latencies if x > threshold)

        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }

    response = JSONResponse(content=results)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
