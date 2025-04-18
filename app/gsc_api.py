import os
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
TOKEN_PATH = "token.json"

@st.cache_resource(show_spinner=False)
def authenticate_gsc():
    st.write("🔐 Starting Google Search Console authentication...")
    print(">>> Starting GSC OAuth flow")

    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        print("✅ Loaded credentials from token.json")

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(
            port=0,
            open_browser=True,
            success_message="✅ Auth complete! You can close this tab.",
            authorization_prompt_message="Click 'Allow' and return here."
        )

        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
        print("✅ Token saved to token.json")

    service = build("searchconsole", "v1", credentials=creds)
    print("✅ GSC service built successfully")
    st.write("✅ Connected to Google Search Console")
    return service

def get_verified_sites(service):
    try:
        st.write("📡 Calling service.sites().list()...")  # Visual log
        response = service.sites().list().execute()
        st.json(response)  # Dump full response

        sites = [
            site['siteUrl']
            for site in response.get("siteEntry", [])
            if site.get("permissionLevel") != "siteUnverifiedUser"
        ]
        st.write("🔗 Filtered verified sites:", sites)
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

        st.write(f"✅ Retrieved {len(data)} rows from GSC")
        return data

    except Exception as e:
        print("❌ Error fetching query data:", e)
        st.error("❌ Failed to retrieve query data")
        return []