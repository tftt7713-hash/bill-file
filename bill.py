import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- DATA STORAGE MANAGEMENT ---
# Data ko permanently save rakhne ke liye ek file name
DATA_FILE = "local_business_data.csv"

# Shuruat mein data load karne ke liye function
def load_my_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            return df
        except:
            pass
    # Agar file nahi hai ya khali hai toh naya format banayein
    return pd.DataFrame(columns=["Customer_Name", "City", "Items_List", "Total_Bill", "Order_Date"])

# App ki temporary memory (Session State) ko set karna
if 'business_df' not in st.session_state:
    st.session_state.business_df = load_my_data()

# Form ko erase/clear karne ke liye callback function
def save_and_clear_form():
    # Pehle check karenge ki zaroori details bhari hain ya nahi
    c_name = st.session_state.form_name.strip()
    c_city = st.session_state.form_city.strip()
    items = st.session_state.form_items.strip()
    bill = st.session_state.form_bill
    date_val = st.session_state.form_date.strftime("%Y-%m-%d")

    if c_name and c_city and items and bill > 0:
        # Naya data create karna
        new_row = pd.DataFrame([{
            "Customer_Name": c_name,
            "City": c_city,
            "Items_List": items,
            "Total_Bill": float(bill),
            "Order_Date": date_val
        }])
        
        # Memory mein data jodna
        st.session_state.business_df = pd.concat([st.session_state.business_df, new_row], ignore_index=True)
        
        # File mein permanently save karna
        st.session_state.business_df.to_csv(DATA_FILE, index=False)
        
        st.toast(f"✅ {c_name} ka bill kamyabi se save ho gaya!", icon="🎉")
        
        # --- ERASE / CLEAR BOXES ---
        # Input boxes ko khali karne ke liye unki values reset karna
        st.session_state.form_name = ""
        st.session_state.form_city = ""
        st.session_state.form_items = ""
        st.session_state.form_bill = 0.0
    else:
        st.error("❌ Kripya saari details (Naam, City, Items aur Bill) sahi se bharein!")

# --- APP INTERFACE ---
st.title("📊 My Smart Business Tracker")

# Sidebar Navigation
menu = ["📝 Naya Bill Upload Karen", "🔍 Search Dashboard"]
choice = st.sidebar.selectbox("Menu Chuniye", menu)

# Ek baar data ko variable mein le lena search ke liye
df = st.session_state.business_df

# --- 1. DATA ENTRY SECTION ---
if choice == "📝 Naya Bill Upload Karen":
    st.header("🛍️ Customer Ka Naya Bill Daalein")
    st.write("Niche details bharein aur save button dabayein. Save hote hi form agle bill ke liye khali ho jayega.")
    
    # Input fields mein 'key' lagayi hai taaki hum unhe clear kar sakein
    st.text_input("👤 Customer Ka Naam", key="form_name")
    st.text_input("📍 Customer Ka Shahar (City)", key="form_city")
    st.text_area("📦 Samaan Ki List (e.g., 2 Dhoop, 1 Agarbatti)", key="form_items")
    st.number_input("💰 Total Bill (Kitne Rupaye Hue?)", min_value=0.0, step=10.0, key="form_bill")
    st.date_input("📅 Tarikh (Date)", datetime.now(), key="form_date")

    # Button dabane par 'save_and_clear_form' function chalega
    st.button("🚀 Bill Save Karen", on_click=save_and_clear_form)

# --- 2. SEARCH DASHBOARD ---
elif choice == "🔍 Search Dashboard":
    st.header("🧐 Bill aur Customer History Khojein")
    
    if df.empty:
        st.info("⚠️ Abhi app mein koi data nahi hai. Pehle 'Naya Bill Upload Karen' section mein jaakar entry karein.")
    else:
        # Customer Search
        st.subheader("👤 Customer Ke Naam Se Khojein")
        search_name = st.text_input("Customer ka naam likhein...").strip()
        if search_name:
            res = df[df['Customer_Name'].str.contains(search_name, case=False, na=False)]
            if not res.empty:
                st.dataframe(res[['Order_Date', 'Items_List', 'Total_Bill', 'City']], use_container_width=True)
            else:
                st.warning("Is naam ka koi customer nahi mila.")

        # City Search
        st.subheader("📍 Shahar (City) Ke Hisab Se")
        search_city = st.text_input("Shahar ka naam likhein (e.g., Mumbai)...").strip()
        if search_city:
            res = df[df['City'].str.contains(search_city, case=False, na=False)]
            if not res.empty:
                st.dataframe(res[['Customer_Name', 'Items_List', 'Total_Bill', 'Order_Date']], use_container_width=True)
            else:
                st.warning("Is shahar ka koi data nahi mila.")

        # Product/Item Search
        st.subheader("📦 Samaan (Product) Ke Hisab Se")
        search_item = st.text_input("Samaan ka naam likhein (e.g., Dhoop)...").strip()
        if search_item:
            res = df[df['Items_List'].str.contains(search_item, case=False, na=False)]
            if not res.empty:
                st.dataframe(res[['Customer_Name', 'City', 'Items_List', 'Total_Bill', 'Order_Date']], use_container_width=True)
            else:
                st.warning("Is samaan ka koi data nahi mila.")
