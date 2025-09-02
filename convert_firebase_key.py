import json

# Replace this with your JSON key file path
json_path = r"C:\Users\DELL\OneDrive\Desktop\skills-advisor\skills-advisor-firebase-adminsdk-fbsvc-8f3131e8fb.json"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

compact_json_str = json.dumps(data)

print("\nCopy everything below (including the braces):\n")
print(compact_json_str)
 
