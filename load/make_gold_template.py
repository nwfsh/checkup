import os
import pandas as pd
from load_data import load_patients

FIELDS = ["Date of Birth", "Sex", "Handedness", "Relationship Status", "Medications"]

# never overwrite labels by accident: delete outputs/gold.csv yourself if you really want a fresh template
if os.path.exists("outputs/gold.csv"):
    raise SystemExit("outputs/gold.csv already exists, not overwriting your labels.")

links = pd.read_csv("outputs/links.csv")
quality = pd.read_csv("outputs/quality.csv")
pairs = links.merge(quality, on="transcript_file")
pairs = pairs[(pairs["status"] == "confirmed") & (~pairs["short"])]

sample = pairs.sample(10, random_state=42)     # same 10 every time you run it
patients = load_patients()

rows = []
for _, p in sample.iterrows():
    for field in FIELDS:
        rows.append({
            "transcript_file": p["transcript_file"],
            "field": field,
            "csv_value": patients.loc[p["row_index"], field],
            "transcript_value": "",   # what the patient said, you fill this in
            "notes_value": "",        # what the notes say, you fill this in
            "label": "",              # CAPTURED / MISSED / INVENTED / WRONG
            "comment": "",
        })
pd.DataFrame(rows).to_csv("outputs/gold.csv", index=False)
