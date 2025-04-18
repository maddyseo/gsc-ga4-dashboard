import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define scope
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

# Use environment variables with fallback
TOKEN_PATH = os.getenv("TOKEN_PATH", "token.json")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "credentials.json")
ON_RENDER = os.getenv("RENDER", "false").lower() == "true"

@st.cache_resource(show_spinner=False)
def authenticate_gsc():
    st.write("🔐 Starting Google Search Console authentication...")
    st.write(f"📁 Current working directory: {os.getcwd()}")

    creds = None

    # Load token if it exists
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            st.success("✅ Loaded existing token.json")
        except Exception as e:
            st.warning(f"⚠️ Failed to load token.json: {e}")
            creds = None
    else:
        st.warning("⚠️ token.json not found.")

    # If token is not valid, try interactive or fail on Render
    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_PATH):
            st.error("❌ credentials.json is missing. Please upload it.")
            raise FileNotFoundError("credentials.json is missing")

        if ON_RENDER:
            st.error("❌ Token invalid or expired on Render. Please upload a fresh token.json.")
            raise Exception("Token not valid on Render environment")
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(
                    port=0,
                    open_browser=True,
                    success_message="✅ Auth complete! You can close this tab.",
                    authorization_prompt_message="🔓 Authorize access in browser..."
                )

                with open(TOKEN_PATH, 'w') as token_file:
                    token_file.write(cre_
