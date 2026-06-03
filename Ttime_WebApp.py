import streamlit as st
import requests
from datetime import datetime

# --- WEB APP SETUP ---
st.set_page_config(page_title="SLC Tee Times", page_icon="⛳")
st.title("⛳ SLC Tee Time Finder")

# --- INTERACTIVE UI CONTROLS ---
target_date = st.date_input("Select a Date")
col1, col2 = st.columns(2)
with col1:
    start_time_input = st.time_input("Earliest Time", value=datetime.strptime("06:00", "%H:%M"))
with col2:
    end_time_input = st.time_input("Latest Time", value=datetime.strptime("18:00", "%H:%M"))

TARGET_DATE = target_date.strftime("%Y-%m-%d")
START_TIME = start_time_input.strftime("%H:%M")
END_TIME = end_time_input.strftime("%H:%M")

# --- THE COURSE LIST (Converted to a Python List) ---
# By making this a real list (using square brackets), we can loop through them one by one.
COURSE_UUIDS_LIST = [
    "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3",  # Bonneville
    "caa8142a-4a42-482b-8d35-4239ce26f7b0",  # Glendale
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

# --- API DETAILS & SECURITY HEADERS ---
URL = "https://www.chronogolf.com/marketplace/v2/teetimes"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.chronogolf.com",
    "Referer": "https://www.chronogolf.com/marketplace",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"'
}

# --- THE SEARCH BUTTON LOGIC ---
if st.button("🔍 Check For Openings", type="primary"):
    
    # We update the spinner text so you know it's working hard!
    with st.spinner("Querying courses one by one to ensure no data is lost..."):
        course_openings = {}
        openings_found = 0
        
        # 1. Loop through each course individually
        for course_id in COURSE_UUIDS_LIST:
            
            # 2. Check up to 2 pages per individual course (plenty for just one location)
            for page_num in range(1, 3):
                PARAMS = {
                    "start_date": TARGET_DATE, 
                    "course_ids": course_id,  # We only send ONE id at a time now
                    "holes": "9,18", 
                    "page": str(page_num) 
                }
                
                try:
                    response = requests.get(URL, headers=HEADERS, params=PARAMS)
                    
                    if response.status_code != 200:
                        break # Skip to the next page/course if this one fails
                    
                    data = response.json()
                    
                    if isinstance(data, dict):
                        tee_time_list = data.get('data', data.get('teetimes', data.get('tee_times', [])))
                    elif isinstance(data, list):
                        tee_time_list = data
                    else:
                        tee_time_list = []
                        
                    if not tee_time_list:
                        break # No more times for this specific course, move to the next course!
                    
                    for item in tee_time_list:
                        raw_time = item.get('start_time') 
                        course_name = item.get('course', {}).get('name', 'Unknown Course')
                        
                        if raw_time:
                            time_part = raw_time.zfill(5)
                            
                            if START_TIME <= time_part <= END_TIME:
                                if course_name not in course_openings:
                                    course_openings[course_name] = []
                                
                                if time_part not in course_openings[course_name]:
                                    course_openings[course_name].append(time_part)
                                    openings_found += 1
                                    
                except Exception as e:
                    # If one course errors out, we don't want the whole app to crash
                    continue 

        # --- DISPLAY RESULTS ---
        if openings_found > 0:
            st.success(f"🎉 Found {openings_found} total tee times matching your filters!")
            
            for course_name, times in course_openings.items():
                times.sort() 
                st.subheader(f"⛳ {course_name}")
                formatted_times = ", ".join(times)
                st.info(f"**Available Slots:** {formatted_times}")
                
        else:
            st.warning(f"❌ No available times found between {START_TIME} and {END_TIME}.")