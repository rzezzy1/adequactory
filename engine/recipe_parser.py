import json

# # TODO: figure out a way to have this find the user's game data
docs_path = "scripts/en-US.json"

with open(docs_path, mode="r", encoding="utf-16") as read_file:
    docs_raw = json.load(read_file)

docs_unwrap_intermediate: dict[str, dict] = {}
docs_unwrap: dict[str, dict] = {}

for category in docs_raw:
    category_name = category["NativeClass"].split(".")[2].rstrip("'")
    docs_unwrap_intermediate[category_name] = category["Classes"]
    docs_unwrap[category_name] = {}
    for class_dict in category["Classes"]:
        docs_unwrap[category_name][class_dict["ClassName"]] = class_dict
