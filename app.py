import streamlit as st
import os
from groq import Groq

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="NexFlow Sales Bot", page_icon="🤖")

# SECURE WAY: Hum Key ko direct nahi likhenge, hum 'Secrets' se mangenge
try:
    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"],
    )
except:
    st.error("API Key nahi mili! Kripya Secrets set karein.")
    st.stop()

# --- 2. SIDEBAR ---
# ... (Baaki code same rahega) ...
# --- 2. SIDEBAR (Dukaan ka Board) ---
with st.sidebar:
    st.title("🏭 A.P. Polymers")
    st.write("Specialist in PVC & HDPE Pipes")
    st.write("---")
    st.write("📞 Contact: +91-98765-XXXXX")
    st.info("💡 Tip: Ask for '6 inch pipe rate' or 'Bulk discount'")

# --- 3. MAIN CHAT INTERFACE ---
st.title("💬 Automated Sales Manager")
st.caption("Powered by NexFlow AI")

# --- 4. SESSION STATE (Ye AI ki 'Yaad' hai) ---
# Streamlit har baar refresh hota hai, isliye hume history save karni padti hai
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """
            Tumhara naam 'Sales Bot' hai. Tum A.P. Polymers ke liye pipe bechte ho.
            
            Rate List:
            1. 4 Inch PVC Pipe - ₹350 / length
            2. 6 Inch PVC Pipe - ₹550 / length
            3. 20mm HDPE Coil - ₹45 / meter
            
            Rules:
            - Sirf pipes ki baat karo.
            - Agar koi rate puche to list se batao.
            - Agar koi discount maange, to max 5% dena.
            - Hinglish mein baat karo.
        """}
    ]

# --- 5. CHAT DISPLAY (Purani baatein dikhana) ---
# System message (hidden instruction) ko chhod kar baaki sab dikhao
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- 6. USER INPUT & AI RESPONSE ---
if user_input := st.chat_input("Apna sawal yahan likhein..."):
    
    # User ka message screen par dikhao
    st.chat_message("user").write(user_input)
    # Memory mein add karo
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI se jawab mango
    try:
        chat_completion = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile",
        )
        bot_reply = chat_completion.choices[0].message.content
        
        # AI ka message screen par dikhao
        st.chat_message("assistant").write(bot_reply)
        # Memory mein add karo
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Error: {e}")