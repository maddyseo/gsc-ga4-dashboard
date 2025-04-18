from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
TOKEN_PATH = "token_test.json"

def authenticate():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

    return creds

def list_sites():
    creds = authenticate()
    service = build("searchconsole", "v1", credentials=creds)

    try:
        response = service.sites().list().execute()
        sites = response.get("siteEntry", [])
        print("✅ Verified GSC Sites:")
        for site in sites:
            print(f"🔗 {site['siteUrl']} — Permission: {site['permissionLevel']}")
    except Exception as e:
        print("❌ Error fetching GSC sites:", e)

if __name__ == "__main__":
    list_sites()
