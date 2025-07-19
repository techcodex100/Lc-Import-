import csv
import os
import time
import datetime
import requests
import psutil

# Constants
INPUT_CSV = "lc_draft_input.csv"  # Ensure this file exists
RENDER_URL = "https://lc-import-1.onrender.com/generate-lc-draft-pdf/"
OUTPUT_DIR = "rendered_lc_draft_pdfs"
MAX_RETRIES = 5
DELAY = 2  # Seconds between requests

# Create output folder
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read CSV and send requests
with open(INPUT_CSV, newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader, start=1):
        success = False
        start_time = time.time()

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(RENDER_URL, json=row)
                if response.status_code == 200:
                    success = True
                    break
                else:
                    print(f"[{i}] ⚠️ Attempt {attempt}: Failed (Status {response.status_code})")
            except Exception as e:
                print(f"[{i}] ❌ Attempt {attempt}: Exception - {e}")
            time.sleep(3)

        if not success:
            print(f"[{i}] ❌ Skipped after {MAX_RETRIES} failed attempts.")
            continue

        # Save PDF
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"lc_draft_{i}_{timestamp}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)

        # Monitoring
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        elapsed = round(time.time() - start_time, 2)

        print(f"✅ [{i}] PDF Saved: {filename}")
        print(f"   CPU: {cpu}% | RAM: {mem}% | Time: {elapsed}s")
        print("-" * 50)

        time.sleep(DELAY)

print("🎉 All LC Draft PDFs processed.")
