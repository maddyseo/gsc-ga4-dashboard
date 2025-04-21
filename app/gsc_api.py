import os
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CREDENTIALS_PATH = "/etc/secrets/credentials.json"
TOKEN_PATH = "/etc/secrets/token.json"  # Optional fallback

@st.cache_resource(show_spinner="🔐 Authenticating using service account...")
def authenticate_gsc():
    try:
        creds = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        service = build("searchconsole", "v1", credentials=creds)
        st.success("✅ Authenticated with service account")
        return service
    except Exception as e:
        st.error(f"❌ Auth failed: {e}")
        raise e

def get_verified_sites(service):
    try:
        st.write("📡 Fetching your verified sites...")
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

def get_gsc_query_data(service, site_url, start_date, end_date, row_limit=1000):
    try:
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['query', 'date'],
            'rowLimit': row_limit
        }

        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        rows = response.get('rows', [])

        data = []
        for row in rows:
            query = row['keys'][0]
            date = row['keys'][1]
            data.append({
                'Query': query,
                'Date': date,
                'Clicks': row['clicks'],
                'Impressions': row['impressions'],
                'CTR': round(row['ctr'] * 100, 2),
                'Position': round(row['position'], 2)
            })

        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ Failed to retrieve query data: {e}")
        return pd.DataFrame()
