import streamlit as st
import requests
import cloudscraper 
from datetime import datetime

# --- WEB APP SETUP ---
st.set_page_config(page_title="SLC Tee Times", page_icon="⛳")
st.title("⛳ SLC Tee Time Finder")

# --- INTERACTIVE UI CONTROLS ---
target_date = st.date_input("Select a Date")
col1, col2, col3 = st.columns(3)
with col1:
    start_time_input = st.time_input("Earliest Time", value=datetime.strptime("06:00", "%H:%M"))
with col2:
    end_time_input = st.time_input("Latest Time", value=datetime.strptime("18:00", "%H:%M"))
with col3:
    players_input = st.selectbox("Players", ["1", "2", "3", "4"], index=3) 

# --- NEW: THE DEBUG TOGGLE ---
st.divider()
debug_mode = st.toggle("🛠️ Turn On Developer Debug Mode")
st.divider()

TARGET_DATE = target_date.strftime("%Y-%m-%d")
START_TIME = start_time_input.strftime("%H:%M")
END_TIME = end_time_input.strftime("%H:%M")

COURSE_UUIDS_LIST = [
    "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3",  # Bonneville
    "caa8142a-4a42-482b-8d35-4239ce26f7b0",  # Bonneville Hole 10 
] # I shortened the list temporarily just for debugging!

URL = "https://www.chronogolf.com/marketplace/v2/teetimes"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.chronogolf.com",
    "Referer": "https://www.chronogolf.com/marketplace"
}

if st.button("🔍 Check For Openings", type="primary"):
    with st.spinner("Interrogating the Chronogolf API..."):
        
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'darwin', 'desktop': True})
        
        for course_id in COURSE_UUIDS_LIST:
            PARAMS = {
                "start_date": TARGET_DATE, 
                "course_ids": course_id,
                "holes": "9,18", 
                "nb_players": players_input,
                "page": "1" 
            }
            
            try:
                response = scraper.get(URL, headers=HEADERS, params=PARAMS)
                
                if response.status_code == 200:
                    data = response.json()
                    tee_time_list = data.get('data', data.get('teetimes', data.get('tee_times', [])))
                    
                    if tee_time_list:
                        # --- THE TRAP DOOR ---
                        if debug_mode:
                            st.warning("⚠️ DEBUG MODE ACTIVE: Displaying raw data for the very first tee time found.")
                            # This will print the exact dictionary the API sends us
                            st.json(tee_time_list[0])
                            st.stop() # This halts the app completely so we can read it!
                            
            except Exception as e:
                st.error(f"Error: {e}")
                
        if not debug_mode:
            st.info("Turn on Debug Mode to see the raw API data.")
