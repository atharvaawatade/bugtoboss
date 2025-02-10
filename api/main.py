import os
import sys
import logging
import traceback
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from api.sheets import GoogleSheetService
    from api.models import ProjectSubmission
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from datetime import datetime
    from fastapi.responses import FileResponse

    logger.info("Imports successful")

    app = FastAPI(title="BugToBoss Submission API")

    # Add static files mounting with error handling
    try:
        static_dir = Path(__file__).parent.parent / "static"
        if not static_dir.exists():
            logger.warning(f"Static directory not found at {static_dir}, creating it")
            static_dir.mkdir(parents=True, exist_ok=True)
            
            # Create an empty favicon.png if it doesn't exist
            favicon_path = static_dir / "favicon.png"
            if not favicon_path.exists():
                with open(favicon_path, "wb") as f:
                    f.write(b"")
        
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        logger.info(f"Successfully mounted static directory at {static_dir}")
    except Exception as e:
        logger.error(f"Error mounting static directory: {e}")
        # Continue without static files if there's an error

    @app.get('/favicon.png')
    async def favicon():
        static_dir = Path(__file__).parent.parent / "static"
        favicon_path = static_dir / "favicon.png"
        if favicon_path.exists():
            return FileResponse(str(favicon_path))
        return {"status": "no favicon"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize GoogleSheetService globally
    sheets_service = GoogleSheetService()
    logger.info("GoogleSheetService initialized successfully")

    @app.post("/api/submit")
    async def submit_project(submission: ProjectSubmission):
        try:
            logger.info("Submit project endpoint called")
            submission_data = submission.model_dump()
            submission_data["submission_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           
            if not sheets_service.append_submission(submission_data):
                logger.error("Failed to append submission to Google Sheets")
                raise HTTPException(status_code=500, detail="Failed to submit to Google Sheets")
           
            logger.info("Project submitted successfully")
            return {"status": "success", "message": "Project submitted successfully"}
        except Exception as e:
            logger.error(f"Error in submit_project: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/health")
    async def health_check():
        logger.info("Health check endpoint called")
        return {"status": "healthy"}

    @app.get("/api/check-sheet")
    async def check_sheet_connection():
        try:
            logger.info("Checking sheet connection")
            if sheets_service.verify_connection():
                logger.info("Sheet connection verified")
                return {"status": "success", "message": "Google Sheets connection verified"}
            logger.error("Sheet connection failed")
            raise HTTPException(status_code=500, detail="Google Sheets connection failed")
        except Exception as e:
            logger.error(f"Error checking sheet connection: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))

    # For local testing
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)

except Exception as global_error:
    logger.critical(f"Global import/setup error: {global_error}")
    logger.critical(traceback.format_exc())
    raise
