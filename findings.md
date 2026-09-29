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

## Decisions