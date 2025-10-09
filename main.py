import time
from api_client import fetch_all_jobs
from utils import save_to_csv, save_to_json

def run_scraper():
    print("[INFO] Mulai scraping MagangHub API...")
    jobs = fetch_all_jobs(limit_total=None, per_page=20)
    if jobs:
        save_to_csv(jobs, "data/maganghub_jobs.csv")
        save_to_json(jobs, "data/maganghub_jobs.json")
    else:
        print("[WARN] Tidak ada data ditemukan!")

if __name__ == "__main__":
    while True:
        run_scraper()
        print("[INFO] Sleeping 1 hour before next update...")
        time.sleep(3600)  # 3600 detik = 1 jam
