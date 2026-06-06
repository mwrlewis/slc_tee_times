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
        "uuid": "c3155ad4-
