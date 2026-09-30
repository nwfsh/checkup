import pandas as pd

# text that only shows up when a model leaks its hidden steps
INTERVIEWER_MARKERS = ["<END_NOTE>", "**Step"]
PATIENT_MARKERS = ["**Step", "Step 1", "<patient_info>"]

def message_leak(m):
    """Return "interviewer" or "patient" if this one message leaked, otherwise None."""
    text = m["content"]
    if m["role"] == "assistant" and any(k in text for k in INTERVIEWER_MARKERS):
        return "interviewer"
    if m["role"] == "user" and any(k in text for k in PATIENT_MARKERS):
        return "patient"
    return None

def find_leaks(transcript):
    """Return which roles leaked, e.g. {"interviewer": True, "patient": False}."""
    interviewer_leak = False
    patient_leak = False
    for m in transcript[:-1]:          # skip [-1], the final notes
        leak = message_leak(m)
        if leak == "interviewer":
            interviewer_leak = True
        if leak == "patient":
            patient_leak = True
    return {"interviewer": interviewer_leak, "patient": patient_leak}

if __name__ == "__main__":
    # imported here, so the review app can import message_leak without needing load_data on its path
    from load_data import load_transcripts
    transcripts = load_transcripts()
    records = []
    for path, t in transcripts.items():
        leaks = find_leaks(t)
        records.append({
            "transcript_file": path.split("/")[-1],
            "interviewer_leak": leaks["interviewer"],
            "patient_leak": leaks["patient"],
            "short": len(t) < 20,
        })
    quality = pd.DataFrame(records)
    quality.to_csv("outputs/quality.csv", index=False)

    print(quality[["interviewer_leak", "patient_leak", "short"]].sum())
    print("any leak:", (quality["interviewer_leak"] | quality["patient_leak"]).sum())
