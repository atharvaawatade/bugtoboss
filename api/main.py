import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from api.sheets import GoogleSheetService
from api.models import ProjectSubmission

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables at startup
load_dotenv()

app = FastAPI(title="BugToBoss Submission API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize sheets service at startup
sheets_service = GoogleSheetService()

@app.get("/")
async def root():
    return {"message": "Bug to Boss API is running!"}

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