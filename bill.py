import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
import google.generativeai as genai

# --- GOOGLE GEMINI AI SETUP (SECURE METHOD) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    pass

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

if 'item_count' not in st.session_state:
    st.session_state.item_count = 1

# --- SPACE-FREE SMART MATCH FUNCTION ---
def smart_match(search_query, target_text):
    if not isinstance(target_text, str) or not search_query:
        return False
    clean_query = re.sub(r'\s+', '', search_query).lower()
    clean_target = re.sub(r'\s+', '', target_text).lower()
    return clean_query in clean_target

# Form ko save aur auto-erase karne ka function
def save_and_clear_form():
    c_name = st.session_state.get("form_name", "").strip()
    c_city = st.session_state.get("form_city", "").strip()
    date_val = st.session_state.get("form_date", datetime.now()).strftime("%Y-%m-%d")
    
    valid_items = []
    calculated_total = 0.0
    
    for i in range(st.session_state.item_count):
        i_name = st.session_state.get(f"item_name_{i}", "").strip()
        i_qty = st.session_state.get(f"item_qty_{i}", 1)
        i_price = st.session_state.get(f"item_price_{i}", 0.0)
        
        if i_name and i_price > 0:
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
        
        # --- AUTO ERASE ---
        st.session_state.form_name = ""
        st.session_state.form_city = ""
        for i in range(st.session_state.item_count):
            st.session_state[f"item_name_{i}"] = ""
            st.session_state[f"item_qty_{i}"] = 1
            st.session_state[f"item_price_{i}"] = 0.0
        st.session_state.item_count = 1
    else:
        st.error("❌ Kripya saari details sahi se bharein!")

# --- APP INTERFACE ---
st.title("📊 Smart Business Billing Tracker")

# --- ADVANCED AI CHATBOT LOGIC ---
def ask_gemini_advanced(user_query, df):
    if "GEMINI_API_KEY" not in st.secrets or st.secrets["GEMINI_API_KEY"] == "":
        return "⚠️ Kripya share.streamlit.io ki Settings -> Secrets mein 'GEMINI_API_KEY' daalein!"
    
    data_text = df.to_string(index=False)
    
    system_instruction = f"""
    You are a Smart Business AI Assistant. Below is the sales data of the business:
    {data_text}
    The user will ask about a specific product in Hindi, English, or Gujarati.
    Your job is to output a clean list or table.
    STRICT RULES:
    1. Filter ONLY the customers who bought the requested product.
    2. Display: Customer Name, City, SPECIFIC QUANTITY of requested product only, Total Bill Amount.
    3. Respond in a friendly Hinglish/Hindi or Gujarati table.
    4. Handle spelling mistakes smartly.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([system_instruction, user_query])
        return response.text
    except Exception as e:
        return f"❌ AI Connection Error: {str(e)}"

# --- 🤖 AI BOT MAIN SCREEN PAR SABSE UPAR ---
df = st.session_state.business_df
st.markdown("### 🤖 MunimJi AI Assistant")
st.write("Aap Hindi/Gujarati/English mein kuch bhi pooch sakte hain:")

user_ai_query = st.text_input(
    "Sawaal Likhein:", 
    placeholder="e.g., Sarva Aushadhi kone ketli lidhi chhe?",
    key="main_page_ai_query"
)

if st.button("✨ AI Se Poochein", key="main_page_ai_btn"):
    if user_ai_query:
        with st.spinner("AI Bill Check Kar Raha Hai..."):
            ai_response = ask_gemini_advanced(user_ai_query, df)
            st.markdown("---")
            st.markdown("**🤖 AI Ka Jawab:**")
            st.info(ai_response)
    else:
        st.warning("Kripya pehle apna sawaal likhein!")

st.write("---")

# --- SIDEBAR MENU ---
menu = ["📝 Naya Bill Upload Karen", "🔍 Search Dashboard", "⚙️ Data Modify (Edit / Delete)"]
choice = st.sidebar.selectbox("Menu Chuniye", menu)

# --- 1. DATA ENTRY SECTION ---
if choice == "📝 Naya Bill Upload Karen":
    st.header("🛍️ Customer Ka Naya Bill Daalein")
    st.write("Samaan aur keemat likhein, jod (Total) apne aap live niche ho jayega!")
    
    st.text_input("👤 Customer Ka Naam", key="form_name")
    st.text_input("📍 Customer Ka Shahar (City)", key="form_city")
    st.date_input("📅 Tarikh (Date)", datetime.now(), key="form_date")
    
    st.subheader("📦 Samaan Ki List (Quantity aur Price Ke Saath)")
    
    running_total = 0.0
    for idx in range(st.session_state.item_count):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input(f"Samaan #{idx+1} Ka Naam", key=f"item_name_{idx}", placeholder="e.g., Sarva Aushadhi")
        with col2:
            st.number_input(f"Qty #{idx+1}", min_value=1, step=1, key=f"item_qty_{idx}")
        with col3:
            price_val = st.number_input(f"Price (₹) #{idx+1}", min_value=0.0, step=100.0, key=f"item_price_{idx}")
            running_total += price_val
            
    if st.button("➕ Naya Item Jodein"):
        st.session_state.item_count += 1
        st.rerun()

    st.markdown(f"### 💰 Kul Bill Amount: `₹ {running_total:,.2f}`")
    st.button("🚀 Bill Save Karen", on_click=save_and_clear_form)

# --- 2. TABLE SEARCH DASHBOARD ---
elif choice == "🔍 Search Dashboard":
    st.header("🧐 Normal Table Search")
    if df.empty:
        st.info("⚠️ Abhi app mein koi data nahi hai.")
    else:
        search_name = st.text_input("👤 Customer Ke Naam Se Khojein").strip()
        if search_name:
            mask = df['Customer_Name'].apply(lambda x: smart_match(search_name, x))
            st.dataframe(df[mask][['Order_Date', 'City', 'Total_Bill', 'Items_List']], use_container_width=True)

        search_city = st.text_input("📍 Shahar (City) Ke Hisab Se").strip()
        if search_city:
            mask = df['City'].apply(lambda x: smart_match(search_city, x))
            st.dataframe(df[mask][['Order_Date', 'Customer_Name', 'Total_Bill', 'Items_List']], use_container_width=True)

        search_product = st.text_input("📦 Samaan (Product) Ke Hisab Se").strip()
        if search_product:
            mask = df['Items_List'].apply(lambda x: smart_match(search_product, x))
            st.dataframe(df[mask][['Order_Date', 'Customer_Name', 'City', 'Total_Bill', 'Items_List']], use_container_width=True)

# --- 3. ADVANCED EDIT / DELETE MANAGEMENT ⚙️ ---
elif choice == "⚙️ Data Modify (Edit / Delete)":
    st.header("⚙️ Samaan, Quantity ya Address Badlein")
    
    if df.empty:
        st.info("⚠️ Abhi database khali hai.")
    else:
        bill_options = []
        for index, row in df.iterrows():
            bill_options.append(f"Index {index} | {row['Customer_Name']} ({row['City']}) - ₹{row['Total_Bill']}")
            
        selected_option = st.selectbox("Badalne ke liye Bill Chuniye:", bill_options)
        
        if selected_option:
            selected_index = int(selected_option.split(" | ").split(" "))
            selected_row = df.loc[selected_index]
            
            st.markdown("---")
            st.subheader("📝 Bill Sudharen (Edit Section)")
            
            edit_name = st.text_input("👤 Customer Name (Naam Badlein)", value=selected_row['Customer_Name'])
            edit_city = st.text_input("📍 City / Address (Address Badlein)", value=selected_row['City'])
            edit_date = st.text_input("📅 Date (YYYY-MM-DD)", value=selected_row['Order_Date'])
            
            st.markdown("#### 📦 Samaan aur Quantity Sudharen ya Hatayen:")
            
            raw_items = [i.strip() for i in selected_row['Items_List'].split(",") if i.strip()]
            
            if f"current_items_{selected_index}" not in st.session_state:
                st.session_state[f"current_items_{selected_index}"] = raw_items
            
            updated_items_list = []
            
            for idx, item in enumerate(list(st.session_state[f"current_items_{selected_index}"])):
                match = re.match(r"(\d+)\s+Kilo/Pcs\s+(.*)", item)
                if match:
                    old_qty = int(match.group(1))
                    old_name = match.group(2)
                else:
                    old_qty = 1
                    old_name = item
                
                st.write(f"🔹 **Samaan #{idx+1}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_item_name = st.text_input(f"Naam #{idx+1}", value=old_name, key=f"edit_item_name_{idx}_{selected_index}")
                with col2:
                    new_item_qty = st.number_input(f"Qty #{idx+1}", min_value=1, value=old_qty, key=f"edit_item_qty_{idx}_{selected_index}")
                with col3:
                    st.write("")
                    if st.button("🗑️ Hatayen", key=f"del_item_btn_{idx}_{selected_index}"):
                        st.session_state[f"current_items_{selected_index}"].pop(idx)
                        st.rerun()
