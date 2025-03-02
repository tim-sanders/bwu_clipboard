import streamlit as st
from modules.authentication import login_ui, logout_ui
from modules.action_buttons import load_roster_ui
from modules.add_tournament import add_tournament_ui


# Set the browser tab name
st.set_page_config(page_title="Google Sheets Data Viewer")

# Streamlit application
def main():
    st.title("Google Sheets Data Viewer")
    
    # setup session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_ui()
    else:
        add_tournament_ui()
        load_roster_ui()
        # add_random_integer_ui()
        logout_ui()

if __name__ == "__main__":
    main()
