import os
import smtplib
from email.message import EmailMessage
import cloudscraper
from datetime import datetime

# --- CREDENTIALS FROM GITHUB SECRETS ---
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
PHONE_GATEWAY = os.environ.get("PHONE_GATEWAY")

# --- BOT HUNTING PARAMETERS (Edit these whenever you want!) ---
TARGET_DATE = "2026-06-06"     # Must be YYYY-MM-DD format
START_TIME = "10:00"           # Earliest acceptable time
END_TIME = "14:30"             # Latest acceptable time
DESIRED_PARTY_SIZE = 4         # Will filter out slots with fewer available openings!

# --- THE COMPLETE COURSE DICTIONARY ---
# Using a dictionary here lets the bot know exactly how to write short names for text alerts
COURSES = {
    "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3": "Bonneville",
    "caa8142a-4a42-482b-8d35-4239ce26f7b0": "Bonn. B9",
    "41ea25ca-ffcb-4f14-a86d-de0ef84510e0": "ForestDale",
    "997cd01f-4ce8-4462-a459-594762efb606": "NibleyPark",
    "2c162b65-6803-4bad-9a21-4c1ca88bb242": "MtnDell L1",
    "77dca1a2-edae-47d2-a202-a1e9391cc305": "MtnDell L2",
    "bd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e": "MtnDell L3",
    "547936f8-0f45-4bea-b557-d15a4de485ad": "Glendale",
    "4984e272-06a5-446a-8e24-8402e3591b7c": "Glendale B9",
    "19a5558e-3821-4935-b6bd-0cbc99693d91": "RosePark",
    "f899015b-2109-4028-8640-d670ada581e4": "RosePark B9",
    "c3155ad4-2f72-4b4d-80ec-a3b3c08a89db": "Meadowbrk"
}

URL = "https://www.chronogolf.com/marketplace/v2/teetimes"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

# --- START THE SWEEP ---
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'darwin', 'desktop': True})
found_slots = []

for course_id, short_name in COURSES.items():
    for page_num in range(1, 3):
        PARAMS = {
            "start_date": TARGET_DATE,
            "course_ids": course_id,
            "holes": "9,18",
            "nb_players": str(DESIRED_PARTY_SIZE),
            "page": str(page_num)
        }
        
        try:
            response = scraper.get(URL, headers=HEADERS, params=PARAMS)
            if response.status_code != 200:
                break
                
            data = response.json()
            tee_time_list = data.get('data', []) if isinstance(data, dict) else []
            
            if not tee_time_list:
                break
                
            for item in tee_time_list:
                # Capacity Check matching our verified Streamlit fix
                max_allowed = item.get('max_player_size', 4)
                if DESIRED_PARTY_SIZE > max_allowed:
                    continue
                    
                raw_time = item.get('start_time')
                if raw_time:
                    time_part = raw_time.zfill(5)
                    # Filter for our specific morning window
                    if START_TIME <= time_part <= END_TIME:
                        found_slots.append(f"{short_name} {time_part}")
                        
        except Exception:
            continue

# --- SMS NOTIFICATION LOGIC ---
if found_slots:
    # Deduplicate and sort times to keep the message neat
    unique_slots = list(set(found_slots))
    unique_slots.sort()
    
    # Construct a highly compacted message body to respect the 160 SMS character limit
    msg_body = f"⛳ Openings found for {DESIRED_PARTY_SIZE}:\n" + "\n".join(unique_slots)
    
    msg = EmailMessage()
    msg.set_content(msg_body)
    msg['Subject'] = "⛳ Alert"
    msg['From'] = SENDER_EMAIL
    msg['To'] = PHONE_GATEWAY

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Success! Alert sent containing {len(unique_slots)} options.")
    except Exception as e:
        print(f"Failed to transmit message: {e}")
else:
    print("Sweep complete. No valid openings match your filter criteria.")
