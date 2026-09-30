# checkup
checking if llm generated notes matches to what happens in a clinical interview, whether anything were hallucinated, missed and what were successfully captured 

# data & credits
this project evaluates data from SPIT (Synthetic Patient and Interview Transcript) creator by Warner et al. (2025), UBC Brain Circuits.
- Paper :
Warner A, LeDue J, Cao Y, Tham J and Murphy TH (2025) Synthetic patient and interview transcript creator: an essential tool for LLMs in mental health. Front. Digit. Health 7:1625444. doi: 10.3389/fdgth.2025.1625444
- Code & Data : https://github.com/ubcbraincircuits/SPIT_Generation

data here will not be redistributed, original data exists in original repo 

# results
Summary of what I found: [result.md](result.md). Full notes: [findings.md](findings.md).

# what I'd do next
- Label new held-out transcripts and test the fixed pipeline on them once (so far it was only checked on the same 50 labels used to find its problems)
- Investigate the leakage: whether one model is copying the other's leaked format from the shared conversation
- Investigate what "Separated" is supposed to mean in the CSV
- Look into the notes' wordiness and East Asian name handling

# how to run
python3 load/linking_data.py          # link transcripts to patients → outputs/links.csv
python3 load/transcript_quality.py    # flag leaked reasoning → outputs/quality.csv
python -m streamlit run compare/review_app.py
python3 pipeline/extracted.py         # needs Ollama + llama3.1:8b
python3 pipeline/score.py
