import json
import glob # find files which names matches  a pattern
import pandas as pd

def load_transcripts(pattern ="data/transcripts/DM_202504*.json"):
    transcripts = {}
    for p in sorted(glob.glob(pattern)):
        with open(p) as f:
            transcripts[p] = json.load(f)

    return transcripts # dict

def load_patients(path = "data/llm_patients_042425.csv"):
    return pd.read_csv(path, sep="|") # dataframe 

if __name__ == "__main__":
    transcripts = load_transcripts()
    patients = load_patients()
    print(len(transcripts), patients.shape)
    print(patients)
    ## 174, (1000, 51), means 174 april transcripts + 1000 patients but only interviewing 174 of them 
    
