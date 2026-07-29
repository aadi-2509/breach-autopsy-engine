import json
import pandas as pd

with open("structured_breaches.json") as f:
    data = json.load(f)

df = pd.json_normalize(data)
df.to_csv("breach_dataset.csv", index=False)
print(df.head())
print(f"\nSaved {len(df)} rows to breach_dataset.csv")