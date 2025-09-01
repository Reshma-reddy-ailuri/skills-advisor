import firebase_admin
from firebase_admin import credentials, firestore

# Use the full path as shown in your screenshot (no spaces in folder names, so it's safe)
cred = credentials.Certificate(
    r"C:\Users\DELL\OneDrive\Desktop\skills-advisor\skills-advisor-firebase-adminsdk-fbsvc-8f3131e8fb.json"
)

# Initialize the Firebase app
firebase_admin.initialize_app(cred)

# Get the Firestore client
db = firestore.client()

print("Firestore client initialized successfully.")
 
