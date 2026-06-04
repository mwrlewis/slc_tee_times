import streamlit as st
import requests
import cloudscraper 
from datetime import datetime

# --- WEB APP SETUP ---
st.set_page_config(page_title="SLC Tee Times", page_icon="⛳")
st.title("⛳ SLC Tee Time Finder")

# --- INTERACTIVE UI CONTROLS ---
target_date = st.date_input("Select a Date")

# We updated this to 3 columns to fit the new player dropdown!
col1, col2, col3 = st.columns(3)
with col1:
    start_time_input = st.time_input("Earliest Time", value=datetime.strptime("06:00", "%H:%M"))
with col2:
    end_time_input = st.time_input("Latest Time", value=datetime.strptime("18:00", "%H:%M"))
with col3:
    players_input = st.selectbox("Players", ["1", "2", "3", "4"], index=3) # Defaults to 4

TARGET_DATE = target_date.strftime("%Y-%m-%d")
START_TIME = start_time_input.strftime("%H:%M")
END_TIME = end_time_input.strftime("%H:%M")

# --- THE COURSE LIST ---
COURSE_UUIDS_LIST = [
    "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3",  # Bonneville
    "caa8142a-4a42-482b-8d35-4239ce26f7b0",  # Bonneville Hole 10 
    "41ea25ca-ffcb-4f14-a86d-de0ef84510e0",  # Forest Dale
    "2c162b65-6803-4bad-9a21-4c1ca88bb242",  # Valley Course 1
    "77dca1a2-edae-47d2-a202-a1e9391cc305",  # Valley Course 2
    "bd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e",  # Valley Course 3
    "547936f8-0f45-4bea-b557-d15a4de485ad",  # Valley Course 4
    "4984e272-06a5-446a-8e24-8402e3591b7c",  # Valley Course 5
    "997cd01f-4ce8-4462-a459-594762efb606",  # Valley Course 6
    "19a5558e-3821-4935-b6bd-0cbc99693d91",  # Valley Course 7
    "f899015b-2109-4028-8640-d670ada581e4",  # Valley Course 8
    "c3155ad4-2f72-4b4d-80ec-a3b3c08a89db"   # Valley Course 9
]

# --- DIRECT COURSE LINKS ---
COURSE_LINKS = {
    "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3": "https://www.chronogolf.com/club/bonneville-golf-course",
    "caa8142a-4a42-482b-8d35-4239ce26f7b0": "https://www.chronogolf.com/club/bonneville-golf-course",
    "41ea25ca-ffcb-4f14-a86d-de0ef84510e0": "https://www.chronogolf.com/club/forest-dale-golf-course",
}

URL = "https://www.chronogolf.com/marketplace/v2/teetimes"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.chronogolf.com",
    "Referer": "https://www.chronogolf.com/marketplace"
}

# --- THE SEARCH BUTTON LOGIC ---
if st.button("🔍 Check For Openings", type="primary"):
    with st.spinner(f"Hunting for {players_input}-player tee times..."):
        
        scraper = cloudscraper.create_scraper(browser={
            'browser': 'chrome',
            'platform': 'darwin',
            'desktop': True
        })
        
        course_openings = {}
        openings_found = 0
        
        for course_id in COURSE_UUIDS_LIST:
            for page_num in range(1, 3):
                PARAMS = {
                    "start_date": TARGET_DATE, 
                    "course_ids": course_id,
                    "holes": "9,18", 
                    "size": players_input,  # <--- Added the new parameter here!
                    "page": str(page_num) 
                }
                
                try:
                    response = scraper.get(URL, headers=HEADERS, params=PARAMS)
                    
                    if response.status_code != 200:
                        break 
                    
                    data = response.json()
                    
                    if isinstance(data, dict):
                        tee_time_list = data.get('data', data.get('teetimes', data.get('tee_times', [])))
                    elif isinstance(data, list):
                        tee_time_list = data
                    else:
                        tee_time_list = []
                        
                    if not tee_time_list:
                        break 
                    
                    for item in tee_time_list:
                        raw_time = item.get('start_time') 
                        course_name = item.get('course', {}).get('name', 'Unknown Course')
                        
                        if course_id == "caa8142a-4a42-482b-8d35-4239ce26f7b0":
                            course_name = "Bonneville (Hole 10 Start)"
                            
                        if raw_time:
                            time_part = raw_time.zfill(5)
                            
                            if START_TIME <= time_part <= END_TIME:
                                if course_name not in course_openings:
                                    course_openings[course_name] = {"times": [], "uuid": course_id}
                                
                                if time_part not in course_openings[course_name]["times"]:
                                    course_openings[course_name]["times"].append(time_part)
                                    openings_found += 1
                                    
                except Exception as e:
                    continue 

        # --- DISPLAY RESULTS ---
        if openings_found > 0:
            st.success(f"🎉 Found {openings_found} total tee times matching your filters!")
            
            for course_name, data in course_openings.items():
                times = data["times"]
                course_uuid = data["uuid"]
                
                times.sort() 
                st.subheader(f"⛳ {course_name}")
                formatted_times = ", ".join(times)
                st.info(f"**Available Slots:** {formatted_times}")
                
                if course_uuid in COURSE_LINKS:
                    base_url = COURSE_LINKS[course_uuid]
                    booking_url = f"{base_url}?date={TARGET_DATE}"
                else:
                    booking_url = f"https://www.chronogolf.com/marketplace?date={TARGET_DATE}"
                    
                st.link_button(f"🔗 Book {course_name}", booking_url)
                st.divider()
                
        else:
            st.warning(f"❌ No available times found between {START_TIME} and {END_TIME}.")
