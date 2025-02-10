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
            
            # Ensure private key is properly formatted
            private_key = os.getenv("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n').strip()
            
            # Create credentials dictionary
            credentials_dict = {
                "type": "service_account",
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": private_key,
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
                "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
                "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL")
            }
            
            # Remove None values
            credentials_dict = {k: v for k, v in credentials_dict.items() if v is not None}
            
            # Validate private key
            if not private_key:
                raise ValueError("Private key is empty or not properly set")
            
            # Attempt to create credentials
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                credentials_dict, self.scope)
            
            self.client = gspread.authorize(creds)
            logger.info("Google Sheets client created successfully")
            
            self.worksheet = None
        except Exception as e:
            logger.error(f"Error initializing GoogleSheetService: {e}")
            logger.error(f"Credentials: {json.dumps({k: '***' if 'key' in k.lower() else v for k, v in credentials_dict.items()})}")
            logger.error(traceback.format_exc())
            raise

    def verify_connection(self):
        try:
            sheet_id = os.getenv("SHEET_ID")
            sheet_name = os.getenv("SHEET_NAME", "Submissions")
            
            spreadsheet = self.client.open_by_key(sheet_id)
            self.worksheet = spreadsheet.worksheet(sheet_name)
            
            return True
        except Exception as e:
            logger.error(f"Sheet connection verification failed: {e}")
            logger.error(traceback.format_exc())
            return False

    def append_submission(self, data: dict):
        try:
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
           
            self.worksheet.append_row(row, value_input_option='RAW')
            
            return True
        except Exception as e:
            logger.error(f"Error appending submission: {e}")
            logger.error(traceback.format_exc())
            return False
