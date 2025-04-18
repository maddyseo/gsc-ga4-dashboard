import streamlit as st
from datetime import date, timedelta
import pandas as pd
from app.gsc_api import authenticate_gsc, get_verified_sites, get_gsc_query_data

def main():
    st.title("🚀 GSC + GA4 Forecasting Dashboard")
    st.write("Pull live data from Google Search Console and export insights!")

    st.subheader("🔐 Connect to Google Search Console")

    if "gsc_service" not in st.session_state:
        if st.button("Authenticate with Google"):
            try:
                service = authenticate_gsc()
                st.session_state["gsc_service"] = service
                st.success("✅ Authenticated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Auth failed: {e}")
        return

    # If authenticated
    st.success("✅ Connected to Google Search Console")
    service = st.session_state["gsc_service"]

    st.info("🎉 Authenticated — pulling site list now...")
    st.write("🔍 Authenticated session keys:", list(st.session_state.keys()))

    st.write("🛠 Fetching verified sites...")
    sites = get_verified_sites(service)
    st.write("🔗 Sites returned:", sites)

    if not sites:
        st.warning("⚠️ No verified sites found. Please check your Search Console access or Google Cloud credentials.")
        return

    site_url = st.selectbox("Choose your verified site", sites)
    start_date = st.date_input("Start date", date.today() - timedelta(days=30))
    end_date = st.date_input("End date", date.today())

    if st.button("Fetch Query Data"):
        with st.spinner("📊 Fetching data..."):
            data = get_gsc_query_data(service, site_url, start_date.isoformat(), end_date.isoformat())
            if data:
                df = pd.DataFrame(data)
                st.success(f"✅ Retrieved {len(df)} rows")
                st.dataframe(df)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", csv, "gsc_data.csv", "text/csv")
            else:
                st.warning("⚠️ No data found for this site and date range.")
