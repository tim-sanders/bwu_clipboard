import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Function to authenticate and connect to Google Sheets
def connect_to_google_sheets(credentials_dict, sheet_name, worksheet_name):
    """
    Authenticate and connect to a Google Sheets document.

    Args:
        credentials_dict (dict): The dictionary containing Google service account credentials.
        sheet_name (str): The name of the Google Sheets document.
        worksheet_name (str): The name of the worksheet within the Google Sheets document.

    Returns:
        gspread.models.Worksheet: The Google Sheets worksheet object.
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    return sheet