import streamlit as st
import requests
import cloudscraper 
from datetime import datetime
import os

# --- WEB APP SETUP ---
st.set_page_config(page_title="SLC Tee Times", page_icon="⛳", layout="wide")
st.title("⛳ SLC Tee Time Finder")

# ==========================================
# 🤖 BOT COMMAND CENTER (SIDEBAR)
# ==========================================
st.sidebar.header("🤖 Bot Control Center")
st.sidebar.write("Update your GitHub automated bot's hunting parameters.")

with st.sidebar.form("bot_update_form"):
    new_date = st.date_input("Hunt Date")
    new_start = st.time_input("Earliest Time", value=datetime.strptime("06:00", "%H:%M"))
    new_end = st.time_input("Latest Time", value=datetime.strptime("14:00", "%H:%M"))
    new_players = st.selectbox("Party Size", ["1", "2", "3", "4"], index=1)
    
    submit_button = st.form_submit_button("Update GitHub Bot")

if submit_button:
    try:
        # Pull the secure secrets
        gh_token = st.secrets["GITHUB_TOKEN"]
        gh_repo = st.secrets["GITHUB_REPO"]
        
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {gh_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Dictionary mapping GitHub variable names to the new Streamlit inputs
        updates = {
            "TARGET_DATE": new_date.strftime("%Y-%m-%d"),
            "START_TIME": new_start.strftime("%H:%M"),
            "END_TIME": new_end.strftime("%H:%M"),
            "PARTY_SIZE": new_players
        }
        
        with st.spinner("Pushing new coordinates to GitHub..."):
            success_count = 0
            for var_name, var_value in updates.items():
                url = f"https://api.github.com/repos/{gh_repo}/actions/variables/{var_name}"
                payload = {"name": var_name, "value": var_value}
                
                # The PATCH request updates the existing variable
                response = requests.patch(url, json=payload, headers=headers)
                
                if response.status_code == 204:
                    success_count += 1
                else:
                    st.sidebar.
