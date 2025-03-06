import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEngine:
    def __init__(self):
        self.scaler = MinMaxScaler()
        
    def extract_features(self, hotels_df):
        """Convert hotel data into numerical features for similarity calculation"""
        
        # Extract price levels (convert price ranges to numerical values)
        def get_price_level(price_range):
            avg_price = np.mean([float(x.replace(',', '').replace('PKR', '').strip()) 
                               for x in price_range.split('-')])
            return avg_price
        
        # Create feature matrix
        features = []
        for _, hotel in hotels_df.iterrows():
            hotel_features = [
                get_price_level(hotel['price_range']),  # Price level
                hotel['rating'],                        # Rating
                len(hotel['amenities']),               # Number of amenities
                len(hotel['nearby_attractions']),      # Number of attractions
                # Location encoding (could be lat/long or one-hot encoded)
                hotel['coordinates']['lat'],
                hotel['coordinates']['lng']
            ]
            features.append(hotel_features)
            
        # Normalize features
        features_normalized = self.scaler.fit_transform(features)
        return features_normalized
    
    def get_user_profile(self, user_preferences):
        """Convert user preferences into a feature vector"""
        
        # Convert user preferences to numerical values
        price_map = {'Budget': 0.2, 'Mid-range': 0.5, 'Luxury': 0.8}
        
        profile = [
            price_map[user_preferences['price_preference']],  # Price preference
            user_preferences.get('min_rating', 0.6),         # Minimum rating
            len(user_preferences.get('preferred_amenities', [])) / 10,  # Amenities preference
            0.5,  # Neutral preference for attractions
            user_preferences.get('preferred_lat', 0.5),      # Location preference
            user_preferences.get('preferred_lng', 0.5)
        ]
        
        # Normalize user profile
        profile_normalized = self.scaler.transform([profile])
        return profile_normalized
    
    def get_recommendations(self, user_preferences, hotels_df, top_k=5):
        """Get personalized hotel recommendations"""
        
        # Extract features from hotels
        hotel_features = self.extract_features(hotels_df)
        
        # Get user profile
        user_profile = self.get_user_profile(user_preferences)
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(user_profile, hotel_features)[0]
        
        # Get top recommendations
        top_indices = similarity_scores.argsort()[-top_k:][::-1]
        recommended_hotels = hotels_df.iloc[top_indices].copy()
        recommended_hotels['similarity_score'] = similarity_scores[top_indices]
        
        return recommended_hotels 