import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.sheets import GoogleSheetService
from api.models import ProjectSubmission

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="BugToBoss Submission API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sheets_service = GoogleSheetService()

@app.post("/api/submit")
async def submit_project(submission: ProjectSubmission):
    try:
        submission_data = submission.model_dump()
        submission_data["submission_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       
        if not sheets_service.append_submission(submission_data):
            raise HTTPException(status_code=500, detail="Failed to submit to Google Sheets")
           
        return {"status": "success", "message": "Project submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/check-sheet")
async def check_sheet_connection():
    if sheets_service.verify_connection():
        return {"status": "success", "message": "Google Sheets connection verified"}
    raise HTTPException(status_code=500, detail="Google Sheets connection failed")

# For local testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
