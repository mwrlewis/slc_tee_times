import streamlit as st
import requests
import cloudscraper 
from datetime import datetime

# --- WEB APP SETUP ---
st.set_page_config(page_title="SLC Tee Times", page_icon="⛳")
st.title("⛳ SLC Tee Time Finder")

# --- THE UNIFIED COURSE CONFIGURATION ---
COURSE_CONFIG = {
    "Bonneville": {
        "uuid": "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3",
        "link": "https://www.chronogolf.com/club/bonneville-golf-course",
        "type": "city"
    },
    "Bonneville (Hole 10 Start)": {
        "uuid": "caa8142a-4a42-482b-8d35-4239ce26f7b0",
        "link": "https://www.chronogolf.com/club/bonneville-golf-course",
        "type": "city"
    },
    "Forest Dale": {
        "uuid": "41ea25ca-ffcb-4f14-a86d-de0ef84510e0",
        "link": "https://www.chronogolf.com/club/forest-dale-golf-course",
        "type": "city"
    },
    "Nibley Park": {
        "uuid": "997cd01f-4ce8-4462-a459-594762efb606",
        "link": "https://www.chronogolf.com/club/nibley-park-golf-course",
        "type": "city"
    },
    "Mountain Dell (Layout 1)": {
        "uuid": "2c162b65-6803-4bad-9a21-4c1ca88bb242",
        "link": "https://www.chronogolf.com/club/mountain-dell-golf-club",
        "type": "city"
    },
    "Mountain Dell (Layout 2)": {
        "uuid": "77dca1a2-edae-47d2-a202-a1e9391cc305",
        "link": "https://www.chronogolf.com/club/mountain-dell-golf-club",
        "type": "city"
    },
    "Mountain Dell (Layout 3)": {
        "uuid": "bd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e",
        "link": "https://www.chronogolf.com/club/mountain-dell-golf-club",
        "type": "city"
    },
    "Glendale": {
        "uuid": "547936f8-0f45-4bea-b557-d15a4de485ad",
        "link": "https://www.chronogolf.com/club/glendale-golf-course",
        "type": "city"
    },
    "Glendale (Hole 10 Start)": {
        "uuid": "4984e272-06a5-446a-8e24-8402e3591b7c",
        "link": "https://www.chronogolf.com/club/glendale-golf-course",
        "type": "city"
    },
    "Rose Park": {
        "uuid": "19a5558e-3821-4935-b6bd-0cbc99693d91",
        "link": "https://www.chronogolf.com/club/rose-park-golf-course",
        "type": "city"
    },
    "Rose Park (Hole 10 Start)": {
        "uuid": "f899015b-2109-4028-8640-d670ada581e4",
        "link": "https://www.chronogolf.com/club/rose-park-golf-course",
        "type": "city"
    },
    "Meadowbrook": {
        "uuid": "c3155ad4-2f72-4b4d-80ec-a3b3c08a89db",
        "link": "https://www.chronogolf.com/club/meadow-brook-slco",
        "type": "city"
    },
    "Old Mill": {
        "uuid": "99cc98d7-03aa-400c-a8b6-c5e5f3665ca4",
        "link": "https://www.chronogolf.com/club/old-mill-slco",
        "type": "county"
    }
}

# --- INTERACTIVE UI CONTROLS ---
target_date = st.date_input("Select a Date")

col1, col2, col3 = st.columns(3)
with col1:
    start_time_input = st.time_input("Earliest Time", value=datetime.strptime("06:00", "%H:%M"))
with col2:
    end_time_input = st.time_input("Latest Time", value=datetime.strptime("18:00", "%H:%M"))
with col3:
    players_input = st.selectbox("Players Wanted", ["1", "2", "3", "4"], index=3) 

# --- THE "SELECT ALL" DROPDOWN LOGIC ---
all_course_names = list(COURSE_CONFIG.keys())
dropdown_options = ["Select All"] + all_course_names

selected_ui_options = st.multiselect(
    "Select Courses to Search",
    options=dropdown_options,
    default=["Select All"]
)

# If "Select All" is in the box, search everything. Otherwise, just search what is picked.
if "Select All" in selected_ui_options:
    selected_courses = all_course_names
else:
    selected_courses = selected_ui_options

TARGET_DATE = target_date.strftime("%Y-%m-%d")
START_TIME = start_time_input.strftime("%H:%M")
END_TIME = end_time_input.strftime("%H:%M")
DESIRED_PARTY_SIZE = int(players_input)

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
    
    # Check if the user completely cleared the box
    if not selected_courses:
        st.warning("⚠️ Please select at least one golf course to run the search.")
    else:
        with st.spinner(f"Scrubbing selected databases for slots fitting exactly {players_input} players..."):
            
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'darwin', 'desktop': True})
            course_openings = {}
            openings_found = 0
            
            for course_name in selected_courses:
                course_info = COURSE_CONFIG[course_name]
                course_id = course_info["uuid"]
                
                # ---------------------------------------------------------
                # COUNTY COURSE ROUTING (Old Mill)
                # ---------------------------------------------------------
                if course_info["type"] == "county":
                    PRIVATE_URL = "https://www.chronogolf.com/marketplace/clubs/14210/teetimes"
                    affiliations = ["57662"] * DESIRED_PARTY_SIZE 
                    
                    PARAMS = {
                        "date": TARGET_DATE,
                        "course_id": "16298",
                        "nb_holes": "18",
                        "affiliation_type_ids[]": affiliations
                    }
                    
                    try:
                        response = scraper.get(PRIVATE_URL, headers=HEADERS, params=PARAMS)
                        if response.status_code != 200:
                            continue 
                        
                        tee_time_list = response.json()
                        if isinstance(tee_time_list, dict):
                            tee_time_list = tee_time_list.get('data', [])
                            
                        for item in tee_time_list:
                            if item.get('out_of_capacity') == True:
                                continue
                                
                            raw_time = item.get('start_time') 
                            
                            if raw_time:
                                time_part = raw_time.zfill(5)
                                
                                if START_TIME <= time_part <= END_TIME:
                                    if course_name not in course_openings:
                                        course_openings[course_name] = {"times": [], "uuid": course_id}
                                    
                                    if time_part not in course_openings[course_name]["times"]:
                                        course_openings[course_name]["times"].append(time_part)
                                        openings_found += 1
                                        
                    except Exception:
                        continue 

                # ---------------------------------------------------------
                # CITY COURSE ROUTING (All Other Locations)
                # ---------------------------------------------------------
                else:
                    for page_num in range(1, 3):
                        PARAMS = {
                            "start_date": TARGET_DATE, 
                            "course_ids": course_id,
                            "holes": "9,18", 
                            "nb_players": players_input, 
                            "page": str(page_num) 
                        }
                        
                        try:
                            response = scraper.get(URL, headers=
