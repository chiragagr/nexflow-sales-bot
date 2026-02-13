import streamlit as st
import os
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials

# --- 1. SETUP PAGE & SECURITY ---
st.set_page_config(page_title="NexFlow Orders", page_icon="📝")

# Groq Connection
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Groq API Key missing!")
    st.stop()

# --- 2. GOOGLE SHEETS CONNECTION (The Database) ---
def save_to_sheet(name, mobile, requirement, total):
    try:
        # Secrets se JSON data nikalna
        creds_dict = st.secrets["GOOGLE_SHEET_CREDS"]
        
        # Google se connect karna
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Sheet dhundna
        sheet = client.open("NexFlow_Orders").sheet1  # Yahan apni sheet ka naam likhein
        
        # Data add karna
        row = [str(name), str(mobile), str(requirement), str(total)]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False

# --- 3. SIDEBAR (Order Form) ---
with st.sidebar:
    st.header("🛒 Finalize Order")
    st.write("Baat cheet ke baad order yahan confirm karein:")
    
    with st.form("order_form"):
        cust_name = st.text_input("Customer Name")
        cust_mobile = st.text_input("Mobile Number")
        cust_req = st.text_input("Item Required (e.g. 50 pipes)")
        cust_total = st.text_input("Total Amount (₹)")
        
        submitted = st.form_submit_button("✅ Confirm Order")
        
        if submitted:
            if cust_name and cust_mobile:
                st.info("Saving order...")
                if save_to_sheet(cust_name, cust_mobile, cust_req, cust_total):
                    st.success(f"Mubarak ho! {cust_name} ka order save ho gaya!")
                    st.balloons()
            else:
                st.warning("Naam aur Mobile number zaroori hai!")

# --- 4. CHAT BOT LOGIC (Same as before) ---
st.title("🤖 Smart Sales Manager")
st.caption("Chat with AI & Book Order in Sidebar 👉")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful sales assistant."}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

if user_input := st.chat_input("Ask about pipes..."):
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        messages=st.session_state.messages,
        model="llama-3.3-70b-versatile"
    )
    bot_reply = response.choices[0].message.content
    st.chat_message("assistant").write(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
