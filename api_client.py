import requests
import time
import random

BASE_URL = "https://maganghub.kemnaker.go.id/be/v1/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MagangScraper/1.0)"
}

def fetch_jobs(page=1, limit=100, order_by="", order_direction="ASC"):
    url = f"{BASE_URL}/list/vacancies-aktif"
    params = {
        "order_by": order_by,
        "order_direction": order_direction,
        "page": page,
        "limit": limit
    }
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_all_jobs(limit_total=None, per_page=100):
    jobs = []
    page = 1

    while True:
        data = fetch_jobs(page=page, limit=per_page)
        items = data.get("data", [])
        if not items:
            break

        jobs.extend(items)
        print(f"[INFO] Page {page}: +{len(items)} jobs, total={len(jobs)}")

        page += 1
        time.sleep(random.uniform(1, 2))

    return jobs

