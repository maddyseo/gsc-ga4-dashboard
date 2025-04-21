# app/gsc_api.py
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
SERVICE_ACCOUNT_PATH = "/etc/secrets/service_account.json"

@st.cache_resource(show_spinner=False)
def authenticate_gsc():
    st.write("🔐 Authenticating using service account...")

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_PATH, scopes=SCOPES
        )
        service = build("searchconsole", "v1", credentials=creds)
        st.success("✅ Authenticated with service account")
        return service
    except Exception as e:
        st.error(f"❌ Auth failed: {e}")
        raise e


def get_verified_sites(service):
    try:
        response = service.sites().list().execute()
        sites = [
            site['siteUrl']
            for site in response.get("siteEntry", [])
            if site.get("permissionLevel") != "siteUnverifiedUser"
        ]
        return sites
    except Exception as e:
        st.error(f"❌ Failed to fetch sites: {e}")
        return []


def get_gsc_query_data(service, site_url, start_date, end_date, row_limit=50):
    try:
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['query'],
            'rowLimit': row_limit
        }

        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        rows = response.get('rows', [])
        return [
            {
                'Query': row['keys'][0],
                'Clicks': row['clicks'],
                'Impressions': row['impressions'],
                'CTR': round(row['ctr'] * 100, 2),
                'Position': round(row['position'], 2)
            }
            for row in rows
        ]
    except Exception as e:
        st.error(f"❌ Failed to retrieve data: {e}")
        return []
