import streamlit as st
from utils.recommender import CollaborativeRecommender

def show_recommendations(data_loader):
    st.title("🌟 Personalized Recommendations")
    
    # Initialize recommender
    recommender = CollaborativeRecommender(data_loader.df)
    
    if "user" in st.session_state and st.session_state.logged_in:
        user_id = st.session_state.user["id"]
        
        # Get recommendations
        recommendations = recommender.get_recommendations_for_user(user_id)
        
        if recommendations.empty:
            st.info("We don't have enough data to make personalized recommendations yet. Please update your preferences or explore our hotels.")
        else:
            st.write("Based on your preferences and similar users, we think you'll love these hotels:")
            
            # Display recommendations
            for _, hotel in recommendations.iterrows():
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
    else:
        st.info("Please log in to see personalized recommendations.")
        if st.button("Login / Register"):
            st.session_state.page = 'user'
            st.rerun() 