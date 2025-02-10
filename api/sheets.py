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
        self._setup_client()
        
    def _setup_client(self):
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
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, self.scope)
        self.client = gspread.authorize(creds)
        self.worksheet = self.client.open_by_key(os.getenv("SHEET_ID")).worksheet(os.getenv("SHEET_NAME", "Submissions"))

    def verify_connection(self):
        return True

    def append_submission(self, data: dict):
        try:
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
        except:
            return False