import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes for Search Console
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

# Paths to auth files
TOKEN_PATH = os.getenv("TOKEN_PATH", "token.json")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "credentials.json")
ON_RENDER = os.getenv("RENDER", "false").lower() == "true"

@st.cache_resource(show_spinner=False)
def authenticate_gsc():
    st.write("🔐 Starting Google Search Console authentication...")
    st.write(f"📁 Current working directory: {os.getcwd()}")
    st.write(f"📄 TOKEN_PATH: {TOKEN_PATH}")
    st.write(f"📄 CREDENTIALS_PATH: {CREDENTIALS_PATH}")

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

    # If creds not valid, run auth flow or show error on Render
    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_PATH):
            st.error("❌ credentials.json is missing. Upload it locally or as a secret file on Render.")
            raise FileNotFoundError("credentials.json is missing")

        if ON_RENDER:
            st.error("❌ Token is missing or expired. Please re-authenticate locally and redeploy token.json.")
            raise Exception("Token not valid in Render environment")
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(
                    port=0,
                    open_browser=True,
                    success_message="✅ Auth complete! You can close this tab.",
                    authorization_prompt_message="🔓 Please authorize access in the browser..."
                )

                with open(TOKEN_PATH, 'w') as token_file:
                    token_file.write(creds.to_json())
                st.success("✅ token.json saved locally")

            except Exception as e:
                st.error(f"❌ OAuth flow failed: {e}")
                raise e

    try:
        service = build("searchconsole", "v1", credentials=creds)
        st.success("✅ GSC service initialized")
        return service
    except Exception as e:
        st.error(f"❌ Failed to create GSC service: {e}")
        raise e


def get_verified_sites(service):
    try:
        st.write("📡 Calling service.sites().list()...")
        response = service.sites().list().execute()
        st.json(response)

        sites = [
            site["siteUrl"]
            for site in response.get("siteEntry", [])
            if site.get("permissionLevel") != "siteUnverifiedUser"
        ]
        st.write("🔗 Verified sites:", sites)
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
        rows = response.get("rows", [])

        data = []
        for row in rows:
            data.append({
                "Query": row["keys"][0],
                "Clicks": row["clicks"],
                "Impressions": row["impressions"],
                "CTR": round(row["ctr"] * 100, 2),
                "Position": round(row["position"], 2)
            })

        st.success(f"✅ Retrieved {len(data)} rows from GSC")
        return data

    except Exception as e:
        st.error(f"❌ Failed to fetch query data: {e}")
        return []
