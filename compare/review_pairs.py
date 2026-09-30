import json
import pandas as pd
from load.load_data import load_patients, load_transcripts


links = pd.read_csv("data/links.csv")
pd.set_option("display.max_rows", None)
# shortcut to bring out only values of status confirmed 
confirmed = links[links["status"] == "confirmed"]

transcripts = load_transcripts()
patients = load_patients()

for n in range(10):
    # print 10 rows in the dataframe 
    link = confirmed.iloc[n]
    print(link["transcript_file"], link["row_index"])

    t = transcripts["data/transcripts/" + link["transcript_file"]]

    print(t[-1]["content"])
    print(patients.iloc[link["row_index"]])
    