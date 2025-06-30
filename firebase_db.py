# firebase_db.py

import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_user_profile(email, data):
    db.collection("users").document(email).set(data, merge=True)

def save_user_note(email, title, content):
    note = {"title": title, "content": content}
    db.collection("notes").document(email).collection("entries").add(note)

def submit_feedback(email, f_type, message):
    feedback = {"type": f_type, "message": message}
    db.collection("feedback").document(email).collection("entries").add(feedback)
