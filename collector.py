import requests
import time
import json

HEADERS = {
    "User-Agent": "Aaditya Modi aadityamodi192@gmail.com"  # SEC requires a real identifying header
}

BASE_URL = "https://efts.sec.gov/LATEST/search-index"

def search_filings(query, forms="8-K", date_from="2023-12-18", date_to=None, max_pages=5):
    """
    Query SEC EDGAR full-text search.
    query: phrase to search, e.g. '"Item 1.05"' (quotes = exact phrase match)
    forms: comma-separated form types, e.g. "8-K"
    """
    all_hits = []
    for page in range(max_pages):
        params = {
            "q": query,
            "forms": forms,
            "dateRange": "custom",
            "startdt": date_from,
        }
        if date_to:
            params["enddt"] = date_to
        params["from"] = page * 10  # EDGAR paginates 10 at a time

        resp = requests.get(BASE_URL, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()

        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break
        all_hits.extend(hits)
        time.sleep(0.3)  # be polite to SEC's servers, avoid rate-limit blocks

    return all_hits


if __name__ == "__main__":
    print("Searching for Item 1.05 filings...")
    item_105 = search_filings('"Item 1.05"')
    print(f"Found {len(item_105)} Item 1.05 hits")

    print("Searching for Item 8.01 cybersecurity filings...")
    item_801 = search_filings('"cybersecurity incident"', forms="8-K")
    print(f"Found {len(item_801)} Item 8.01 / cyber-related hits")

    with open("raw_filings.json", "w") as f:
        json.dump({"item_105": item_105, "item_801": item_801}, f, indent=2)

    print("Saved to raw_filings.json")