import os
import json
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetService:
    def __init__(self):
        try:
            print("Initializing GoogleSheetService")

            # Load credentials from environment variables
            credentials_json = {
                "type": os.getenv("GOOGLE_ACCOUNT_TYPE"),
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),  # Fix formatting issue
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL')}"
            }

            # Check if private key is present
            if not credentials_json["private_key"]:
                raise ValueError("Private key is missing from environment variables!")

            # Load credentials
            self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
                credentials_json,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )

            print("GoogleSheetService initialized successfully!")

        except Exception as e:
            print(f"Error initializing GoogleSheetService: {e}")
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
