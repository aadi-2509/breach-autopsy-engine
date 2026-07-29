import json
import requests
import time
import os

HEADERS = {"User-Agent": "Aaditya Modi aadityamodi192@gmail.com"}

def hit_to_url(hit):
    """Reconstruct the direct URL to the filing document from a search hit."""
    src = hit["_source"]
    cik = str(src["ciks"][0]).lstrip("0")
    accession = hit["_id"].split(":")[0].replace("-", "")
    filename = hit["_id"].split(":")[1]
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{filename}"

def fetch_all(raw_file="raw_filings.json", out_dir="filings_text"):
    os.makedirs(out_dir, exist_ok=True)
    with open(raw_file) as f:
        data = json.load(f)

    all_hits = data["item_105"] + data["item_801"]
    metadata = []

    for i, hit in enumerate(all_hits):
        try:
            url = hit_to_url(hit)
            resp = requests.get(url, headers=HEADERS)
            resp.raise_for_status()

            company = hit["_source"].get("display_names", ["unknown"])[0]
            filed_date = hit["_source"].get("file_date", "unknown")
            safe_name = f"{i}_{company[:30].replace('/', '-')}".replace(" ", "_")

            with open(f"{out_dir}/{safe_name}.html", "w", encoding="utf-8") as out:
                out.write(resp.text)

            metadata.append({
                "index": i,
                "company": company,
                "filed_date": filed_date,
                "url": url,
                "local_file": f"{safe_name}.html"
            })
            print(f"[{i+1}/{len(all_hits)}] Saved: {company}")
            time.sleep(0.3)
        except Exception as e:
            print(f"[{i+1}/{len(all_hits)}] FAILED: {e}")

    with open("filings_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

if __name__ == "__main__":
    fetch_all()