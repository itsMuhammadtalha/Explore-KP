import streamlit as st
from recommendation_kg import KnowledgeGraphRecommender, load_data
import streamlit as st
from utils.data_loader import DataLoader
import pandas as pd
from components.chat_interface import chat_interface
from components.user_registration import user_registration
from components.preference_form import preference_form
from components.recommendations import show_recommendations


# Set Streamlit page configuration
st.set_page_config(
    page_title="Explore KP",
    page_icon="🏔️",
    layout="wide"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = {'username': 'Guest'}

# Display main page title
st.markdown("""
    <div style='text-align: center; margin-top: 50px;'>
        <h1 style='font-size: 4em; font-family: sans-serif;'>Explore KP</h1>
    </div>
""", unsafe_allow_html=True)

# Auto-login for testing
if not st.session_state.logged_in:
    st.session_state.logged_in = True
    st.session_state.user['username'] = 'TestUser'

st.success(f"Logged in as {st.session_state.user['username']}")

# City selection
cities = ["Swat", "Murree", "Ayubia", "Natiagali", "Hunza", "Kashmir"]
st.title("Select a City to Explore Hotels")
selected_city = st.selectbox("Select a City", cities)

# Load hotel data
data_loader = DataLoader(f"data/{selected_city.lower()}_complete_hotels.json")
df = data_loader.df

# Sidebar filters
with st.sidebar:
    st.title("🔍 Filters")
    price_ranges = data_loader.get_price_ranges()
    selected_price_range = st.multiselect("💰 Price Range", price_ranges)

    locations = data_loader.get_locations()
    selected_location = st.multiselect("📍 Location", locations)

    min_rating = st.slider("⭐ Minimum Rating", min_value=1.0, max_value=5.0, value=1.0, step=0.5)

    if st.button("Get Recommendations"):
        kg = KnowledgeGraph()
        kg.build_graph(df)
        recommendations = recommend_hotels(kg, df)
        st.session_state.recommendations = recommendations

# Apply filters
filtered_data = df.copy()
if selected_price_range:
    filtered_data = filtered_data[filtered_data['price_range'].isin(selected_price_range)]
if selected_location:
    filtered_data = filtered_data[filtered_data['location'].isin(selected_location)]
filtered_data = filtered_data[filtered_data['rating'] >= min_rating]

# Display filtered hotels
st.title(f"Hotels in {selected_city}")
for _, hotel in filtered_data.iterrows():
    st.markdown(f"""
    <div class="hotel-card">
        <h2>{hotel['name']}</h2>
        <p>⭐ {hotel['rating']} | 💰 {hotel['price_range']} | 📍 {hotel['location']}</p>
        <p>{hotel['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📞 Contact Information"):
        st.write(f"**Phone:** {hotel['contact']['phone']}")
        st.write(f"**Email:** {hotel['contact']['email']}")
        st.write(f"**Website:** {hotel['contact']['website']}")

# Show recommendations if available
if 'recommendations' in st.session_state:
    st.title("🔮 Recommended Hotels")
    for hotel in st.session_state.recommendations:
        st.markdown(f"""
        <div class="hotel-card">
            <h2>{hotel['name']}</h2>
            <p>⭐ {hotel['rating']} | 💰 {hotel['price_range']} | 📍 {hotel['location']}</p>
            <p>{hotel['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📞 Contact Information"):
            st.write(f"**Phone:** {hotel['contact']['phone']}")
            st.write(f"**Email:** {hotel['contact']['email']}")
            st.write(f"**Website:** {hotel['contact']['website']}")
