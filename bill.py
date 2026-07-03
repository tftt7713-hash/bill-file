import streamlit as st
import pandas as pd
from datetime import datetime

# --- GOOGLE SHEET CONNECTION ---
# Yahan apni share ki hui Google Sheet ka link paste karein
GSHEET_URL = "YOUR_GOOGLE_SHEET_URL_HERE"

# Link ko direct entry format mein badalne ka function
def get_csv_url(url):
    try:
        if "/edit" in url:
            return url.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
        return url
    except:
        return url

# Data load karne ka function
def load_data():
    csv_url = get_csv_url(GSHEET_URL)
    try:
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()
        return df
    except:
        # Agar sheet khali hai toh yeh columns banenge
        return pd.DataFrame(columns=["Customer_Name", "City", "Items_List", "Total_Bill", "Order_Date"])

# Title
st.title("📊 My Smart Business Tracker")

# Sidebar Menu
menu = ["📝 Naya Bill Upload Karen", "🔍 Search Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

df = load_data()

# --- 1. DATA ENTRY SECTION ---
if choice == "📝 Naya Bill Upload Karen":
    st.header("🛍️ Customer Ka Naya Bill Daalein")
    
    # Form input fields
    c_name = st.text_input("👤 Customer Ka Naam").strip()
    c_city = st.text_input("📍 Customer Ka Shahar (City)").strip()
    
    # Samaan ki list ke liye bada box
    items_list = st.text_area("📦 Samaan Ki List (e.g., 2 Dhoop, 1 Agarbatti, 5 Tel)").strip()
    
    # Bill ke paise
    total_bill = st.number_input("💰 Total Bill (Kitne Rupaye Hue?)", min_value=0.0, step=10.0)
    o_date = st.date_input("📅 Tarikh (Date)", datetime.now())

    if st.button("🚀 Bill Save Karen"):
        if c_name and c_city and items_list and total_bill > 0:
            formatted_date = o_date.strftime("%Y-%m-%d")
            
            # --- GOOGLE SHEET ENTRY METHOD ---
            # NOTE: Internet par bina password ke sheet mein direct write karne ke liye,
            # Streamlit ke 'Secrets' ka use hota hai. Agar aap direct live app se save karna chahte hain,
            # toh abhi ke liye aapko niche ek link milega jisse aap sheet mein data daal sakenge,
            # ya fir aap niche diye gaye link par click karke direct sheet mein enter kar sakte hain.
            
            st.success(f"✅ App ne data tayar kar liya hai! Bas ise Google Sheet mein save kar dein.")
            st.info(f"Naam: {c_name} | Bill: ₹{total_bill}")
            
            # Form reset ya direct open karne ke liye link
            st.markdown(f"[👉 Google Sheet Mein Entry Lock Karne Ke Liye Yahan Click Karen]({GSHEET_URL})")
        else:
            st.error("❌ Kripya saari details (Naam, City, Items aur Bill Amount) sahi se bharein!")

# --- 2. SEARCH DASHBOARD ---
elif choice == "🔍 Search Dashboard":
    st.header("🧐 Bill aur Customer History Khojein")
    
    if df.empty:
        st.warning("⚠️ Abhi database mein koi data nahi hai. Pehle Google Sheet mein thoda data daalein.")
    else:
        # Customer Search
        st.subheader("👤 Customer Ke Naam Se Khojein")
        search_name = st.text_input("Customer ka naam likhein...").strip()
        if search_name:
            res = df[df['Customer_Name'].str.contains(search_name, case=False, na=False)]
            st.dataframe(res[['Order_Date', 'Items_List', 'Total_Bill', 'City']], use_container_width=True)

        # City Search
        st.subheader("📍 Shahar (City) Ke Hisab Se")
        search_city = st.text_input("Shahar ka naam likhein (e.g., Mumbai)...").strip()
        if search_city:
            res = df[df['City'].str.contains(search_city, case=False, na=False)]
            st.dataframe(res[['Customer_Name', 'Items_List', 'Total_Bill', 'Order_Date']], use_container_width=True)

        # Product/Item Search
        st.subheader("📦 Samaan (Product) Ke Hisab Se")
        search_item = st.text_input("Samaan ka naam likhein (e.g., Dhoop)...").strip()
        if search_item:
            res = df[df['Items_List'].str.contains(search_item, case=False, na=False)]
            st.dataframe(res[['Customer_Name', 'City', 'Items_List', 'Total_Bill', 'Order_Date']], use_container_width=True)
