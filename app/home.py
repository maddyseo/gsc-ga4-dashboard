import streamlit as st
import pandas as pd
from datetime import date, timedelta
from app.gsc_api import authenticate_gsc, get_verified_sites, get_gsc_query_data

def main():
    st.title("🚀 GSC + GA4 Forecasting Dashboard")
    st.write("Pull live data from Google Search Console and export insights!")

    st.subheader("🔐 Connect to Google Search Console")

    # Auth
    if "gsc_service" not in st.session_state:
        service = authenticate_gsc()
        st.session_state["gsc_service"] = service
    else:
        service = st.session_state["gsc_service"]
        st.success("✅ Connected to Google Search Console")

    # Site list
    sites = get_verified_sites(service)
    if not sites:
        st.warning("⚠️ No verified sites found. Please make sure your service account has access.")
        return

    site_url = st.selectbox("🌐 Choose your verified site", sites)

    # Date input
    start_date = st.date_input("📅 Start date", date.today() - timedelta(days=30))
    end_date = st.date_input("📅 End date", date.today())

    # Fetch GSC data
    if st.button("Fetch Query Data"):
        with st.spinner("⏳ Fetching data from GSC..."):
            df = get_gsc_query_data(service, site_url, start_date.isoformat(), end_date.isoformat())

        if not df.empty:
            st.success(f"✅ Retrieved {len(df)} rows")

            selected_query = st.selectbox("🔎 Choose a keyword to visualize", df['Query'].unique())
            query_df = df[df['Query'] == selected_query].sort_values("Date")

            # Impressions trend
            st.line_chart(query_df.set_index("Date")[["Impressions"]], use_container_width=True)

            # Clicks trend
            st.line_chart(query_df.set_index("Date")[["Clicks"]], use_container_width=True)

            # Full table & download
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv, "gsc_data.csv", "text/csv")
        else:
            st.warning("⚠️ No data returned from GSC")
