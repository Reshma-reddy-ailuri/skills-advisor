import os, requests, json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("REACT_APP_GEMINI_API_KEY")

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"

prompt = "Give a short career suggestion for a user with Python and SQL skills."

payload = {
    "prompt": prompt,
    "temperature": 0.7,
    "max_output_tokens": 200
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

res = requests.post(url, headers=headers, data=json.dumps(payload))
print(res.status_code)
print(res.text)
