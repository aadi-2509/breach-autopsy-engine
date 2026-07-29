import pandas as pd

df = pd.read_csv("breach_dataset.csv")

print("=== Attack vector breakdown ===")
print(df["attack_vector"].value_counts())

print("\n=== Confidence levels (disclosure quality) ===")
print(df["confidence"].value_counts())

print("\n=== Filings over time ===")
df["filed_date"] = pd.to_datetime(df["filed_date"])
print(df.groupby(df["filed_date"].dt.to_period("M")).size())