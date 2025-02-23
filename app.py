import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import random

# Function to authenticate and connect to Google Sheets
def connect_to_google_sheets(credentials_dict, sheet_name, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    return sheet

# Function to validate login credentials
def validate_login(username, password):
    # Replace with your own validation logic
    return username == st.secrets["APP_USERNAME"] and password == st.secrets["APP_PASSWORD"]

def insert_random_integer(sheet):
    random_integer = random.randint(100, 999)
    sheet.append_row([random_integer])
    return random_integer

# Streamlit application
def main():
    st.title("Google Sheets Data Viewer")

    # Check if the user is logged in
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Login form
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if validate_login(username, password):
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    else:
        st.title("Logged in")
        # Input fields for JSON keyfile, Google Sheets name, and worksheet name
        credentials = st.secrets["gcp_service_account"]
        sheet_name = "Ski 25 - Via Lattea"
        worksheet_name = "test"

        if st.button("Load Data"):
            try:
                sheet = connect_to_google_sheets(credentials, sheet_name, worksheet_name)
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                st.write("Data from Google Sheets:")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error: {e}")

        if st.button("Add Random Integer"):
            try:
                # Read credentials from Streamlit secrets
                credentials = st.secrets["gcp_service_account"]
                sheet = connect_to_google_sheets(credentials, sheet_name, worksheet_name)
                random_integer = insert_random_integer(sheet)
                st.success(f"Inserted random integer: {random_integer}")
            except Exception as e:
                st.error(f"Error: {e}")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.success("Logged out successfully!")
            st.rerun()

if __name__ == "__main__":
    main()
