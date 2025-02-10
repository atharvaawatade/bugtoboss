import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

# Load environment variables
load_dotenv()

class GoogleSheetService:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        # Don't initialize connection in constructor
        self.client = None
        self.worksheet = None
        
    def _get_connection(self):
        if self.client is None:
            try:
                credentials_dict = {
                    "type": "service_account",
                    "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
                    "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID"),
                    "private_key": os.environ.get("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
                    "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
                    "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_CERT_URL")
                }
                
                creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, self.scope)
                self.client = gspread.authorize(creds)
            except Exception as e:
                print(f"Connection error: {str(e)}")
                raise e

    def append_submission(self, data: dict):
        try:
            self._get_connection()
            sheet = self.client.open_by_key(os.environ.get("SHEET_ID"))
            worksheet = sheet.worksheet(os.environ.get("SHEET_NAME", "Submissions"))
            
            row = [
                data["name"],
                data["email"],
                str(data["github_url"]),
                str(data["linkedin_url"]),
                str(data["twitter_url"]),
                data.get("submission_date", "")
            ]
            
            worksheet.append_row(row, value_input_option='RAW')
            return True
        except Exception as e:
            print(f"Submission error: {str(e)}")
            raise e
