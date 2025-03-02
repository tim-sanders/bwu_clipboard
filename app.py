import streamlit as st
from modules.authentication import login_ui, logout_ui
from modules.action_buttons import load_roster_ui
from modules.add_tournament import add_tournament_ui
# Import additional modules as needed
# from modules.record_match import record_match_ui

# Set the browser tab name
st.set_page_config(page_title="BWU Clipboard", layout="wide")

# Streamlit application
def main():
    st.title("BWU Clipboard")
    
    # Setup session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Record Match"
    
    if not st.session_state.logged_in:
        login_ui()
    else:
        # Sidebar navigation
        with st.sidebar:
            st.title("Navigation")
            
            # Navigation options
            if st.button("Add Tournament", key="nav_add_tournament"):
                st.session_state.current_page = "Add Tournament"
            
            if st.button("Record Match", key="nav_record_match"):
                st.session_state.current_page = "Record Match"
            
            # Add a visual separator
            st.markdown("---")
            
            # Logout button in the sidebar
            logout_ui()
        
        # Content based on navigation selection
        if st.session_state.current_page == "Add Tournament":
            add_tournament_ui()
        
        elif st.session_state.current_page == "Record Match":
            st.header("Record Match")
            st.info("Record match functionality will be implemented here")
            # record_match_ui()  # Uncomment when this function is available

if __name__ == "__main__":
    main()
