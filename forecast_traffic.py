import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Load GSC data
df = pd.read_excel("gsc_data.xlsx")

# Rename columns to fit Prophet's expected format
df.rename(columns={"date": "ds", "clicks": "y"}, inplace=True)

# Make sure date column is datetime
df['ds'] = pd.to_datetime(df['ds'])

# Initialize and fit model
model = Prophet()
model.fit(df)

# Create a DataFrame for the next 30 days
future = model.make_future_dataframe(periods=30)

# Predict future traffic
forecast = model.predict(future)

# Plot forecast
fig = model.plot(forecast)
plt.title("Forecasted Clicks (Next 30 Days)")
plt.xlabel("Date")
plt.ylabel("Clicks")
plt.tight_layout()
plt.show()