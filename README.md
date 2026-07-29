# Breach Autopsy Engine

Structured, MITRE ATT&CK-mapped threat intelligence extracted from real SEC cybersecurity incident disclosures (Form 8-K, Item 1.05 and Item 8.01).

Since December 2023, the SEC has required public companies to disclose material cybersecurity incidents within four business days of determining materiality. This project turns that raw, legally-worded, inconsistently-formatted disclosure text into a clean, structured, queryable dataset — the kind of threat intelligence that's normally locked behind commercial platforms costing tens of thousands of dollars a year.

## What it does

1. **Collects** real 8-K filings directly from the SEC EDGAR full-text search API (Item 1.05 and Item 8.01 cyber disclosures)
2. **Extracts** structured fields from each filing's raw text using an LLM — attack vector, MITRE ATT&CK technique, data types compromised, operational impact, threat actor (if named), and a confidence score reflecting how much real detail the filing actually gave
3. **Serves** the result as a searchable, sortable dashboard, plus a clean CSV dataset anyone can reuse

## Why this matters

Public cybersecurity disclosures are legally required but written to be as vague as possible ("an unauthorized third party may have accessed certain systems"). Reading them at scale by hand doesn't work. This pipeline handles that ambiguity honestly — flagging low-confidence extractions instead of inventing detail that isn't there — rather than pretending every filing gives a clean answer.

## Key findings

*(Fill this in once your dataset is complete — pull real numbers from the dashboard's stat cards and vector chart. Example structure below.)*

- **X%** of disclosed incidents in this dataset are attributable to ransomware
- **Y%** of filings gave insufficient detail to determine even a basic attack vector — a live measure of how opaque these mandatory disclosures actually are
- Third-party/vendor compromise is the fastest-growing category disclosed in [year]

## Tech stack

- **Data source:** SEC EDGAR full-text search API (`efts.sec.gov`) — free, public, no API key required
- **Extraction:** Google Gemini API (free tier)
- **Processing:** Python, pandas, BeautifulSoup
- **Dashboard:** Flask, vanilla JS

## Screenshots

*(Add 2-3 screenshots here: the dashboard overview, the attack vector chart, one filing entry next to its source)*

## Running it locally

```bash
git clone https://github.com/YOUR-USERNAME/breach-autopsy-engine.git
cd breach-autopsy-engine
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your-key-here
```

Then run the pipeline in order:
```bash
python collector.py          # pull filing metadata from SEC EDGAR
python fetch_documents.py    # download full filing text
python extract.py            # LLM extraction into structured_breaches.json
python build_dataset.py      # convert to breach_dataset.csv
python app.py                # launch the dashboard at localhost:5000
```

## Data & methodology notes

- Filings are deduplicated by source URL — the same incident is sometimes indexed multiple times across Item 1.05 and Item 8.01 searches, or amended via 8-K/A
- Extraction is capped at the first 15,000 characters of each filing to stay within model context limits
- Every field defaults to `null` rather than a guess when the filing doesn't state something explicitly — this is a deliberate choice to avoid the extraction pipeline hallucinating specifics that were never disclosed
- `confidence` reflects how much concrete detail the *filing itself* gave, not the extraction pipeline's certainty — a `low` confidence record means the company's own disclosure was vague, which is itself a finding worth tracking

## Limitations

- Sample size is bounded by how many companies have actually filed under this rule since December 2023 — this is a real constraint of the disclosure regime, not a gap in collection
- LLM extraction, while constrained to avoid invention, can still misclassify ambiguous language — spot-check any finding you plan to cite externally against the linked source filing
- This is not legal or financial advice, and not a substitute for a professional threat intelligence service

## Roadmap

- [ ] Add state AG breach notification data as a second source
- [ ] Trend analysis: mean time-to-disclosure over time
- [ ] Sector-level breakdown (SIC code cross-reference)

## License

MIT — see LICENSE file. Data sourced from public SEC filings; underlying filing text belongs to the originating companies and the SEC.

---

Built by Aaditya Modi — [LinkedIn](#) · [GitHub](#)
