import streamlit as st
from utils.data_loader import DataLoader
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Pakistan Travel Guide - Swat Valley",
    page_icon="🏔️",
    layout="wide"
)

# Initialize data loader
@st.cache_resource
def get_data():
    return DataLoader("/home/talha/Documents/travel-app/data/swat_complete_hotels.json")

data_loader = get_data()

def main():
    # Sidebar filters
    st.sidebar.title("Filter Hotels")
    
    # Price range filter
    price_ranges = data_loader.get_price_ranges()
    selected_price_range = st.sidebar.multiselect(
        "Price Range",
        price_ranges
    )
    
    # Location filter
    locations = data_loader.get_locations()
    selected_location = st.sidebar.multiselect(
        "Location",
        locations
    )
    
    # Rating filter
    min_rating = st.sidebar.slider(
        "Minimum Rating",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.5
    )
    
    st.markdown("""
<style>
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .hotel-card {
        background-color: black;
        border-radius: 8px;
        padding: 20px;
        margin: 20px auto;
        border: 1px solid #eee;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }
    
    .section {
        background-color: grey;
        padding: 15px;
        border-radius: 6px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)
    # Main content
 
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title("🏔️ Discover Swat Valley")
    st.write("Explore the beautiful hotels and accommodations in Swat Valley")
    
    # Filter data based on selections
    filtered_data = data_loader.df
    
    if selected_price_range:
        filtered_data = filtered_data[filtered_data['price_range'].isin(selected_price_range)]
    if selected_location:
        filtered_data = filtered_data[filtered_data['location'].isin(selected_location)]
    filtered_data = filtered_data[filtered_data['rating'] >= min_rating]
    
    # Display hotels
    for _, hotel in filtered_data.iterrows():
        st.markdown("""
        <div class="hotel-card">
            <h2>{}</h2>
            <p>⭐ {} | 💰 {} | 📍 {}</p>
            <p>{}</p>
            <div class="section">
                <h3>🛋️ Amenities</h3>
                <p>{}</p>
            </div>
            <div class="section">
                <h3>🎯 Nearby Attractions</h3>
                <p>{}</p>
            </div>
        </div>
        """.format(
            hotel['name'],
            hotel['rating'],
            hotel['price_range'],
            hotel['location'],
            hotel['description'],
            ', '.join(hotel['amenities'][:5]) + ('...' if len(hotel['amenities']) > 5 else ''),
            ', '.join(hotel['nearby_attractions'][:3]) + ('...' if len(hotel['nearby_attractions']) > 3 else '')
        ), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()