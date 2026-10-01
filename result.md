# Checkup: inspecting SPIT's generated interviews and notes
Building on SPIT (Warner et al. 2025). I inspected the generated transcripts and summary notes against the patient profiles (ground truth) for the April batch. Most of the work was reading and hand-checking the model outputs.

## What I did
- Linked the transcripts to their patient row in the CSV. The data has no patient ID, so the nth transcript by timestamp should be row n; a pair was only kept if the clinician's name and the patient's full name both matched and exactly one row matched. Added a cleaning function since 3 pairs couldn't match properly. Result: 174 confirmed pairs. Spot-checked 10 pairs, all correct.
- Built two viewing apps for easy reviewing and labelling: one to review the notes and transcript against the CSV, one to label each field.
- Wrote a simple rule-based flag for leak markers so these transcripts can be filtered before evaluation.
- Hand-labelled 10 randomly sampled transcripts (seed 42, short ones excluded) × 5 fields = 50 labels, judged against what the patient said in the transcript. If the CSV disagrees, the mismatch goes in the comment.
- Fields: DOB, Sex, Handedness, Relationship Status, Medications. Excluded short transcripts (< 20 messages). Avoided embeddings for now since it's a small project.

## Results (hand labels)
- CAPTURED 47, MISSED 3, INVENTED 0, WRONG 0
- DOB, Sex, Relationship Status: 10/10 captured
- Handedness: 9/10 (1 missed)
- Medications: 8/10 (2 missed), the most clinically important field
- e.g. DM_20250428-012836: patient named Risperdal, Celexa and Prozac; the notes completely missed them.

Small sample, so these are examples of failure types, not rates.

## Findings

### Notes (interviewer / summarizer)
- Notes used more words than needed but did not invent new information: in 6/50 labelled rows they repeated the patient's name or added phrases like "Patient identifies as…". This lengthens notes and costs extra tokens. The errors were omissions (medications) and padding, not hallucination.
- Notes format is inconsistent between transcripts: the same field gets different labels ("Sex:", "Sex identification:", "Sex identified:", "Identified sex:"), and some notes use bullets/headers while others use plain lines.
- In DM_20250425-201459, the interviewer is leaking its steps.

### Patient model
- In DM_20250427-235930 the patient model named completely different medications than the CSV (Lisinopril + Alprazolam; CSV has Olanzapine + Prozac), and the notes then dropped them. This patient had an edge case instruction to describe pills by colour or shape instead of the name, and neither drug appears anywhere in the profile, so the patient model ignored the instruction and named drugs not in its profile. Two stages failed on one patient, which is why notes are judged against the transcript, not the CSV.
- Alcohol and nicotine are meant to live inside the Recreational Drug Usage field (their variables.py lists them as recreational drugs), but that field is empty for 121/174 interviewed patients. A blank could mean "doesn't use" or "wasn't generated", and when it's blank the patient model still describes habits (e.g. DM_20250426-080834: "I occasionally drink socially…"). So substance use answers can't be checked against the profile. Not scoring substance use.
- East Asian names are not accurately split, e.g. "I'm fine with being addressed as Liang Xinyi, but some friends also call me Liang." Liang is actually a surname.
- In DM_20250425-180816, the patient leaks step-by-step reasoning instead of answering sex.

### Leakage Hypothesis 
- Leaks cluster: patient leaks occur in 58% of transcripts with an interviewer leak vs 10% without. In transcripts with both, the interviewer usually leaked first (14/22). Possibly one model copying the other's format from the shared conversation; not tested further.

### Ground truth (CSV)
- Mr/Mrs stored inside Full Name, sometimes contradicting the sex identified with.
- Empty fields don't tell you if they mean "none" or "never generated", and "none" is stored inconsistently (Health Supplements uses [] while Allergies / drug fields are left empty).
- Relationship Status categories aren't defined: "Separated" could mean legally separated from a marriage or a break-up from a long-term relationship. Also misspelled "Widowded".

## Automated check (first run)
The first run of the pipeline (llama3.1:8b + rules) agreed with my labels on 45/50 (untuned).

## Limitations & next steps
No separate test set yet: the same 50 labels were used to find the pipeline's problems, so the first run (45/50, untuned) is the fair number. Fixes (date parsing, excluding supplements from medications) haven't been tested on new data. With more time, I'd label new held-out transcripts, test the fixed pipeline on them once, and expand to harder free-text fields.

- Investigate the leakage further: whether one model is copying the other's leaked format from the shared conversation.
- Investigate what "Separated" is supposed to mean in the CSV, since the patient model mixes up the two meanings.
- Look into the notes' wordiness: how much extra wording (repeated names, "Patient identifies as…") adds to note length and tokens, and whether a stricter note format would reduce it.
- Look into East Asian name handling: whether the models consistently mix up surname and given name.

Details: [findings.md](findings.md)

Code written with help from Claude Code; the inspection, labelling and findings are my own.
