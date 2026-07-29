import json
import os
import time
from google import genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("KEY LOADED:", api_key[:8] if api_key else "NOT FOUND")
client = genai.Client(api_key=api_key)

EXTRACTION_PROMPT = """You are analyzing a real SEC 8-K filing disclosing a cybersecurity incident.
Extract the following fields as JSON only, no other text, no markdown fences, no explanation.
If a field is not stated or is too vague to determine, use null — do NOT guess or invent specifics.
{{
  "company": "company name",
  "attack_vector": "one of: ransomware, third_party_vendor, credential_compromise, unknown_unauthorized_access, insider, other, insufficient_data",
  "mitre_attack_technique": "a MITRE ATT&CK technique ID if inferable (e.g. T1486 for ransomware/data encryption), else null",
  "data_compromised": ["list of data types mentioned, e.g. PII, SSN, financial records, health records"],
  "operational_impact": "brief description of business disruption mentioned, or null",
  "attacker_named": "name of threat actor/ransomware group if named, else null",
  "confidence": "high/medium/low — how much concrete detail this filing actually gave vs boilerplate/vague language"
}}
Filing text:
{filing_text}
"""

def clean_html(path):
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text(separator=" ", strip=True)[:15000]

def extract_one(filing_text):
    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=EXTRACTION_PROMPT.format(filing_text=filing_text)
    )
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def dedupe_metadata(metadata):
    """Keep only one entry per unique filing URL — removes true duplicate hits."""
    seen = set()
    unique = []
    for entry in metadata:
        if entry["url"] not in seen:
            seen.add(entry["url"])
            unique.append(entry)
    print(f"Deduped: {len(metadata)} -> {len(unique)} unique filings")
    return unique

def run():
    with open("filings_metadata.json") as f:
        metadata = json.load(f)

    metadata = dedupe_metadata(metadata)

    results = []
    already_done = set()
    if os.path.exists("structured_breaches.json"):
        with open("structured_breaches.json") as f:
            results = json.load(f)
        already_done = {r["source_url"] for r in results}
        print(f"Resuming: {len(results)} already extracted, skipping those.")

    remaining = [e for e in metadata if e["url"] not in already_done]
    print(f"{len(remaining)} filings left to process.\n")

    for entry in remaining:
        try:
            text = clean_html(f"filings_text/{entry['local_file']}")
            extracted = extract_one(text)
            extracted["filed_date"] = entry["filed_date"]
            extracted["source_url"] = entry["url"]
            results.append(extracted)
            print(f"Extracted ({len(results)} total): {extracted.get('company')}")

            # Save after EVERY success — nothing is ever lost on a crash or Ctrl+C
            with open("structured_breaches.json", "w") as f:
                json.dump(results, f, indent=2)

        except Exception as e:
            print(f"FAILED on {entry.get('company')}: {e}")
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("\nHit Gemini's daily quota.")
                print(f"Progress saved: {len(results)} total records in structured_breaches.json")
                print("Rerun this exact script tomorrow — it resumes automatically from here.")
                break

        time.sleep(4)

    print(f"\nDone for now. {len(results)} total unique records saved to structured_breaches.json")

if __name__ == "__main__":
    run()