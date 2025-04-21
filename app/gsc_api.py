import os
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
TOKEN_PATH = "token.json" if os.environ.get("RENDER") != "true" else "/etc/secrets/token.json"
CREDENTIALS_PATH = "credentials.json" if os.environ.get("RENDER") != "true" else "/etc/secrets/credentials.json"

@st.cache_resource(show_spinner=False)
def authenticate_gsc():
    st.write("🔐 Starting Google Search Console authentication...")
    st.write(f"📂 Current working directory: {os.getcwd()}")
    st.write(f"📄 TOKEN_PATH: {TOKEN_PATH}")
    st.write(f"📄 CREDENTIALS_PATH: {CREDENTIALS_PATH}")

    creds = None

    # Try loading existing token
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            st.success("✅ Loaded existing token.json")
        except Exception as e:
            st.warning(f"⚠️ Failed to load token.json: {e}")
            creds = None
    else:
        st.warning("⚠️ token.json not found.")

    # If not valid, refresh or re-auth
    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_PATH):
            st.error("❌ credentials.json missing.")
            raise FileNotFoundError("credentials.json not found")

        try:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)

            if os.environ.get("RENDER") == "true":
                st.warning("⚠️ Token invalid. Use the console below to authenticate.")
                creds = flow.run_console()
            else:
                creds = flow.run_local_server(
                    port=0,
                    open_browser=True,
                    success_message="✅ Auth successful",
                    authorization_prompt_message="🔓 Please authorize access..."
                )

            # Save token
            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
            st.success("✅ Token refreshed and saved.")

        except Exception as e:
            st.error(f"❌ Auth failed: {e}")
            raise e

    try:
        service = build("searchconsole", "v1", credentials=creds)
        st.success("✅ Google Search Console connected")
        return service
    except Exception as e:
        st.error(f"❌ Failed to build GSC service: {e}")
        raise e

# ✅ Add these two functions back
def get_verified_sites(service):
    try:
        st.write("📡 Calling service.sites().list()...")
        response = service.sites().list().execute()
        st.json(response)  # Show raw response for debugging

        sites = [
            site['siteUrl']
            for site in response.get("siteEntry", [])
            if site.get("permissionLevel") != "siteUnverifiedUser"
        ]
        st.write("🔗 Verified sites found:", sites)
        return sites

    except Exception as e:
        st.error(f"❌ Error in get_verified_sites: {e}")
        return []

def get_gsc_query_data(service, site_url, start_date, end_date, row_limit=50):
    try:
        st.write(f"📥 Querying GSC data for: {site_url}")
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['query'],
            'rowLimit': row_limit
        }

        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        rows = response.get('rows', [])

        data = []
        for row in rows:
            data.append({
                'Query': row['keys'][0],
                'Clicks': row['clicks'],
                'Impressions': row['impressions'],
                'CTR': round(row['ctr'] * 100, 2),
                'Position': round(row['position'], 2)
            })

        st.success(f"✅ Retrieved {len(data)} rows from GSC")
        return data

    except Exception as e:
        st.error(f"❌ Failed to retrieve query data: {e}")
        return []