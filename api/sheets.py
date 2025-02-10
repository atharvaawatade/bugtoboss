import os
import logging
import traceback
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
            
            # Log credential retrieval process
            logger.debug("Retrieving credentials from environment")
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
            
            logger.debug("Attempting to create service account credentials")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                credentials_dict, self.scope)
            
            logger.debug("Authorizing with gspread")
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
