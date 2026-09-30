import re
import pandas as pd


def norm_date(text):
    try:
        return pd.to_datetime(text.strip(" ."), errors="raise").date()
    except (ValueError, TypeError):
        return text.strip().lower()          # couldn't parse: compare as text

def norm_sex(text):
    t = text.lower()
    if "female" in t or "woman" in t:        # check female first, "male" is inside "female"
        return "female"
    if "male" in t or "man" in t:
        return "male"
    return t

def norm_hand(text):
    t = text.lower()
    if "ambi" in t or "both" in t:
        return "ambidextrous"
    if "left" in t:
        return "left"
    if "right" in t:
        return "right"
    return t

def norm_relationship(text):
    t = text.lower()
    # order matters: "separated" and "common-law" texts can also contain "married"/"relationship"
    for key, value in [("common", "common-law"), ("divorc", "divorced"), ("separat", "separated"),
                       ("widow", "widowed"), ("long-term", "long-term"), ("long term", "long-term"),
                       ("married", "married"), ("single", "single")]:
        if key in t:
            return value
    return t

def same_meds(extracted, said):
    # every drug Llama found in the notes must appear in what the patient said
    names = [m.strip().split()[0].lower() for m in extracted.split(",") if m.strip()]
    said = said.lower()
    return all(re.sub(r"[^a-z]", "", n) in said for n in names)

NORMALIZERS = {
    "Date of Birth": norm_date,
    "Sex": norm_sex,
    "Handedness": norm_hand,
    "Relationship Status": norm_relationship,
}

def same(field, extracted, said):
    if field == "Medications":
        return same_meds(extracted, said)
    norm = NORMALIZERS[field]
    return norm(extracted) == norm(said)


def pipeline_label(field, extracted, said):
    extracted, said = extracted.strip(), said.strip()
    if not extracted and not said:
        return "BOTH EMPTY"
    if not extracted:
        return "MISSED"
    if not said:
        return "INVENTED"
    return "CAPTURED" if same(field, extracted, said) else "WRONG"


if __name__ == "__main__":
    gold = pd.read_csv("outputs/gold.csv", dtype=str).fillna("")
    extracted = pd.read_csv("outputs/extracted.csv", dtype=str).fillna("")
    df = gold.merge(extracted, on=["transcript_file", "field"])

    df["pipeline_label"] = [
        pipeline_label(r["field"], r["extracted_value"], r["transcript_value"])
        for _, r in df.iterrows()
    ]
    df["agree"] = df["pipeline_label"] == df["label"]
    df.to_csv("outputs/scored.csv", index=False)

    print(f"agreement: {df['agree'].sum()}/{len(df)}")
    print("\nper field:")
    print(df.groupby("field")["agree"].agg(["sum", "count"]))
    print("\nyour label (rows) vs pipeline label (columns):")
    print(pd.crosstab(df["label"], df["pipeline_label"]))
    print("\ndisagreements:")
    print(df[~df["agree"]][["transcript_file", "field", "label", "pipeline_label",
                            "transcript_value", "extracted_value"]].to_string())
