import streamlit as st
from datetime import date, timedelta
import pandas as pd
from app.gsc_api import authenticate_gsc, get_verified_sites, get_gsc_query_data

def main():
    st.title("🚀 GSC + GA4 Forecasting Dashboard")
    st.write("Pull live data from Google Search Console and export insights!")

    st.subheader("🔐 Connect to Google Search Console")
    with st.spinner("Connecting..."):
        try:
            service = authenticate_gsc()
        except Exception as e:
            st.error(f"❌ Failed to authenticate: {e}")
            return

    st.success("✅ Connected to Google Search Console")

    # Fetch and show verified sites
    st.info("📡 Fetching your verified sites...")
    sites = get_verified_sites(service)

    if not sites:
        st.warning("⚠️ No verified sites found. Please make sure your service account has been added in Search Console.")
        return

    site_url = st.selectbox("🌐 Choose your verified site", sites)
    start_date = st.date_input("📅 Start date", date.today() - timedelta(days=30))
    end_date = st.date_input("📅 End date", date.today())

    if st.button("Fetch Query Data"):
        with st.spinner("📊 Querying GSC data..."):
            data = get_gsc_query_data(service, site_url, start_date.isoformat(), end_date.isoformat())
            if data:
                df = pd.DataFrame(data)
                st.success(f"✅ Retrieved {len(df)} rows")
                st.dataframe(df)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", csv, "gsc_data.csv", "text/csv")
            else:
                st.warning("⚠️ No data returned for this date range or site.")