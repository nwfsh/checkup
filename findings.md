## Linking
The data has no patient ID, so transcripts had to be linked to their patient row (ground truth) in the CSV.
Only the April batch was linked 

Rule: transcripts were generated in CSV row order, so the nth transcript by timestamp should be row n. A pair was only kept (confirmed) if:
- the clinician's name appears in the opening message, and
- the patient's full name appears somewhere in the transcript, and
- exactly one of the 1000 rows matches, and it's the expected row.

Limitation: matching is by exact text, not an ID. Names that contain other names (e.g. "Chen Li" / "Chen Liu") could match the wrong row; requiring exactly one match excludes these instead of mislinking them. Spot-checked pairs in the review app on DOB, sex and occupation. ( Have spot checked 10 findings, all correct ) 

Added a cleaning function since 3 of the pairs were unable to match properly.

Through this methodology, was able to product 174 comfirmed pairs,
no data left astray. 

## Ground truth (CSV) problems
Generation of Mr/Mrs stored inside Full name, which is wrong.
Generation of Mr/Mrs stored inside Full name that contradicts sex identified with. 

## Patient model problems
East asian names are not accurately split when generating scripts regarding them explainng their names. 
Eg. "I'm fine with being addressed as Liang Xinyi, but some friends also call me Liang." Liang is actually a surname.
In DM_20250425-180816, The patient leaking step-by-step reasoning instead of answering sex . 

## Interviewer / summarizer problems
In DM_20250425-201459, interviewer is leaking the steps. 

## Formatting quirks (cleaning)
THere are inconsistent quotation marks generated within the script, however does not affect quality of notes.
Notes generated sometimes have spaces between texts but sometimes doesn't, will affect UX quality of notes. 

## Notice on empty fields + made-up substance use
The interviewer asks every patient about nicotine, marijuana and alcohol (question bank), but the CSV has no alcohol or nicotine field. It only has Substance Abuse (just "yes" or empty) and Recreational Drug Usage (sometimes "wine"/"beer", mostly empty).

So when the patient gets asked, there's nothing in the ground truth to answer from, and the patient model makes up a scenario.
- e.g. DM_20250426-080834: "I occasionally drink socially but try to limit my intake due to my health conditions and medication regimen."

Empty also doesn't tell you if it means "none" or "never generated", so these fields can't be cross checked against the CSV. Only the transcript says what the patient claimed.

"None" is also stored inconsistently: Health Supplements uses [] while Allergies / drug fields are left empty. Source truth storage quality isn't great.

Decision: not scoring substance use. Good finding, bad test field.

## Insights on leakage
Leaks cluster: patient leaks occur in 58% of transcripts with an interviewer leak vs 10% without. In transcripts with both, the interviewer usually leaked first (14/22). Possibly one model copying the other's format from the shared conversation; not tested further.

## Decisions
Avoiding embeddings for now since its a small project

Fields : DOB, Sex, Handedness, Relationship Status, Medicaitons
Excluding : Short transcripts ( < 20 messages )
Labels : Invented,

## Pipeline to accelerate 
The paper identifies leaked chain-of-thought ('soft failures') through manual review and lists automated quality checks as future work.
I wrote a simple rule-based flag for the leak markers so these transcripts can be filtered before evaluation.