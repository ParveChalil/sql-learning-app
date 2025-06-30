# sql_learning_app.py

import streamlit as st
from datetime import date
import pandas as pd
import sqlite3
import os
from py_countries_states_cities_database import get_all_countries, get_all_states, get_all_cities
from firebase_auth import login, auth
from firebase_db import save_user_profile, save_user_note, submit_feedback
from razorpay_util import create_payment_order
import streamlit.components.v1 as components

st.set_page_config(
    page_title="SQL Learning Dictionary A–Z",
    page_icon="📘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- LOGIN ----------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    user = login()
    st.stop()
else:
    try:
        auth.get_account_info(st.session_state.id_token)
    except:
        st.error("Session expired. Please log in again.")
        st.session_state.logged_in = False
        st.experimental_rerun()

# ---------------------- PROFILE FORM ----------------------
def user_registration():
    st.subheader("📝 Complete Your Profile")
    countries = get_all_countries()
    country_names = sorted([c.get("name", "") for c in countries])

    with st.form("user_profile_form"):
        full_name = st.text_input("Full Name")
        dob = st.date_input("Date of Birth", min_value=date(1947, 12, 1), max_value=date.today())
        selected_country = st.selectbox("🌍 Country", ["Select Country"] + country_names)

        selected_state = selected_city = ""
        country_code = state_code = ""
        state_names = city_names = []

        if selected_country != "Select Country":
            country_code = next((c.get("iso2") for c in countries if c.get("name") == selected_country), "")
            states = [s for s in get_all_states() if s.get("countryCode") == country_code]
            state_names = sorted([s["name"] for s in states if s.get("name")])

            if state_names:
                selected_state = st.selectbox("🏷️ State", ["Select State"] + state_names)

                if selected_state != "Select State":
                    state_code = next((s.get("iso2") for s in states if s.get("name") == selected_state), "")
                    cities = [c for c in get_all_cities() if c.get("countryCode") == country_code and c.get("stateCode") == state_code]
                    city_names = sorted([c["name"] for c in cities if c.get("name")])

                    if city_names:
                        selected_city = st.selectbox("🌇️ City", ["Select City"] + city_names)

        contact_number = st.text_input("📱 Contact Number")
        role = st.selectbox("You are a:", ["Student", "Working Professional", "Businessman"])
        organization = st.text_input("College / Company Name")
        submit = st.form_submit_button("Submit")

    if submit:
        if full_name and contact_number and selected_state != "Select State":
            user_data = {
                "full_name": full_name,
                "dob": str(dob),
                "country": selected_country,
                "state": selected_state,
                "city": selected_city if selected_city != "Select City" else "",
                "contact": contact_number,
                "role": role,
                "organization": organization,
                "updated_on": str(date.today())
            }
            save_user_profile(st.session_state.user_email, user_data)
            st.success("✅ Profile saved successfully!")
        else:
            st.warning("⚠️ Please complete all required fields.")

user_registration()

# ---------------------- PAYMENT ----------------------
if not st.session_state.get("has_paid"):
    st.subheader("💳 One-Time Payment Required")
    order = create_payment_order(99, "sql-user-access")

    payment_form = f'''
    <style>
    .razorpay-payment-button {{
        background-color: #00CED1;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
        padding: 14px 35px;
    }}
    </style>
    <form>
    <script src="https://checkout.razorpay.com/v1/checkout.js"
            data-key="rzp_test_2Ye6LH82OehWTV"
            data-amount="{order['amount']}"
            data-currency="INR"
            data-order_id="{order['id']}"
            data-buttontext="Pay ₹99"
            data-name="SQL Learning App"
            data-description="One-time access fee"
            data-prefill.name="{st.session_state.get('user_email', '')}"
            data-theme.color="#00CED1">
    </script>
    </form>
    '''
    components.html(payment_form, height=300)

    if st.button("✅ I have paid"):
        st.session_state.has_paid = True
    st.stop()

# ---------------------- MAIN PAGE ----------------------
st.markdown("<h1 style='text-align: center;'>📘️ SQL Learning Dictionary A–Z</h1>", unsafe_allow_html=True)
df = pd.read_excel("SQL_Complete_Dictionary_A_to_Z_V1.xlsx").fillna("")

search_input = st.text_input("🔍 Search Term, SQL Type, or Variation")
if search_input:
    df = df[df.apply(lambda row: search_input.lower() in str(row['Term']).lower() \
                                or search_input.lower() in str(row['Type']).lower() \
                                or search_input.lower() in str(row['variations']).lower(), axis=1)]

st.sidebar.header("🧽 Filter SQL Commands")
type_options = sorted(df['Type'].dropna().unique().tolist())
type_selected = st.sidebar.selectbox("Select SQL Type", ["ALL"] + type_options)
filtered_df = df if type_selected == "ALL" else df[df['Type'] == type_selected]

term_options = sorted(filtered_df['Term'].dropna().unique())
term_selected = st.sidebar.selectbox("Select Term", term_options)
term_df = filtered_df[filtered_df['Term'] == term_selected]

variation_options = sorted(term_df['variations'].dropna().unique())
variation_selected = st.sidebar.selectbox("Select Variation", ["ALL"] + variation_options)
final_df = term_df if variation_selected == "ALL" else term_df[term_df['variations'] == variation_selected]

if final_df.empty:
    st.warning("No results found.")
else:
    for _, row in final_df.iterrows():
        st.subheader(f"📌 {row['Term']} - {row['variations']}")
        st.markdown(f"**Definition:** {row['Definition']}")
        st.markdown(f"**Use Case:** {row['Use Case']}")
        st.info(f"**Remarks**\n\n1: {row['Remark 1']}\n\n2: {row['Remark 2']}")
        st.markdown("**General Code:**")
        st.code(row['Code'], language='sql')
        st.markdown("**Example:**")
        st.code(row['Example'], language='sql')

# ---------------------- SQL PRACTICE AREA ----------------------
st.markdown("---")
st.header("🧪 Practice SQL Here (In-Memory)")
conn = sqlite3.connect("sql_practice.db")

st.markdown("#### 📁 Upload Your Own Table (Max 200MB)")
uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
user_tables = []
if uploaded and uploaded.size < 200 * 1024 * 1024:
    try:
        user_df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        table_name = os.path.splitext(uploaded.name)[0].replace(" ", "_")
        user_df.to_sql(table_name, conn, if_exists='replace', index=False)
        st.success(f"✅ Uploaded `{table_name}` with {user_df.shape[0]} rows.")
        user_tables.append(table_name)
    except Exception as e:
        st.error(f"❌ Upload failed: {e}")

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
all_tables = [t[0] for t in cursor.fetchall()]
tables_to_show = user_tables + [t for t in all_tables if t not in user_tables]
selected_table = st.selectbox("📋 Select Table", options=tables_to_show)
if selected_table:
    schema = pd.read_sql_query(f"PRAGMA table_info({selected_table});", conn)
    row_count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {selected_table}", conn)['cnt'].iloc[0]
    st.markdown(f"**Schema for `{selected_table}` (Rows: {row_count})**")
    st.dataframe(schema)

query = st.text_area("SQL Editor", height=150)
if st.button("▶️ Run SQL"):
    try:
        result = pd.read_sql_query(query, conn)
        st.success("✅ Query executed successfully!")
        st.dataframe(result)
    except Exception as e:
        st.error(f"❌ Error: {e}")
conn.close()

# ---------------------- NOTES + FEEDBACK ----------------------
with st.expander("📝 Take Notes"):
    title = st.text_input("Note Title")
    content = st.text_area("Note Content")
    if st.button("📅 Save Note"):
        if title and content:
            save_user_note(st.session_state.user_email, title, content)
            st.success("Note saved!")
        else:
            st.warning("Please fill both fields.")

with st.expander("📢 Suggestions or Complaints"):
    f_type = st.selectbox("Select Type", ["Suggestion", "Correction Needed", "Complaint"])
    msg = st.text_area("Your Message")
    if st.button("📨 Submit Feedback"):
        if msg:
            submit_feedback(st.session_state.user_email, f_type, msg)
            st.success("✅ Sent to Admin!")
        else:
            st.warning("Message can't be empty.")

if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()
