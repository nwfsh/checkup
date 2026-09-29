import json

with open("data/transcripts/DM_20250426-085818_Interview.json") as f:
    t = json.load(f)

print("number of messages:", len(t))

for i, msg in enumerate(t):
    print(f"\n--- [{i}] {msg['role']} ---")
    print(msg["content"])
