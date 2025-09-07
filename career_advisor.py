import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv("REACT_APP_GEMINI_API_KEY")

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText"

prompt = """
Provide career advice for a user in these labeled sections:
Career Suggestions, Roadmap, Skill Gap, Learning Resources, Practice Websites, Job Search Platforms.
User Info:
- Age: 25
- Experience: 3 years
- Skills: Python (Intermediate), SQL (Beginner), Machine Learning (Beginner)
- Target Role: Data Scientist
- Education: B.Tech
- Location: Bangalore
"""

payload = {
    "prompt": prompt,
    "temperature": 0.7,
    "max_output_tokens": 1500
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.status_code)
print(response.text)
