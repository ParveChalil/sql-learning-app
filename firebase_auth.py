import streamlit as st
import pyrebase

firebaseConfig = {
    "apiKey": st.secrets["firebase"]["apiKey"],
    "authDomain": st.secrets["firebase"]["authDomain"],
    "projectId": st.secrets["firebase"]["projectId"],
    "storageBucket": st.secrets["firebase"]["storageBucket"],
    "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
    "appId": st.secrets["firebase"]["appId"],
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

def login():
    st.title("🔐 Welcome to SQL Learning App")

    action = st.radio("Select Action", ["Login", "Sign Up", "Forgot Password"])

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

    if action == "Login":
        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.success("✅ Logged in successfully!")
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token = user['idToken']
                return user
            except Exception as e:
                st.error("❌ Invalid credentials or user not registered.")

    elif action == "Sign Up":
        if st.button("Create Account"):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success("✅ Account created! You can now login.")
            except Exception as e:
                st.error(f"❌ Signup failed. {e}")

    elif action == "Forgot Password":
        if st.button("Send Password Reset Link"):
            try:
                auth.send_password_reset_email(email)
                st.success("📩 Password reset email sent. Check your inbox/spam.")
            except Exception as e:
                st.error("❌ Could not send reset email. Is the email registered?")
