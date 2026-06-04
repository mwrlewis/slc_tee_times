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
    players_input = st.selectbox("Players Wanted", ["1", "2", "3", "4"], index=3) 

TARGET_DATE = target_date.strftime("%Y-%m-%d")
START_TIME = start_time_input.strftime("%H:%M")
END_TIME = end_time_input.strftime("%H:%M")

DESIRED_PARTY_SIZE = int(players_input)

# --- THE COURSE LIST ---
COURSE_UUIDS_LIST = [
    "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3",  # Bonneville
    "caa8142a-4a42-482b-8d35-4239ce26f7b0",  # Bonneville Hole 10 
    "41ea25ca-ffcb-4f14-a86d-de0ef84510e0",  # Forest Dale
    "997cd01f-4ce8-4462-a459-594762efb606",  # Nibley Park 
    "2c162b65-6803-4bad-9a21-4c1ca88bb242",  # Mountain Dell (Layout 1)
    "77dca1a2-edae-47d2-a202-a1e9391cc305",  # Mountain Dell (Layout 2)
    "bd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e",  # Mountain Dell (Layout 3)
    "547936f8-0f45-4bea-b557-d15a4de485ad",  # Glendale (Main)
    "4984e272-06a5-446a-8e24-8402e3591b7c",  # Glendale (Hole 10)
    "19a5558e-3821-4935-b6bd-0cbc99693d91",  # Rose Park (Main)
    "f899015b-2109-4028-8640-d670ada581e4",  # Rose Park (Hole 10)
    "c3155ad4-2f72-4b4d-80ec-a3b3c08a89db"   # Meadowbrook
]

# --- DIRECT COURSE LINKS ---
COURSE_LINKS = {
    "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3": "https://www.chronogolf.com/club/bonneville-golf-course",
    "caa8142a-4a42-482b-8d35-4239ce26f7b0": "https://www.chronogolf.com/club/bonneville-golf-course",
    "41ea25ca-ffcb-4f14-a86d-de0ef84510e0": "https://www.chronogolf.com/club/forest-dale-golf-course",
    "997cd01f-4ce8-4462-a459-594762efb606": "https://www.chronogolf.com/club/nibley-park-golf-course",
    "2c162b65-6803-4bad-9a21-4c1ca88bb242": "https://www.chronogolf.com/club/mountain-dell-golf-club",
    "77dca1a2-edae-47d2-a202-a1e9391cc305": "https://www.chronogolf.com/club/mountain-dell-golf-club",
    "bd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e": "https://www.chronogolf.com/club/mountain-dell-golf-club",
    "547936f8-0f45-4bea-b557-d15a4de485ad": "https://www.chronogolf.com/club/glendale-golf-course", 
    "4984e272-06a5-446a-8e24-8402e3591b7c": "https://www.chronogolf.com/club/glendale-golf-course", 
    "19a5558e-3821-4935-b6bd-0cbc99693d91": "https://www.chronogolf.com/club/rose-park-golf-course",
    "f899015b-2109-4028-8640-d670ada581e4": "https://www.chronogolf.com/club/rose-park-golf-course",
    "c3155ad4-2f72-4b4d-80ec-a3b3c08a89db": "https://www.chronogolf.com/club/meadow-brook-slco", # Meadowbrook Link!
}

URL = "
