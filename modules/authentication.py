import streamlit as st

# Function to validate login credentials
def validate_login(username, password):
    """
    Validate login credentials.

    Args:
        username (str): The username entered by the user.
        password (str): The password entered by the user.

    Returns:
        bool: True if the credentials are valid, False otherwise.
    """
    return username == st.secrets["APP_USERNAME"] and password == st.secrets["APP_PASSWORD"]


def login_ui():
    """
    Display the login UI and handle the login process.

    This function creates a login form in the Streamlit app. When the login button is clicked,
    it validates the entered credentials and updates the session state accordingly.
    """
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


def logout_ui():
    """
    Display the logout button and handle the logout process.

    This function creates a logout button in the Streamlit app. When the logout button is clicked,
    it updates the session state to log the user out and displays a success message.
    """
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
        st.rerun()
