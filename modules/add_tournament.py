import streamlit as st
import pandas as pd
from modules.google_sheets_connection import connect_to_google_sheets
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Input fields for JSON keyfile, Google Sheets name, and worksheet name
credentials = st.secrets["gcp_service_account"]
sheet_name = st.secrets["SHEET_NAME"]
tournament_tab_name = st.secrets["TOURNAMENT_TAB_NAME"]
roster_tab_name = st.secrets["ROSTER_TAB_NAME"]
tournament_roster_tab_name = st.secrets["TOURNAMENT_ROSTER_TAB_NAME"]


def get_roster():
    """
    Get the club roster from the roster tab in Google Sheets.
    
    Returns:
        pandas.DataFrame: DataFrame containing the club roster.
    """
    try:
        sheet = connect_to_google_sheets(credentials, sheet_name, roster_tab_name)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        raise e


def add_tournament(tournament_name, selected_players):
    """
    Add a new tournament and its roster using the most efficient approach.
    
    Args:
        tournament_name (str): The name of the tournament to add.
        selected_players (list): List of dictionaries containing player info and assignments.
        
    Returns:
        bool: True if the tournament was successfully added, False otherwise.
    """
    try:
        # Connect to Google Sheets once
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open(sheet_name)
        
        # Get tournament worksheet
        tournament_sheet = spreadsheet.worksheet(tournament_tab_name)
        
        # Check if tournament exists
        all_tournaments = tournament_sheet.get_all_records()
        for row in all_tournaments:
            if 'tournament_name' in row and row['tournament_name'] == tournament_name:
                return False
                
        # Add tournament
        tournament_sheet.append_row([tournament_name], value_input_option='RAW')
        
        # Get tournament roster worksheet
        roster_sheet = spreadsheet.worksheet(tournament_roster_tab_name)
        
        # Filter only selected players and prepare data for batch insert
        selected_players_data = [
            [tournament_name, p['player_name'], p['line'], p['position']]
            for p in selected_players if p['selected']
        ]
        
        # Use batch append for maximum efficiency
        if selected_players_data:
            roster_sheet.append_rows(
                selected_players_data, 
                value_input_option='RAW',  # Use RAW for faster processing
                insert_data_option='INSERT_ROWS',
                table_range='A1'  # Ensure data is added to the right range
            )
        
        return True
    except Exception as e:
        raise e


def add_tournament_ui():
    """
    Display UI for adding a new tournament with player selection.
    
    This function creates a form in the Streamlit app that allows the user to enter a
    tournament name and select players from the roster with their line and position assignments.
    When the form is submitted, it adds the tournament and player information to the Google
    Sheets document and displays a success or error message.
    """
    st.subheader("Add New Tournament")
    
    try:
        # Get the roster first
        roster_df = get_roster()
    except Exception as e:
        st.error(f"Error loading roster: {e}")
        return
    
    # Create a form for tournament details
    with st.form(key='add_tournament_form'):
        tournament_name = st.text_input("Tournament Name")
        
        st.subheader("Select Players")
        
        # Initialize a list to store player selections
        player_selections = []
        
        # Display each player with selection options
        for index, row in roster_df.iterrows():
            player_name = row.get('player_name', f"Player {index + 1}")
            
            # Create a container for each player
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                selected = st.checkbox("Select", key=f"select_{index}")
            
            with col2:
                player_info = st.text(f"{player_name}")
            
            with col3:
                line = st.selectbox("Line", 
                                    options=["O", "D"], 
                                    key=f"line_{index}")
            
            with col4:
                position = st.selectbox("Position", 
                                        options=["Handler", "Cutter", "Hybrid"], 
                                        key=f"position_{index}")
            
            # Add player info to selections
            player_selections.append({
                'player_name': player_name,
                'selected': selected,
                'line': line,
                'position': position
            })
        
        # Submit button
        submit_button = st.form_submit_button(label='Add Tournament')
    
    # Process form submission
    if submit_button:
        if not tournament_name:
            st.error("Tournament name cannot be empty")
            return
        
        selected_count = sum(1 for player in player_selections if player['selected'])
        if selected_count == 0:
            st.warning("No players selected for the tournament")
            return
            
        try:
            success = add_tournament(tournament_name, player_selections)
            if success:
                st.success(f"Successfully added tournament '{tournament_name}' with {selected_count} players")
            else:
                st.warning(f"Tournament '{tournament_name}' already exists")
        except gspread.exceptions.APIError as e:
            st.error(f"API Error: {e.response.text}")
        except Exception as e:
            st.error(f"Error: {e}")
