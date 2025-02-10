import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetService:
    def append_submission(self, data: dict):
        try:
            # Setup credentials
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            # Get private key from environment
            private_key = os.environ.get("GOOGLE_PRIVATE_KEY", "")
            if "\\n" in private_key:
                private_key = private_key.replace("\\n", "\n")
            
            creds_dict = {
                "type": "service_account",
                "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
                "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": private_key,
                "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_CERT_URL")
            }

            # Create credentials and client
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            
            # Access the sheet
            sheet_id = os.environ.get("SHEET_ID")
            if not sheet_id:
                raise ValueError("SHEET_ID environment variable is missing")
                
            sheet = client.open_by_key(sheet_id)
            worksheet = sheet.worksheet(os.environ.get("SHEET_NAME", "Submissions"))
            
            # Append data
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
            print(f"Detailed error: {str(e)}")
            raise Exception(f"Failed to submit: {str(e)}")
