import json
import ollama
import pandas as pd

PROMPT = """You are reading clinical intake notes. Extract these fields as JSON.
Use null if a field is not mentioned in the notes. Do not guess.
{{"date_of_birth": ..., "sex": ..., "handedness": ..., "relationship_status": ...,
  "medications": list of medication names (empty list if notes say none, null if not mentioned)}}

Notes:
{notes}"""

def extract(notes):
    response = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": PROMPT.format(notes=notes)}],
        format="json",                 # forces valid JSON back
        options={"temperature": 0},    # same answer every run
    )
    return json.loads(response["message"]["content"])



# JSON key from Llama -> field name used in gold.csv
KEY_TO_FIELD = {
    "date_of_birth": "Date of Birth",
    "sex": "Sex",
    "handedness": "Handedness",
    "relationship_status": "Relationship Status",
    "medications": "Medications",
}

def get_notes(transcript_file):
    with open("data/transcripts/" + transcript_file) as f:
        t = json.load(f)
    return t[-1]["content"].split("<STOP>")[0]   # drop the end marker


if __name__ == "__main__":
    gold = pd.read_csv("outputs/gold.csv", dtype=str).fillna("")
    rows = []
    for transcript_file in gold["transcript_file"].unique():
        print("extracting", transcript_file)
        result = extract(get_notes(transcript_file))
        for key, field in KEY_TO_FIELD.items():
            value = result.get(key)
            if isinstance(value, list):            # medications come back as a list
                value = ", ".join(str(v) for v in value)
            rows.append({
                "transcript_file": transcript_file,
                "field": field,
                "extracted_value": "" if value is None else str(value),
            })
    pd.DataFrame(rows).to_csv("outputs/extracted.csv", index=False)
    print("saved outputs/extracted.csv")
