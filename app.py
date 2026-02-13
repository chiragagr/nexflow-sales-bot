import streamlit as st
import os
from groq import Groq
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd # Naya mehmaan (Data dikhane ke liye)

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="NexFlow Admin", page_icon="🏭", layout="wide")

# --- 2. AUTHENTICATION (Database Connect) ---
def get_sheet_connection():
    try:
        if "GOOGLE_SHEET_CREDS" not in st.secrets:
            st.error("Secrets not found!")
            return None
        
        creds_dict = st.secrets["GOOGLE_SHEET_CREDS"]
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open("NexFlow_Orders").sheet1
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

# --- 3. SIDEBAR (Login System) ---
st.sidebar.title("🏭 A.P. Polymers")
menu = st.sidebar.radio("Navigation", ["🤖 Sales Bot", "🔐 Admin Panel"])

# --- 4. OPTION A: SALES BOT (Grahak ke liye) ---
if menu == "🤖 Sales Bot":
    st.title("🤖 Smart Sales Manager")
    st.caption("Chat with AI & Book Order")

    # Groq Connection
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except:
        st.error("Groq Key Missing")
        st.stop()

    # Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a helpful sales assistant."}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Pipe ka rate puchiye..."):
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        bot_reply = response.choices[0].message.content
        st.chat_message("assistant").write(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    
    # Order Form (Sidebar mein)
    st.sidebar.markdown("---")
    st.sidebar.header("🛒 Book Order")
    with st.sidebar.form("order_form"):
        name = st.text_input("Name")
        mobile = st.text_input("Mobile")
        req = st.text_input("Requirement")
        amount = st.text_input("Total Amount")
        
        if st.form_submit_button("Confirm Order"):
            sheet = get_sheet_connection()
            if sheet:
                sheet.append_row([str(name), str(mobile), str(req), str(amount)])
                st.success("Order Saved!")
                st.balloons()

# --- 5. OPTION B: ADMIN PANEL (Malik ke liye) ---
elif menu == "🔐 Admin Panel":
    st.title("📊 Owner Dashboard")
    
    # Password Protection
    password = st.sidebar.text_input("Enter Admin Password", type="password")
    
    if password == "12345": # Yahan apna password set karein
        sheet = get_sheet_connection()
        if sheet:
            # Data lana
            data = sheet.get_all_records()
            df = pd.DataFrame(data) # Excel jaisa table banana
            
            # Dashboard Metrics (Bade Numbers)
            col1, col2 = st.columns(2)
            col1.metric("Total Orders", len(df))
            
            # Agar 'Bill Amount' column ho to total sale dikhana (Optional)
            # col2.metric("Total Sales", "₹ 50,000") 
            
            st.markdown("### 📝 Recent Orders")
            st.dataframe(df, use_container_width=True) # Table dikhana
            
            # Download Button
            st.download_button(
                label="📥 Download Excel",
                data=df.to_csv(index=False),
                file_name="orders.csv",
                mime="text/csv"
            )
    elif password:
        st.error("Galat Password! Sirf Malik allowed hai.")
    else:
        st.info("Kripya password dalein.")
