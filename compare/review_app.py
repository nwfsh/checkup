import streamlit as st
import pandas as pd
from load.load_data import load_patients, load_transcripts

# fields to compare against the notes (what we'll eventually score)
FIELDS = [
    "Full Name", "Age", "Date of Birth", "Sex", "Handedness",
    "Relationship Status", "Children", "Occupation",
    "Medical Conditions", "Medications", "Allergies",
    "Substance Abuse", "Recreational Drug Usage",
]

# fields linking never looked at, used to double-check the pair is the same person
LINK_CHECK_FIELDS = ["Full Name", "Date of Birth", "Sex", "Occupation"]

st.set_page_config(layout="wide")


@st.cache_data
def load_all():
    links = pd.read_csv("data/links.csv")
    confirmed = links[links["status"] == "confirmed"]
    return confirmed, load_patients(), load_transcripts()


def show_csv(row_index, fields):
    # astype(str) because a row mixes numbers (Age) and text, which st.table can't display
    st.table(patients.loc[row_index, fields].astype(str))


confirmed, patients, transcripts = load_all()

st.title("Review linked pairs")

# pick one pair; every tab below shows this same pair
file = st.selectbox("Transcript", confirmed["transcript_file"])
link = confirmed[confirmed["transcript_file"] == file].iloc[0]
t = transcripts["data/transcripts/" + file]
st.caption(f"CSV row {link['row_index']} · {len(t)} messages")

notes_tab, transcript_tab = st.tabs(["CSV vs notes", "CSV vs transcript"])

# main project view: did the notes capture what's true?
with notes_tab:
    left, right = st.columns(2)
    with left:
        st.subheader("Summary notes")
        st.text(t[-1]["content"])
    with right:
        st.subheader("CSV (ground truth)")
        show_csv(link["row_index"], FIELDS)

# link check / tiebreaker: what did the patient actually say?
with transcript_tab:
    left, right = st.columns(2)
    with left:
        st.subheader("Conversation")
        # scrollable box, since some transcripts have 200 messages
        with st.container(height=700):
            # skip [-1], that's the notes, shown in the other tab
            for i, msg in enumerate(t[:-1]):
                speaker = "Patient" if msg["role"] == "user" else "Interviewer"
                st.markdown(f"**[{i}] {speaker}**")
                st.text(msg["content"])
    with right:
        st.subheader("CSV (ground truth)")
        show_csv(link["row_index"], LINK_CHECK_FIELDS)
        with st.expander("All scored fields"):
            show_csv(link["row_index"], FIELDS)
