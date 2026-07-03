import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

# --- GOOGLE GEMINI AI SETUP ---
import google.generativeai as genai

# YAHAN APNI GEMINI API KEY PASTE KAREIN
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)

# --- DATA STORAGE MANAGEMENT ---
DATA_FILE = "local_business_data.csv"

def load_my_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except:
            pass
    return pd.DataFrame(columns=["Customer_Name", "City", "Items_List", "Total_Bill", "Order_Date"])

if 'business_df' not in st.session_state:
    st.session_state.business_df = load_my_data()

if 'item_rows' not in st.session_state:
    st.session_state.item_rows = [{"name": "", "qty": 1, "price": 0.0}]

# --- COMFORTABLE AI BOT LOGIC FOR SPECIFIC EXTRACTION ---
def ask_gemini_advanced(user_query, df):
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "⚠️ Kripya pehle app.py code mein apni Google Gemini API Key set karein!"
    
    # Pura data text format mein AI ko bhejna
    data_text = df.to_string(index=False)
    
    # AI ko sakht nirdesh (System Instruction) dena taaki woh aapke format mein hi jawab de
    system_instruction = f"""
    You are a Smart Business AI Assistant. Below is the sales data of the business:
    {data_text}
    
    The user will ask about a specific product in Hindi, English, or Gujarati (e.g., 'Sarva Aushadhi' or 'Sarva Aushadhi kisne li').
    Your job is to read the data carefully and output a clean, well-formatted table/list.
    
    STRICT RULES FOR YOUR ANSWER:
    1. Filter out ONLY the customers who bought the requested product.
    2. For each matching customer, you must extract and display:
       - Customer Name (कस्टमर का नाम)
       - City (शहर)
       - The SPECIFIC QUANTITY of that requested product only (सिर्फ उस प्रोडक्ट की क्वांटिटी जो मांगा गया है).
       - The Total Bill Amount of that order (उस पूरे बिल का कुल अमाउंट).
    3. If there are other items in their bill, DO NOT count their quantities, but show the Total Bill of that transaction.
    4. Respond in a friendly, easy-to-read Hinglish/Hindi or Gujarati table structure so the user can look at it on a phone screen.
    5. If there's a spelling mistake in the query (e.g., 'sarva ausadi'), understand it smartly using your LLM capability and find the right product.
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([system_instruction, user_query])
        return response.text
    except Exception as e:
        return f"❌ AI Connection Error: {str(e)}"

# Form reset karne ke liye function
def save_and_clear_form():
    c_name = st.session_state.get("form_name", "").strip()
    c_city = st.session_state.get("form_city", "").strip()
    date_val = st.session_state.get("form_date", datetime.now()).strftime("%Y-%m-%d")
    
    valid_items = []
    calculated_total = 0.0
    
    for i in range(len(st.session_state.item_rows)):
        i_name = st.session_state.get(f"item_name_{i}", "").strip()
        i_qty = st.session_state.get(f"item_qty_{i}", 1)
        i_price = st.session_state.get(f"item_price_{i}", 0.0)
        
        if i_name and i_price > 0:
            # Data entry ke samay hi Quantity ko jodna taaki AI use padh sake
            valid_items.append(f"{i_qty} Kilo/Pcs {i_name}")
            calculated_total += i_price

    if c_name and c_city and valid_items:
        items_string = ", ".join(valid_items)
        
        new_row = pd.DataFrame([{
            "Customer_Name": c_name,
            "City": c_city,
            "Items_List": items_string,
            "Total_Bill": float(calculated_total),
            "Order_Date": date_val
        }])
        
        st.session_state.business_df = pd.concat([st.session_state.business_df, new_row], ignore_index=True)
        st.session_state.business_df.to_csv(DATA_FILE, index=False)
        
        st.toast(f"🎉 {c_name} ka ₹{calculated_total} ka bill save ho gaya!", icon="✅")
        
        # Form clear karna
        st.session_state.form_name = ""
        st.session_state.form_city = ""
        st.session_state.item_rows = [{"name": "", "qty": 1, "price": 0.0}]
    else:
        st.error("❌ Kripya saari details sahi se bharein!")

# --- APP INTERFACE ---
st.title("📊 Smart Business Billing Tracker")

menu = ["📝 Naya Bill Upload Karen", "🔍 Search Dashboard"]
choice = st.sidebar.selectbox("Menu Chuniye", menu)

df = st.session_state.business_df

# --- 1. DATA ENTRY SECTION ---
if choice == "📝 Naya Bill Upload Karen":
    st.header("🛍️ Customer Ka Naya Bill Daalein")
    
    st.text_input("👤 Customer Ka Naam", key="form_name")
    st.text_input("📍 Customer Ka Shahar (City)", key="form_city")
    st.date_input("📅 Tarikh (Date)", datetime.now(), key="form_date")
    
    st.subheader("📦 Samaan Ki List (Quantity aur Price Ke Saath)")
    
    running_total = 0.0
    for idx, row in enumerate(st.session_state.item_rows):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.text_input(f"Samaan #{idx+1} Ka Naam", key=f"item_name_{idx}", placeholder="e.g., Sarva Aushadhi")
        with col2:
            st.number_input(f"Qty #{idx+1}", min_value=1, step=1, key=f"item_qty_{idx}")
        with col3:
            price_val = st.number_input(f"Price (₹) #{idx+1}", min_value=0.0, step=100.0, key=f"item_price_{idx}")
            running_total += price_val
            
    if st.button("➕ Naya Item Jodein"):
        st.session_state.item_rows.append({"name": "", "qty": 1, "price": 0.0})
        st.rerun()

    st.markdown(f"### 💰 Kul Bill Amount: `₹ {running_total:,.2f}`")
    st.button("🚀 Bill Save Karen", on_click=save_and_clear_form)

# --- 2. SEARCH DASHBOARD ---
elif choice == "🔍 Search Dashboard":
    st.header("🧐 Normal Table Search")
    st.write("Yahan aapka normal billing data table dikhega.")
    st.dataframe(df, use_container_width=True)

# --- FLOATING STYLE AI BOT POP-UP (BOTTOM RIGHT SIDEBAR EFFECT) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Live AI Assistant")
open_bot = st.sidebar.checkbox("💬 Open Smart AI Bot", value=True)

if open_bot:
    # Sidebar ke niche ek permanent floating jaisa chat container
    with st.sidebar.container():
        st.write("---")
        st.markdown("#### **🤖 MunimJi AI Bot**")
        st.write("Aap Hindi/Gujarati/English mein kuch bhi pooch sakte hain:")
        
        user_ai_query = st.text_input(
            "Sawaal Likhein:", 
            placeholder="e.g., Sarva Aushadhi kisne kitni li?",
            key="ai_query_input"
        )
        
        if st.button("✨ AI Se Poochein"):
            if user_ai_query:
                with st.spinner("AI Bill Check Kar Raha Hai..."):
                    ai_response = ask_gemini_advanced(user_ai_query, df)
                    st.markdown("---")
                    st.markdown("**🤖 AI Ka Jawab:**")
                    st.write(ai_response)
            else:
                st.warning("Kripya pehle apna sawaal likhein!")
