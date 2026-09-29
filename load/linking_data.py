import pandas as pd
from load_data import load_patients, load_transcripts

def find_candidates(transcript, patients):
    # break up the transcript 
    opener = transcript[0]["content"]
    whole_text = " ".join(m["content"] for m in transcript)


    # break up the rows 
    candidates = []
    for j, row in patients.iterrows():
        # check if doctor name is inside 
        clinician_ok = str(row["Clinician Name"]) in opener
        # check if patient name exist inside 
        name_ok = str(row["Full Name"]).strip() in whole_text

        if clinician_ok and name_ok:
            candidates.append(j)
        pass

    return candidates

def link(transcripts, patients):
    records = []
    for i, (path, t) in enumerate(transcripts.items()):
        cands = find_candidates(t, patients)
        if cands == [i]:
            status = "confirmed"
            reason = ""
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