import os
import cloudscraper
import requests
from datetime import datetime

# --- CREDENTIALS FROM GITHUB SECRETS ---
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "").strip()

# --- BOT HUNTING PARAMETERS ---
TARGET_DATE = "2026-06-07"     # Must be YYYY-MM-DD format
START_TIME = "09:30"           # Earliest acceptable time
END_TIME = "11:30"             # Latest acceptable time
DESIRED_PARTY_SIZE = 1         # Will filter out slots with fewer available openings!

# --- THE COMPLETE COURSE DICTIONARY ---
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
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.chronogolf.com",
    "Referer": "https://www.chronogolf.com/marketplace"
}

# --- START THE SWEEP ---
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'darwin', 'desktop': True})
found_slots = []

print(f"Starting sweep for {TARGET_DATE} between {START_TIME} and {END_TIME} for {DESIRED_PARTY_SIZE} players...")

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
                print(f"BLOCKED by Cloudflare on {short_name}! Status Code: {response.status_code}")
                break
                
            data = response.json()
            
            if isinstance(data, dict):
                tee_time_list = data.get('data', data.get('teetimes', data.get('tee_times', [])))
            elif isinstance(data, list):
                tee_time_list = data
            else:
                tee_time_list = []
            
            if not tee_time_list:
                if page_num == 1:
                    print(f"Clear connection to {short_name}, but zero times exist on this date.")
                break
                
            for item in tee_time_list:
                max_allowed = item.get('max_player_size', 4)
                if DESIRED_PARTY_SIZE > max_allowed:
                    continue
                    
                raw_time = item.get('start_time')
                if raw_time:
                    time_part = raw_time.zfill(5)
                    if START_TIME <= time_part <= END_TIME:
                        found_slots.append(f"{short_name} {time_part}")
                        
        except Exception as e:
            print(f"Crash on {short_name}: {e}")
            continue

# --- NTFY PUSH NOTIFICATION LOGIC ---
if found_slots:
    unique_slots = list(set(found_slots))
    unique_slots.sort()
    
    # Body text is perfectly fine to have emojis
    msg_body = f"⛳ Openings found for {DESIRED_PARTY_SIZE} players:\n\n" + "\n".join(unique_slots)
    
    try:
        response = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=msg_body.encode('utf-8'),
            headers={
                "Title": "SLC Tee Time Alert!", # <-- The crashing emoji has been removed from the header!
                "Priority": "high",
                "Tags": "golf" # <-- This tag automatically adds the emoji back onto your phone screen!
            }
        )
        print(f"🚀 Success! Push notification sent to your phone.")
        print(msg_body) 
    except Exception as e:
        print(f"❌ Failed to transmit message: {e}")
else:
    print("🛑 Sweep complete. No valid openings match your filter criteria.")
