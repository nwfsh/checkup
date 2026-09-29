import re
import pandas as pd
from load_data import load_patients, load_transcripts

def clean_name(name):
    # some CSV names have a title or stray punctuation the transcript doesn't, e.g. "Mr. Cezary Bregula", "Pamfil Georgescu,"
    name = str(name).strip()
    name = re.sub(r"^(Mr|Mrs|Ms|Miss|Mx|Dr)\.?\s+", "", name)   # remove a title at the start
    return name.strip(" ,.")                                     # remove stray spaces/commas/periods at the ends

def find_candidates(transcript, patients):
    # break up the transcript 
    opener = transcript[0]["content"]
    whole_text = " ".join(m["content"] for m in transcript)


    # break up the rows 
    candidates = []
    for j, row in patients.iterrows():
        # check if doctor name is inside 
        clinician_ok = clean_name(row["Clinician Name"]) in opener
        # check if patient name exist inside
        name_ok = clean_name(row["Full Name"]) in whole_text

        if clinician_ok and name_ok:
            candidates.append(j)

    return candidates

def link(transcripts, patients):
    records = []
    for i, (path, t) in enumerate(transcripts.items()):
        cands = find_candidates(t, patients)
        if cands == [i]:
            status = "confirmed"
            # flag pairs that only matched because of clean_name, so they stay visible
            raw_name = str(patients.iloc[i]["Full Name"]).strip()
            whole_text = " ".join(m["content"] for m in t)
            if raw_name in whole_text:
                reason = ""
            else:
                reason = "matched after name cleaning"
        else:
            status = "excluded"
            reason = f"expected row {i}, found {cands}"

        records.append({
            "transcript_file": path.split("/")[-1],
            "row_index": i,
            "status": status,   
            "reason": reason,
        })
    return pd.DataFrame(records)

if __name__ == "__main__":
    transcripts = load_transcripts()
    patients = load_patients()
    links = link(transcripts, patients)
    links.to_csv("data/links.csv", index=False)

    print(links["status"].value_counts())
    print(links[links["status"] == "excluded"])
    print(links[links["reason"] == "matched after name cleaning"])