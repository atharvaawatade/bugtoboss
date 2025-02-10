from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from api.sheets import GoogleSheetService
from api.models import ProjectSubmission

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/submit")
async def submit_project(submission: ProjectSubmission):
    try:
        service = GoogleSheetService()
        data = submission.model_dump()
        data["submission_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        service.append_submission(data)
        return {"status": "success", "message": "Submitted successfully"}
    
    except Exception as e:
        print(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "online"}
