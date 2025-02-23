import streamlit as st
import pandas as pd
import random
from modules.google_sheets_connection import connect_to_google_sheets

# Input fields for JSON keyfile, Google Sheets name, and worksheet name
credentials = st.secrets["gcp_service_account"]
sheet_name = st.secrets["SHEET_NAME"]
worksheet_name = st.secrets["WORKSHEET_NAME"]


def load_data_ui():
    """
    Load data from the specified Google Sheets document and display it in a Streamlit app.

    This function creates a button in the Streamlit app. When the button is clicked,
    it connects to the specified Google Sheets document, retrieves the data, and
    displays it as a DataFrame in the app.
    """
    if st.button("Load Data"):
        try:
            sheet = connect_to_google_sheets(credentials, sheet_name, worksheet_name)
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            st.write("Data from Google Sheets:")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error: {e}")


def insert_random_integer(sheet):
    """
    Insert a random integer between 100 and 999 into the specified Google Sheets worksheet.

    Args:
        sheet (gspread.models.Worksheet): The Google Sheets worksheet object.

    Returns:
        int: The random integer that was inserted into the worksheet.
    """
    random_integer = random.randint(100, 999)
    sheet.append_row([random_integer])
    return random_integer


def add_random_integer_ui():
    """
    Add a random integer to the specified Google Sheets worksheet and display a success message.

    This function creates a button in the Streamlit app. When the button is clicked,
    it connects to the specified Google Sheets document, inserts a random integer
    into the worksheet, and displays a success message with the inserted integer.
    """
    if st.button("Add Random Integer"):
        try:
            # Read credentials from Streamlit secrets
            credentials = st.secrets["gcp_service_account"]
            sheet = connect_to_google_sheets(credentials, sheet_name, worksheet_name)
            random_integer = insert_random_integer(sheet)
            st.success(f"Inserted random integer: {random_integer}")
        except Exception as e:
            st.error(f"Error: {e}")
