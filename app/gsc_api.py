# app/gsc_api.py

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

def authenticate_gsc():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('searchconsole', 'v1', credentials=creds)
    return service

def get_verified_sites(service):
    site_list = service.sites().list().execute()
    return [site['siteUrl'] for site in site_list['siteEntry']]