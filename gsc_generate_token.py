# gsc_generate_token.py

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES
)

creds = flow.run_local_server(port=0)
print("✅ Authenticated successfully!")

# Save the token
with open('token.json', 'w') as token:
    token.write(creds.to_json())
print("✅ token.json saved in project folder.")
