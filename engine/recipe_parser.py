import json

# # Will need to figure out a way to have this find the user's game data
docs_path = "scripts/en-US.json"

with open(docs_path, mode="r", encoding="utf-16") as read_file:
    docs_raw = json.load(read_file)

docs_unwrap_intermediate: dict[str, dict] = {}
docs_unwrap: dict[str, dict] = {}

# # TODO: tighten this up into a single loop
for category in docs_raw:
    docs_unwrap_intermediate[category["NativeClass"].split(".")[2].rstrip("'")] = (
        category["Classes"]
    )
    docs_unwrap[category["NativeClass"].split(".")[2].rstrip("'")] = {}
for native_class, class_list in docs_unwrap_intermediate.items():
    for class_dict in docs_unwrap_intermediate[native_class]:
        docs_unwrap[native_class][class_dict["ClassName"]] = class_dict
