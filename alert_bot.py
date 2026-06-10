import os
import cloudscraper
import requests
from datetime import datetime

# --- CREDENTIALS & PARAMETERS FROM GITHUB ---
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "").strip()
TARGET_DATE = os.environ.get("TARGET_DATE", "2026-06-07")
START_TIME = os.environ.get("START_TIME", "06:00")
END_TIME = os.environ.get("END_TIME", "18:00")
DESIRED_PARTY_SIZE = int(os.environ.get("PARTY_SIZE", 2))

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
    "c3155ad4-2f72-4b4d-80ec-a3b3c08a89db": "Meadowbrk",
    "99cc98d7-03aa-400c-a8b6-c5e5f3665ca4": "OldMill"
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
    
    # ---------------------------------------------------------
    # OLD MILL COUNTY FALLBACK ROUTING
    # ---------------------------------------------------------
    if course_id == "99cc98d7-03aa-400c-a8b6-c5e5f3665ca4":
        try:
            res = scraper.get(
                "https://www.chronogolf.com/marketplace/clubs/14210/teetimes", 
                headers=HEADERS, 
                params={"date": TARGET_DATE}
            )
            if res.status_code == 200:
                data = res.json()
                items = data if isinstance(data, list) else data.get('data', [])
                for item in items:
                    raw_time = item.get('start_time', '')
                    if raw_time and START_TIME <= raw_time.zfill(5) <= END_TIME:
                        found_slots.append(f"{short_name} {raw_time.zfill(5)}")
        except Exception as e:
            print(f"Crash on {short_name}: {e}")
            continue

    # ---------------------------------------------------------
    # CITY COURSES ROUTING
    # ---------------------------------------------------------
    else:
        for page_num in range(1, 3):
            PARAMS = {
                "start_date": TARGET_DATE,
                "course_ids": course_id,
                "holes": "9,18",
                "page": str(page_num)
            }
            try:
                response = scraper.get(URL, headers=HEADERS, params=PARAMS)
                if response.status_code != 200:
                    break
                    
                data = response.json()
                items = data.get('data', data.get('teetimes', [])) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                
                if not items:
                    break
                    
                for item in items:
                    max_allowed = item.get('available_spots', item.get('max_player_size', item.get('spots_available', 4)))
                    if DESIRED_PARTY_SIZE <= max_allowed:
                        raw_time = item.get('start_time', '')
                        if raw_time and START_TIME <= raw_time.zfill(5) <= END_TIME:
                            found_slots.append(f"{short_name} {raw_time.zfill(5)}")
                            
            except Exception as e:
                print(f"Crash on {short_name}: {e}")
                continue

# --- NTFY PUSH NOTIFICATION LOGIC ---
if found_slots:
    unique_slots = list(set(found_slots))
    unique_slots.sort()
    
    msg_body = f"⛳ Openings found for {DESIRED_PARTY_SIZE} players:\n\n" + "\n".join(unique_slots)
    
    try:
        response = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=msg_body.encode('utf-8'),
            headers={
                "Title": f"SLC Tee Time Alert! ({TARGET_DATE})", 
                "Priority": "high",
                "Tags": "golf" 
            }
        )
        print("🚀 Success! Push notification sent to your phone.")
        print(msg_body) 
    except Exception as e:
        print(f"❌ Failed to transmit message: {e}")
else:
    print("🛑 Sweep complete. No valid openings match your filter criteria.")
