from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the scope for read-only access to GSC
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

# Authenticate using credentials.json
flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

# Build the service
service = build('searchconsole', 'v1', credentials=creds)

# List all verified site URLs
site_list = service.sites().list().execute()
for site in site_list['siteEntry']:
    print(site['siteUrl'])