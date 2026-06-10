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
st.sidebar.header("🤖 Bot Command Center")

# 1. POWER SWITCH
st.sidebar.subheader("Master Power Switch")
current_status = st.sidebar.toggle("🤖 Bot Scheduler (Active/Paused)")

if st.sidebar.button("Apply Power State"):
    try:
        cron_key = st.secrets["CRON_API_KEY"]
        job_id = st.secrets["CRON_JOB_ID"]
        headers = {"Authorization": f"Bearer {cron_key}", "Content-Type": "application/json"}
        payload = {"job": {"enabled": current_status}}
        response = requests.patch(f"https://api.cron-job.org/jobs/{job_id}", json=payload, headers=headers)
        if response.status_code == 200:
            st.sidebar.success(f"✅ Bot is now {'enabled' if current_status else 'disabled'}!")
        else:
            st.sidebar.error("Failed to update power state.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# 2. PARAMETER UPDATER
st.sidebar.subheader("Update Hunt Parameters")
with st.sidebar.form("bot_update_form"):
    new_date = st.date_input("Hunt Date")
    new_start = st.time_input("Earliest Time", value=datetime.strptime("06:00", "%H:%M"))
    new_end = st.time_input("Latest Time", value=datetime.strptime("14:00", "%H:%M"))
    new_players = st.selectbox("Party Size", ["1", "2", "3", "4"], index=1)
    submit_button = st.form_submit_button("Update GitHub Bot")

if submit_button:
    try:
        gh_token = st.secrets["GITHUB_TOKEN"]
        gh_repo = st.secrets["GITHUB_REPO"]
        headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {gh_token}", "X-GitHub-Api-Version": "2022-11-28"}
        updates = {
            "TARGET_DATE": new_date.strftime("%Y-%m-%d"),
            "START_TIME": new_start.strftime("%H:%M"),
            "END_TIME": new_end.strftime("%H:%M"),
            "PARTY_SIZE": new_players
        }
        with st.spinner("Pushing new coordinates to GitHub..."):
            for var_name, var_value in updates.items():
                url = f"https://api.github.com/repos/{gh_repo}/actions/variables/{var_name}"
                requests.patch(url, json={"name": var_name, "value": var_value}, headers=headers)
            st.sidebar.success("✅ Bot parameters updated!")
    except Exception as e:
        st.sidebar.error(f"Failed to update GitHub: {e}")

# 3. CONNECTION CHECK
st.sidebar.subheader("System Utilities")
if st.sidebar.button("Check API Status"):
    try:
        cron_key = st.secrets["CRON_API_KEY"]
        headers = {"Authorization": f"Bearer {cron_key}"}
        response = requests.get("https://api.cron-job.org/jobs", headers=headers)
        if response.status_code == 200:
            st.sidebar.success("✅ Connected to Scheduler")
        else:
            st.sidebar.error("❌ Auth Failed (Check Secrets)")
    except Exception as e:
        st.sidebar.error(f"Connection error: {e}")

# ==========================================
# ⛳ LIVE MANUAL SEARCH ENGINE
# ==========================================
COURSE_CONFIG = {
    "Bonneville": {"uuid": "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3", "link": "https://www.chronogolf.com/club/bonneville-golf-course", "type": "city"},
    "Bonneville (Hole 10 Start)": {"uuid": "caa8142a-4a42-482b-8d35-4239ce26f7b0", "link": "https://www.chronogolf.com/club/bonneville-golf-course", "type": "city"},
    "Forest Dale": {"uuid": "41ea25ca-ffcb-4f14-a86d-de0ef84510e0", "link": "https://www.chronogolf.com/club/forest-dale-golf-course", "type": "city"},
    "Nibley Park": {"uuid": "997cd01f-4ce8-4462-a459-594762efb606", "link": "https://www.chronogolf.com/club/nibley-park-golf-course", "type": "city"},
    "Mountain Dell (Layout 1)": {"uuid": "2c162b65-6803-4bad-9a21-4c1ca88bb242", "link": "https://www.chronogolf.com/club/mountain-dell-golf-club", "type": "city"},
    "Mountain Dell (Layout 2)": {"uuid": "77dca1a2-edae-47d2-a202-a1e9391cc305", "link": "https://www.chronogolf.com/club/mountain-dell-golf-club", "type": "city"},
    "Mountain Dell (Layout 3)": {"uuid": "bd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e", "link": "https://www.chronogolf.com/club/mountain-dell-golf-club", "type": "city"},
    "Glendale": {"uuid": "547936f8-0f45-4bea-b557-d15a4de485ad", "link": "https://www.chronogolf.com/club/glendale-golf-course", "type": "city"},
    "Glendale (Hole 10 Start)": {"uuid": "4984e272-06a5-446a-8e24-8402e3591b7c", "link": "https://www.chronogolf.com/club/glendale-golf-course", "type": "city"},
    "Rose Park": {"uuid": "19a5558e-3821-4935-b6bd-0cbc99693d91", "link": "https://www.chronogolf.com/club/rose-park-golf-course", "type": "city"},
    "Rose Park (Hole 10 Start)": {"uuid": "f899015b-2109-4028-8640-d670ada581e4", "link": "https://www.chronogolf.com/club/rose-park-golf-course", "type": "city"},
    "Meadowbrook": {"uuid": "c3155ad4-2f72-4b4d-80ec-a3b3c08a89db", "link": "https://www.chronogolf.com/club/meadow-brook-slco", "type": "city"},
    "Old Mill": {"uuid": "99cc98d7-03aa-400c-a8b6-c5e5f3665ca4", "link": "https://www.chronogolf.com/club/old-mill-slco", "type": "county"}
}

target_date = st.date_input("Live Search Date")
col1, col2, col3 = st.columns(3)
with col1: start = st.time_input("Earliest Time", value=datetime.strptime("06:00", "%H:%M"))
with col2: end = st.time_input("Latest Time", value=datetime.strptime("18:00", "%H:%M"))
with col3: players = st.selectbox
