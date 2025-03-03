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
    Display UI for recording match data, optimized for mobile devices.
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
    
    # Tournament and opponent selection - stacked for mobile
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
    
    # Opponent name input
    opponent = st.text_input(
        "Opponent Name",
        value=st.session_state.match_info["opponent"] if st.session_state.match_info["opponent"] else ""
    )
    
    # Update session state with tournament and opponent
    if tournament_name != st.session_state.match_info["tournament_name"] or opponent != st.session_state.match_info["opponent"]:
        st.session_state.match_info["tournament_name"] = tournament_name
        st.session_state.match_info["opponent"] = opponent
    
    # Display current match info in a compact card
    st.markdown("""
    <style>
    .match-info-card {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .match-score {
        font-size: 18px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"""
        <div class="match-info-card">
            <div class="match-score">{st.session_state.match_info['score_for']} - {st.session_state.match_info['score_against']}</div>
            <p><b>Point:</b> {st.session_state.match_info['point_number']} | 
            <b>Date:</b> {st.session_state.match_info['date']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Get tournament roster
    if st.session_state.match_info["tournament_name"]:
        try:
            roster_df = get_tournament_roster(st.session_state.match_info["tournament_name"])
            if roster_df.empty:
                st.warning(f"No players found for tournament: {st.session_state.match_info['tournament_name']}")
                return
            
            # Form for recording a point
            with st.form(key='record_point_form'):
                st.subheader(f"Point {st.session_state.match_info['point_number']}")
                
                # Group players by line for better organization
                st.markdown("### Select exactly 7 players")
                
                # Create player selection with line info
                all_lines = sorted(roster_df['line'].unique())
                
                # Track selected players across all lines
                selected_player_names = []
                
                # For storing complete player info when selected
                player_selections = []
                
                # Show players grouped by line
                for line in all_lines:
                    with st.expander(f"Line: {line}", expanded=True):
                        line_players = roster_df[roster_df['line'] == line]
                        
                        # Create a multiselect for this line's players
                        line_player_options = []
                        line_player_labels = {}
                        
                        # Create clear labels with position info
                        for _, player in line_players.iterrows():
                            player_name = player.get('player_name', "")
                            position = player.get('position', "")
                            display_name = f"{player_name} ({position})"
                            line_player_options.append(player_name)
                            line_player_labels[player_name] = display_name
                        
                        # Custom format for selectbox options
                        line_selected_players = st.multiselect(
                            f"Select players",
                            options=line_player_options,
                            format_func=lambda x: line_player_labels[x],
                            key=f"line_{line}_players"
                        )
                        
                        # Add selected players to our tracking lists
                        selected_player_names.extend(line_selected_players)
                        
                        # Get complete info for selected players
                        for player_name in line_selected_players:
                            player_info = line_players[line_players['player_name'] == player_name].iloc[0]
                            player_selections.append({
                                'player_name': player_name,
                                'line': player_info['line'],
                                'position': player_info['position'],
                                'selected': True
                            })
                
                # Show counter for selected players
                selected_count = len(selected_player_names)
                st.write(f"**{selected_count}/7** players selected")
                
                # Point outcome - simple UI
                st.markdown("### Point Outcome")
                point_scored = st.radio(
                    "Did your team score?",
                    options=["Yes", "No"],
                    horizontal=True
                )
                
                # Submit button - make it more prominent
                submit_button = st.form_submit_button(label='SAVE POINT', use_container_width=True)
            
            # Show current selection summary outside the form
            if selected_player_names:
                with st.expander("Selected Players", expanded=False):
                    # Create a neat table for selected players
                    st.table(pd.DataFrame([
                        {"Player": p['player_name'], "Line": p['line'], "Position": p['position']}
                        for p in player_selections
                    ]))
            
            # Process form submission
            if submit_button:
                selected_count = len(selected_player_names)
                
                if not st.session_state.match_info["opponent"]:
                    st.error("Please enter an opponent name")
                    return
                
                if selected_count != 7:
                    st.error(f"Please select exactly 7 players for the point. You selected {selected_count}")
                    return
                
                # Update scores
                if point_scored == "Yes":
                    st.session_state.match_info["score_for"] += 1
                    point_scored_value = "Yes"
                else:
                    st.session_state.match_info["score_against"] += 1
                    point_scored_value = "No"
                
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
                        point_scored_value,
                        st.session_state.match_info["score_for"],
                        st.session_state.match_info["score_against"],
                        f"{st.session_state.match_info['score_for']}-{st.session_state.match_info['score_against']}"
                    ])
                
                try:
                    success = save_match_data(match_data)
                    if success:
                        st.success(f"✅ Point {st.session_state.match_info['point_number']} recorded!")
                        # Increment point number for next point
                        st.session_state.match_info["point_number"] += 1
                        # Force rerun to update the UI
                        st.rerun()
                    else:
                        st.error("Failed to save match data")
                except gspread.exceptions.APIError as e:
                    st.error(f"API Error: {e.response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
                
        except Exception as e:
            st.error(f"Error loading tournament roster: {e}")
            return
    
    # Option to start a new match - make button full width
    if st.button("Start New Match", use_container_width=True):
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
