import streamlit as st
from utils.data_loader import DataLoader
import pandas as pd
from components.chat_interface import chat_interface


# Page configuration
st.set_page_config(
    page_title="Explore KP - AI Travel Guide",
    page_icon="🏔️",
    layout="wide"
)
# new
# Initialize data loader
@st.cache_resource
def get_data():
    return DataLoader("data/swat_complete_hotels.json")

data_loader = get_data()

# Add custom CSS for hotel cards with new color scheme
st.markdown("""
<style>
    /* Global styles */
    body {
        color: #B0C4DE;  /* Cool Gray for text */
        background-color: #FAFAFA;  /* Light Pearl White background */
    }
    
    /* Streamlit container customization */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #87CEEB !important;  /* Sky Blue for headers */
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #FAFAFA;  /* Light Pearl White */
        border-right: 1px solid #B0C4DE;  /* Cool Gray border */
    }
    
    /* Multiselect and dropdown styling */
    .stMultiSelect div[data-baseweb="select"] {
        border-color: #87CEEB !important;  /* Sky Blue border */
    }
    
    .stMultiSelect div[data-baseweb="tag"] {
        background-color: #87CEEB !important;  /* Sky Blue background */
        color: white !important;
    }
    
    /* Slider styling */
    .stSlider div[data-baseweb="slider"] div[data-testid="stThumbValue"] {
        background-color:  !important;  /* Sky Blue for slider */
    }
    
    .stSlider div[data-baseweb="slider"] div {
        background-color:;  /* Cool Gray for slider track */
    }
    
    /* Hotel card styling */
    .hotel-card {
        background: black  /* Light Pearl White */
        border: 5px solid #B0C4DE;  /* Cool Gray border */
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 6px rgba(176, 196, 222, 0.15);  /* Cool Gray shadow */
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        transition: transform 0.2s ease-in-out;
    }
    
    .hotel-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 10px rgba(176, 196, 222, 0.25);
    }
    
    .hotel-image {
        width: 100%;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 2px solid #87CEEB;  /* Sky Blue border for images */
    }
    
    .hotel-title {
        color: white !important;  /* Sky Blue for hotel titles */
        font-size: 24px;
        margin-bottom: 10px;
    }
    
    .hotel-meta {
        color: #B0C4DE;  /* Cool Gray */
        font-size: 16px;
        margin-bottom: 15px;
    }
    
    .hotel-description {
        color: #555;  /* Darker text for better readability */
        font-size: 15px;
        line-height: 1.5;
        margin-bottom: 15px;
    }
    
    .section-title {
        color: white !important;  /* Sky Blue */
        font-size: 18px;
        margin: 15px 0 10px 0;
        font-weight: 600;
    }
    
    .amenities-list, .attractions-list {
        color: #666;
        font-size: 14px;
    }
    
    /* Container for centered content */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
            
    .contact-info {
        padding: 15px;
        background: #F5DEB3;  /* Soft Sand */
        border-radius: 8px;
        margin-top: 10px;
    }
    
    .contact-row {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        padding: 8px;
        background: #FAFAFA;  /* Light Pearl White */
        border-radius: 6px;
    }
    
    .contact-label {
        min-width: 80px;
        color: #87CEEB;  /* Sky Blue */
        font-weight: 500;
    }
    
    .contact-value {
        color: #555;  /* Darker text for better readability */
        margin-left: 15px;
    }

    /* Button styling */
    .stButton>button {
        background-color: #FF6F61 !important;  /* Coral Pink */
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #ff8577 !important;  /* Lighter Coral Pink */
        box-shadow: 0 2px 6px rgba(255, 111, 97, 0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Success messages */
    .success-message {
        color: #50C878 !important;  /* Emerald Green */
        font-weight: 500 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F5DEB3 !important;  /* Soft Sand */
        color: #555 !important;
        border-radius: 4px !important;
    }
    
    .streamlit-expanderContent {
        border: 1px solid #F5DEB3 !important;  /* Soft Sand */
        border-top: none !important;
        border-radius: 0 0 4px 4px !important;
    }
    
    /* Chat interface styling */
    .user-message {
        background-color: #87CEEB !important;  /* Sky Blue */
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        margin-bottom: 10px !important;
        max-width: 80% !important;
        align-self: flex-end !important;
    }
    
    .ai-message {
        background-color: #F5DEB3 !important;  /* Soft Sand */
        color: #555 !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        margin-bottom: 10px !important;
        max-width: 80% !important;
        align-self: flex-start !important;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-color: #B0C4DE !important;  /* Cool Gray */
        color: #555 !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #87CEEB !important;  /* Sky Blue */
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    
    # Sidebar filters
    with st.sidebar:
        st.title("🔍 Filters")
        st.markdown("---")
        
        # Price range filter
        price_ranges = data_loader.get_price_ranges()
        selected_price_range = st.multiselect(
            "💰 Price Range",
            price_ranges
        )
        
        # Location filter
        locations = data_loader.get_locations()
        selected_location = st.multiselect(
            "📍 Location",
            locations
        )
        
        # Rating filter
        min_rating = st.slider(
            "⭐ Minimum Rating",
            min_value=1.0,
            max_value=5.0,
            value=1.0,
            step=0.5
        )
        
        st.markdown("---")
        # AI Chat button in sidebar
        if st.button("🤖 Chat with AI", use_container_width=True):
            st.session_state.page = 'chat'
            st.rerun()
    
    # Main content area
    if st.session_state.page == 'main':
        # Center-aligned container
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.title("🏔️ Discover Swat Valley")
        
        # Filter data based on selections
        filtered_data = data_loader.df
        
        if selected_price_range:
            filtered_data = filtered_data[filtered_data['price_range'].isin(selected_price_range)]
        if selected_location:
            filtered_data = filtered_data[filtered_data['location'].isin(selected_location)]
        filtered_data = filtered_data[filtered_data['rating'] >= min_rating]
        
        # Display hotels
        for _, hotel in filtered_data.iterrows():
            st.markdown(f"""
            <div class="hotel-card">
                <h2 class="hotel-title">{hotel['name']}</h2>
                <div class="hotel-meta">
                    ⭐ {hotel['rating']} | 💰 {hotel['price_range']} | 📍 {hotel['location']}
                </div>
                <p class="hotel-description">{hotel['description']}</p>
                <h3 class="section-title">🛋️ Amenities</h3>
                <p class="amenities-list">{', '.join(hotel['amenities'][:5])}
                    {'...' if len(hotel['amenities']) > 5 else ''}</p>
                <h3 class="section-title">🎯 Nearby Attractions</h3>
                <p class="attractions-list">{', '.join(hotel['nearby_attractions'][:3])}
                    {'...' if len(hotel['nearby_attractions']) > 3 else ''}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Contact information as a dropdown
            with st.expander("📞 Contact Information"):
                st.markdown(f"""
                <div class="contact-info">
                    <div class="contact-row">
                        <span class="contact-label">📱 Phone</span>
                        <span class="contact-value">{hotel['contact']['phone']}</span>
                    </div>
                    <div class="contact-row">
                        <span class="contact-label">📧 Email</span>
                        <span class="contact-value">{hotel['contact']['email']}</span>
                    </div>
                    <div class="contact-row">
                        <span class="contact-label">🌐 Website</span>
                        <span class="contact-value">{hotel['contact']['website']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat page
    elif st.session_state.page == 'chat':
        # Add back button
        if st.button("← Back to Hotels"):
            st.session_state.page = 'main'
            st.rerun()
        
        # Show chat interface
        chat_interface()

if __name__ == "__main__":
    main()