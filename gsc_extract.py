from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd
import datetime

# Auth scope
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

# Load credentials and authenticate
flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)
service = build('searchconsole', 'v1', credentials=creds)

# Set your verified site URL
site_url = 'https://aspenservices.com.au/'  # ← Replace with your actual site from Step 2

# Set date range for data pull (e.g., last 90 days)
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=90)

# Build API request
request = {
    'startDate': start_date.isoformat(),
    'endDate': end_date.isoformat(),
    'dimensions': ['date'],
    'rowLimit': 25000
}


response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()

# Convert response to DataFrame
rows = response.get('rows', [])
data = []
for row in rows:
    keys = row['keys']
    data.append({
        'date': keys[0],
        'clicks': row.get('clicks', 0),
        'impressions': row.get('impressions', 0),
        'ctr': row.get('ctr', 0),
        'position': row.get('position', 0)
    })


df = pd.DataFrame(data)

# Save to Excel
df.to_excel("gsc_data.xlsx", index=False)
print("✅ GSC data saved to gsc_data.xlsx")
