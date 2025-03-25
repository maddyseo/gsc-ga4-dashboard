import streamlit as st
from app.gsc_api import authenticate_gsc, get_verified_sites

def main():
    st.title("🚀 GSC + GA4 Forecasting Dashboard")
    st.write("Coming soon: traffic insights, keyword opportunities, and more.")

    st.subheader("🔐 Connect to Google Search Console")

    if st.button("Authenticate with Google"):
        try:
            service = authenticate_gsc()
            st.success("✅ Authentication successful!")

            # Get site list
            sites = get_verified_sites(service)
            selected_site = st.selectbox("Choose a verified site", sites)

            if selected_site:
                st.write(f"You selected: `{selected_site}`")
        except Exception as e:
            st.error(f"❌ Authentication failed: {e}")
