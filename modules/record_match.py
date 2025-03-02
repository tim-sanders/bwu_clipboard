import streamlit as st
import pandas as pd
from modules.google_sheets_connection import connect_to_google_sheets
import gspread
from datetime import datetime

# Input fields for JSON keyfile, Google Sheets name, and worksheet name
credentials = st.secrets["gcp_service_account"]
sheet_name = st.secrets["SHEET_NAME"]
tournament_tab_name = st.secrets["TOURNAMENT_TAB_NAME"]
tournament_roster_tab_name = st.secrets["TOURNAMENT_ROSTER_TAB_NAME"]
matches_tab_name = st.secrets["MATCHES_TAB_NAME"]

def get_tournaments():
    """
    Get the list of tournaments from the tournaments tab in Google Sheets.
    
    Returns:
        list: List of tournament names.
    """
    try:
        sheet = connect_to_google_sheets(credentials, sheet_name, tournament_tab_name)
        data = sheet.get_all_records()
        tournaments = [row.get('tournament_name') for row in data if 'tournament_name' in row]
        return tournaments
    except Exception as e:
        raise e

def get_tournament_roster(tournament_name):
    """
    Get the roster for a specific tournament from the tournament_rosters tab in Google Sheets.
    
    Args:
        tournament_name (str): The name of the tournament.
        
    Returns:
        pandas.DataFrame: DataFrame containing the tournament roster.
    """
    try:
        sheet = connect_to_google_sheets(credentials, sheet_name, tournament_roster_tab_name)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        # Filter for the selected tournament
        df = df[df['tournament_name'] == tournament_name]
        return df
    except Exception as e:
        raise e

def save_match_data(match_data):
    """
    Save the match data to the matches tab in Google Sheets.
    
    Args:
        match_data (list): List of lists containing match data rows.
        
    Returns:
        bool: True if the data was successfully saved, False otherwise.
    """
    try:
        sheet = connect_to_google_sheets(credentials, sheet_name, matches_tab_name)
        
        # Use batch append for efficiency
        if match_data:
            sheet.append_rows(
                match_data, 
                value_input_option='RAW',
                insert_data_option='INSERT_ROWS',
                table_range='A1'
            )
        
        return True
    except Exception as e:
        raise e

def record_match_ui():
    """
    Display UI for recording match data.
    
    This function creates a form in the Streamlit app that allows the user to select
    a tournament, enter opponent info, select players for a point, and record the outcome.
    When the form is submitted, it adds the match data to the matches tab in Google Sheets.
    """
    st.header("Record Match")
    
    # Initialize session state for match tracking
    if "match_info" not in st.session_state:
        st.session_state.match_info = {
            "tournament_name": None,
            "opponent": None,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "point_number": 1,
            "score_for": 0,
            "score_against": 0
        }
    
    # Tournament and opponent selection
    col1, col2 = st.columns(2)
    
    with col1:
        # Get list of tournaments
        try:
            tournaments = get_tournaments()
            # Tournament selection dropdown
            tournament_name = st.selectbox(
                "Select Tournament",
                tournaments,
                index=tournaments.index(st.session_state.match_info["tournament_name"]) if st.session_state.match_info["tournament_name"] in tournaments else 0
            )
        except Exception as e:
            st.error(f"Error loading tournaments: {e}")
            return
    
    with col2:
        # Opponent name input
        opponent = st.text_input(
            "Opponent Name",
            value=st.session_state.match_info["opponent"] if st.session_state.match_info["opponent"] else ""
        )
    
    # Update session state with tournament and opponent
    if tournament_name != st.session_state.match_info["tournament_name"] or opponent != st.session_state.match_info["opponent"]:
        st.session_state.match_info["tournament_name"] = tournament_name
        st.session_state.match_info["opponent"] = opponent
    
    # Display current match info
    st.subheader("Current Match")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Tournament:** {st.session_state.match_info['tournament_name']}")
    with col2:
        st.write(f"**Opponent:** {st.session_state.match_info['opponent']}")
    with col3:
        st.write(f"**Date:** {st.session_state.match_info['date']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Point:** {st.session_state.match_info['point_number']}")
    with col2:
        st.write(f"**Score:** {st.session_state.match_info['score_for']} - {st.session_state.match_info['score_against']}")
    
    # Get tournament roster
    if st.session_state.match_info["tournament_name"]:
        try:
            roster_df = get_tournament_roster(st.session_state.match_info["tournament_name"])
            if roster_df.empty:
                st.warning(f"No players found for tournament: {st.session_state.match_info['tournament_name']}")
                return
            
            # Form for recording a point
            with st.form(key='record_point_form'):
                st.subheader(f"Select Players for Point {st.session_state.match_info['point_number']}")
                
                # Initialize a list to store player selections
                player_selections = []
                
                # Display each player with selection options
                for index, row in roster_df.iterrows():
                    player_name = row.get('player_name', f"Player {index + 1}")
                    line = row.get('line', "")
                    position = row.get('position', "")
                    
                    # Create a container for each player
                    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                    
                    with col1:
                        selected = st.checkbox(
                            "Select", 
                            key=f"select_player_{player_name}_{st.session_state.match_info['point_number']}"
                        )
                    
                    with col2:
                        st.write(f"**{player_name}**")
                    
                    with col3:
                        st.write(f"Line: {line}")
                    
                    with col4:
                        st.write(f"Position: {position}")
                    
                    # Add player info to selections
                    if selected:
                        player_selections.append({
                            'player_name': player_name,
                            'line': line,
                            'position': position,
                            'selected': selected
                        })
                
                # Point outcome
                st.subheader("Point Outcome")
                col1, col2 = st.columns(2)
                
                with col1:
                    point_scored = st.radio(
                        "Did your team score?",
                        options=["Yes", "No"],
                        horizontal=True
                    )
                
                # Submit button
                submit_button = st.form_submit_button(label='Save Point')
            
            # Process form submission
            if submit_button:
                selected_count = len(player_selections)
                
                if not st.session_state.match_info["opponent"]:
                    st.error("Please enter an opponent name")
                    return
                
                if selected_count != 7:
                    st.error(f"Please select exactly 7 players for the point. You selected {selected_count}")
                    return
                
                # Update scores
                if point_scored == "Yes":
                    st.session_state.match_info["score_for"] += 1
                    point_scored_value = "Yes"  # Changed from boolean to string to match sheet expectations
                else:
                    st.session_state.match_info["score_against"] += 1
                    point_scored_value = "No"  # Changed from boolean to string to match sheet expectations
                
                # Prepare data for the matches sheet
                match_data = []
                for player in player_selections:
                    match_data.append([
                        st.session_state.match_info["tournament_name"],
                        st.session_state.match_info["date"],
                        st.session_state.match_info["opponent"],
                        st.session_state.match_info["point_number"],
                        player['player_name'],
                        player['line'],
                        player['position'],
                        point_scored_value,  # Using the string value now
                        st.session_state.match_info["score_for"],
                        st.session_state.match_info["score_against"],
                        f"{st.session_state.match_info['score_for']}-{st.session_state.match_info['score_against']}"
                    ])
                
                try:
                    success = save_match_data(match_data)
                    if success:
                        st.success(f"Point {st.session_state.match_info['point_number']} recorded successfully")
                        # Increment point number for next point
                        st.session_state.match_info["point_number"] += 1
                        # Force rerun to update the UI
                        st.rerun()
                    else:
                        st.error("Failed to save match data")
                except gspread.exceptions.APIError as e:
                    st.error(f"API Error: {e.response.text}")
                    st.error(f"API Response: {e.response}")  # Add this for more detailed error info
                except Exception as e:
                    st.error(f"Error: {e}")
                
        except Exception as e:
            st.error(f"Error loading tournament roster: {e}")
            return
    
    # Option to start a new match
    if st.button("Start New Match"):
        # Reset match info except for tournament name and opponent
        st.session_state.match_info = {
            "tournament_name": st.session_state.match_info["tournament_name"],
            "opponent": st.session_state.match_info["opponent"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "point_number": 1,
            "score_for": 0,
            "score_against": 0
        }
        st.success("Started new match")
        st.rerun()
