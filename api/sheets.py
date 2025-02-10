import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

class GoogleSheetService:
    def __init__(self):
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = self._get_client()
        self.worksheet = None
       
    def _get_client(self):
        try:
            # Use environment variables for credentials
            credentials_dict = {
                "type": os.getenv("GOOGLE_ACCOUNT_TYPE"),
                "project_id": os.getenv("GOOGLE_PROJECT_ID"),
                "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
                "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
                "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
                "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL")
            }
            
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                credentials_dict, self.scope)
            return gspread.authorize(creds)
        except Exception as e:
            print(f"Client creation error: {e}")
            return None

    def verify_connection(self):
        try:
            if not self.client:
                return False
            
            sheet_id = os.getenv("SHEET_ID")
            sheet_name = os.getenv("SHEET_NAME", "Submissions")
            
            spreadsheet = self.client.open_by_key(sheet_id)
            self.worksheet = spreadsheet.worksheet(sheet_name)
            return True
        except Exception as e:
            print(f"Connection verification error: {e}")
            return False

    def append_submission(self, data: dict):
        try:
            if not self.verify_connection():
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
            print(f"Submission error: {e}")
            return False
