import json

# # Will need to figure out a way to have this find the user's game data
docs_path = "scripts/en-US.json"

with open(docs_path, mode="r", encoding="utf-16") as read_file:
    docs_raw = json.load(read_file)
