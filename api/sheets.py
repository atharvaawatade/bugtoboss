import os
import logging
import traceback
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)

class GoogleSheetService:
    def __init__(self):
        logger.info("Initializing GoogleSheetService")
        try:
            self.scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Log all environment variables for debugging
            logger.debug("Environment Variables:")
            for key, value in os.environ.items():
                logger.debug(f"{key}: {'[REDACTED]' if 'KEY' in key or 'SECRET' in key else value}")
            
            # Try to parse credentials from environment variables
            credentials_dict = {
                "type": os.getenv("GOOGLE_ACCOUNT_TYPE"),
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n'),
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
                "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
                "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL")
            }
            
            # Remove None values
            credentials_dict = {k: v for k, v in credentials_dict.items() if v is not None}
            
            # Log the credentials dictionary (without sensitive info)
            safe_creds = {k: '***' if 'key' in k.lower() else v for k, v in credentials_dict.items()}
            logger.debug(f"Parsed Credentials: {safe_creds}")
            
            # Validate required keys
            required_keys = ["private_key", "client_email", "client_id"]
            missing_keys = [key for key in required_keys if not credentials_dict.get(key)]
            
            if missing_keys:
                raise ValueError(f"Missing required credentials: {missing_keys}")
            
            # Create credentials
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                credentials_dict, self.scope)
            
            self.client = gspread.authorize(creds)
            logger.info("Google Sheets client created successfully")
            
            self.worksheet = None
        except Exception as e:
            logger.error(f"Error initializing GoogleSheetService: {e}")
            logger.error(traceback.format_exc())
            raise

    def verify_connection(self):
        try:
            logger.info("Verifying Google Sheets connection")
            
            sheet_id = os.getenv("SHEET_ID")
            sheet_name = os.getenv("SHEET_NAME", "Submissions")
            
            logger.debug(f"Attempting to open sheet: {sheet_id}, Worksheet: {sheet_name}")
            
            spreadsheet = self.client.open_by_key(sheet_id)
            self.worksheet = spreadsheet.worksheet(sheet_name)
            
            logger.info("Sheet connection verified successfully")
            return True
        except Exception as e:
            logger.error(f"Sheet connection verification failed: {e}")
            logger.error(traceback.format_exc())
            return False

    def append_submission(self, data: dict):
        try:
            logger.info("Attempting to append submission")
            
            if not self.verify_connection():
                logger.error("Cannot append - connection verification failed")
                return False
            
            row = [
                data["name"],
                data["email"],
                str(data["github_url"]),
                str(data["linkedin_url"]),
                str(data["twitter_url"]),
                data.get("submission_date", "")
            ]
           
            logger.debug(f"Appending row: {row}")
            self.worksheet.append_row(row, value_input_option='RAW')
            
            logger.info("Submission appended successfully")
            return True
        except Exception as e:
            logger.error(f"Error appending submission: {e}")
            logger.error(traceback.format_exc())
            return False
