import streamlit as st
import pandas as pd
from load.load_data import load_transcripts
from load.transcript_quality import message_leak

GOLD_PATH = "data/gold.csv"
LABELS = ["CAPTURED", "MISSED", "INVENTED", "WRONG"]

st.set_page_config(layout="wide")


@st.cache_data
def get_transcripts():
    return load_transcripts()

def load_gold():
    # not cached: this file changes every time you save
    # dtype=str + fillna("") so empty cells show as blank boxes, not "nan"
    return pd.read_csv(GOLD_PATH, dtype=str).fillna("")


transcripts = get_transcripts()
gold = load_gold()

st.title("Label gold set")
done = (gold["label"] != "").sum()
st.progress(done / len(gold), text=f"{done}/{len(gold)} rows labeled")

# pick a transcript; show how many of its fields are labeled
files = list(gold["transcript_file"].unique())
def file_status(f):
    rows = gold[gold["transcript_file"] == f]
    return f"{f}  ({(rows['label'] != '').sum()}/{len(rows)})"
file = st.selectbox("Transcript", files, format_func=file_status)
t = transcripts["data/transcripts/" + file]

left, right = st.columns([3, 2])

# left: the two sources you read from
with left:
    notes_tab, convo_tab = st.tabs(["Notes", "Conversation"])
    with notes_tab:
        with st.container(height=650):
            st.text(t[-1]["content"])
    with convo_tab:
        # type a word (e.g. "birth", "medication") to only show messages that contain it
        search = st.text_input("Find in conversation")
        with st.container(height=600):
            for i, msg in enumerate(t[:-1]):
                if search and search.lower() not in msg["content"].lower():
                    continue
                speaker = "Patient" if msg["role"] == "user" else "Interviewer"
                st.markdown(f"**[{i}] {speaker}**")
                if message_leak(msg):
                    st.error(f"leaked reasoning ({message_leak(msg)})")
                st.text(msg["content"])

# right: one block of inputs per field; nothing is saved until you press Save
with right:
    with st.form(f"labels_{file}"):
        rows = gold[gold["transcript_file"] == file]
        new_values = {}
        # scrollable box for the fields; Save stays below it so it's always visible
        with st.container(height=650):
            for idx, row in rows.iterrows():
                st.subheader(row["field"])
                st.caption(f"CSV: {row['csv_value'] or '(empty)'}")
                key = f"{file}_{row['field']}"   # unique per transcript + field
                transcript_value = st.text_input("Patient said", row["transcript_value"], key=key + "_t")
                notes_value = st.text_input("Notes say", row["notes_value"], key=key + "_n")
                label = st.radio(
                    "Label", LABELS, horizontal=True, key=key + "_l",
                    index=LABELS.index(row["label"]) if row["label"] in LABELS else None,
                )
                comment = st.text_input("Comment", row["comment"], key=key + "_c")
                new_values[idx] = (transcript_value, notes_value, label or "", comment)
                st.divider()

        if st.form_submit_button("Save"):
            for idx, (tv, nv, lab, com) in new_values.items():
                gold.loc[idx, ["transcript_value", "notes_value", "label", "comment"]] = [tv, nv, lab, com]
            gold.to_csv(GOLD_PATH, index=False)
            st.success("Saved")
            st.rerun()
