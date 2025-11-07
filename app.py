import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# -------------------------------
# DATASET: Nested Dictionary
# -------------------------------
PRODUCTS = {
    "Electronics": {
        "Laptop": {"name": "Laptop", "price": 70000, "company": "Dell", "last_updated": "2025-10-10"},
        "Smartphone": {"name": "Smartphone", "price": 30000, "company": "Samsung", "last_updated": "2025-09-15"},
        "Earbuds": {"name": "Earbuds", "price": 2500, "company": "Realme", "last_updated": "2025-08-20"},
    },
    "Appliances": {
        "Refrigerator": {"name": "Refrigerator", "price": 55000, "company": "LG", "last_updated": "2025-09-25"},
        "Washing Machine": {"name": "Washing Machine", "price": 45000, "company": "Whirlpool", "last_updated": "2025-07-18"},
    },
    "Accessories": {
        "Keyboard": {"name": "Keyboard", "price": 1200, "company": "Logitech", "last_updated": "2025-08-05"},
        "Mouse": {"name": "Mouse", "price": 800, "company": "HP", "last_updated": "2025-07-30"},
    },
}

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------

@st.cache_data
def load_data():
    """Flatten nested dict -> DataFrame once and cache it."""
    data = []
    for cat, items in PRODUCTS.items():
        for item, details in items.items():
            details = details.copy()
            details["category"] = cat
            details["last_updated"] = pd.to_datetime(details["last_updated"])
            data.append(details)
    df = pd.DataFrame(data)
    return df

def filter_data(df, categories, price_range, sort_by, ascending=True):
    """Apply category, price, and sorting filters."""
    filtered = df[
        df["category"].isin(categories) &
        df["price"].between(price_range[0], price_range[1])
    ]
    return filtered.sort_values(sort_by, ascending=ascending).reset_index(drop=True)

# -------------------------------
# STREAMLIT PAGE SETUP
# -------------------------------
st.set_page_config(page_title="Product Search", layout="wide")
st.title("🛒 Product Search Dashboard")

df = load_data()

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
st.sidebar.header("🎛 Filters")

selected_cats = st.sidebar.multiselect(
    "Category", df["category"].unique(), default=list(df["category"].unique())
)
p_min, p_max = int(df["price"].min()), int(df["price"].max())
price_sel = st.sidebar.slider("Price Range", p_min, p_max, (p_min, p_max))

sort_by = st.sidebar.selectbox("Sort By", ["price", "last_updated", "name"])
ascending = st.sidebar.toggle("Ascending Order", True)

# Summary in sidebar
st.sidebar.markdown("---")
st.sidebar.metric("Total Products", len(df))
st.sidebar.metric("Average Price (₹)", int(np.mean(df["price"])))

# -------------------------------
# MAIN CONTENT
# -------------------------------
col1, col2 = st.columns([2, 5])

with col1:
    st.subheader("🔎 Search")
    query = st.text_input("Product name or company").strip()
    search_btn = st.button("Search")

with col2:
    st.subheader("📊 Overview")
    st.caption("Use filters on the left or the search above.")

# Apply filters
filtered_df = filter_data(df, selected_cats, price_sel, sort_by, ascending)

# Search logic
if query:
    mask = (
        df["name"].str.contains(query, case=False, na=False)
        | df["company"].str.contains(query, case=False, na=False)
    )
    result_df = df[mask]
else:
    result_df = filtered_df

if result_df.empty:
    st.warning("No matching products found.")
else:
    st.success(f"Found {len(result_df)} matching products.")
    st.dataframe(result_df, use_container_width=True)

# -------------------------------
# ADDITIONAL FEATURE: DETAILS VIEW
# -------------------------------
st.markdown("### 🔍 Product Details")

selected = st.selectbox("Select a product to view details:", df["name"].unique())
details = df[df["name"] == selected].iloc[0]

colA, colB = st.columns(2)
with colA:
    st.markdown(f"**🧾 Product:** {details['name']}")
    st.markdown(f"**🏢 Company:** {details['company']}")
with colB:
    st.markdown(f"**💰 Price:** ₹{details['price']:,}")
    st.markdown(f"**📅 Last Updated:** {details['last_updated'].strftime('%d %b %Y')}")

st.markdown("---")
st.caption(f"Average product price across all items: ₹{np.mean(df['price']).round(2)}")
