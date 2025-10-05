# /// script
# requires-python = ">=3.11"
# dependencies = ["fastapi", "uvicorn", "pandas"]
# ///

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Optional

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow a specific domain
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow specific methods
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load CSV data
df = pd.read_csv("students.csv")  # Columns: studentId, class

@app.get("/api")
async def get_students(class_filter: Optional[List[str]] = Query(None, alias="class")):
    # Filter by class if provided
    if class_filter:
        filtered_df = df[df['class'].isin(class_filter)]
    else:
        filtered_df = df

    # Convert to list of dicts
    students = filtered_df.to_dict(orient="records")
    return {"students": students}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
