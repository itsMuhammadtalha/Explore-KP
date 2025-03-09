import streamlit as st
from utils.preference_handler import PreferenceHandler
from utils.data_loader import DataLoader

def preference_form(data_loader):
    st.title("🔍 Your Travel Preferences")
    
    preference_handler = PreferenceHandler()
    
    # Get existing preferences if any
    if "user" in st.session_state:
        existing_preferences = preference_handler.get_user_preferences(st.session_state.user["id"])
    else:
        existing_preferences = None
    
    # Price range preferences
    price_ranges = data_loader.get_price_ranges()
    selected_price_range = st.multiselect(
        "💰 Preferred Price Range",
        price_ranges,
        default=existing_preferences.get("preferred_price_ranges", []) if existing_preferences else []
    )
    
    # Location preferences
    locations = data_loader.get_locations()
    selected_location = st.multiselect(
        "📍 Preferred Locations",
        locations,
        default=existing_preferences.get("preferred_locations", []) if existing_preferences else []
    )
    
    # Amenities preferences
    amenities = data_loader.get_amenities()
    selected_amenities = st.multiselect(
        "🛋️ Must-Have Amenities",
        amenities,
        default=existing_preferences.get("preferred_amenities", []) if existing_preferences else []
    )
    
    # Travel type
    travel_types = ["Solo", "Couple", "Family", "Friends", "Business"]
    selected_travel_type = st.multiselect(
        "👥 Travel Type",
        travel_types,
        default=existing_preferences.get("travel_type", []) if existing_preferences else []
    )
    
    # Stay duration
    min_stay, max_stay = st.slider(
        "📅 Typical Stay Duration (days)",
        min_value=1,
        max_value=30,
        value=(
            existing_preferences.get("min_stay", 1) if existing_preferences else 1,
            existing_preferences.get("max_stay", 7) if existing_preferences else 7
        )
    )
    
    # Save preferences
    if st.button("Save Preferences"):
        if "user" in st.session_state:
            preferences_data = {
                "preferred_price_ranges": selected_price_range,
                "preferred_locations": selected_location,
                "preferred_amenities": selected_amenities,
                "travel_type": selected_travel_type,
                "min_stay": min_stay,
                "max_stay": max_stay
            }
            
            success, message = preference_handler.save_preferences(
                st.session_state.user["id"], 
                preferences_data
            )
            
            if success:
                st.success(message)
            else:
                st.error(message)
        else:
            st.error("Please log in to save your preferences") 