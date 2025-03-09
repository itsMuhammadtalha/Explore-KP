import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from utils.preference_handler import PreferenceHandler
from utils.user_manager import UserManager

class CollaborativeRecommender:
    def __init__(self, hotels_df, user_manager=None, preference_handler=None):
        self.hotels_df = hotels_df
        self.user_manager = user_manager or UserManager()
        self.preference_handler = preference_handler or PreferenceHandler()
        
        # Extract ratings from hotel reviews to build user-item matrix
        self.user_item_matrix = self._build_user_item_matrix()
        
    def _build_user_item_matrix(self):
        """Build user-item matrix from hotel reviews"""
        # Create empty dataframe for user-item matrix
        users = set()
        hotels = set()
        
        # Extract all users and hotels
        for _, hotel in self.hotels_df.iterrows():
            hotels.add(hotel['name'])
            for review in hotel['user_reviews']:
                users.add(review['user'])
        
        # Create empty matrix
        matrix = pd.DataFrame(index=list(users), columns=list(hotels))
        
        # Fill matrix with ratings
        for _, hotel in self.hotels_df.iterrows():
            hotel_name = hotel['name']
            for review in hotel['user_reviews']:
                user = review['user']
                rating = review['rating']
                matrix.loc[user, hotel_name] = rating
        
        return matrix
    
    def _get_similar_users(self, user_id, n=5):
        """Find similar users based on preferences"""
        user_preferences = self.preference_handler.get_user_preferences(user_id)
        if not user_preferences:
            return []
        
        all_users = self.preference_handler.preferences["preferences"]
        similarity_scores = []
        
        for other_user in all_users:
            if other_user["user_id"] == user_id:
                continue
                
            score = 0
            
            # Compare location preferences
            user_locations = set(user_preferences.get("preferred_locations", []))
            other_locations = set(other_user.get("preferred_locations", []))
            if user_locations and other_locations:
                location_similarity = len(user_locations.intersection(other_locations)) / max(len(user_locations), len(other_locations))
                score += location_similarity * 0.3  # Weight for location
            
            # Compare amenity preferences
            user_amenities = set(user_preferences.get("preferred_amenities", []))
            other_amenities = set(other_user.get("preferred_amenities", []))
            if user_amenities and other_amenities:
                amenity_similarity = len(user_amenities.intersection(other_amenities)) / max(len(user_amenities), len(other_amenities))
                score += amenity_similarity * 0.3  # Weight for amenities
            
            # Compare travel type
            user_travel = set(user_preferences.get("travel_type", []))
            other_travel = set(other_user.get("travel_type", []))
            if user_travel and other_travel:
                travel_similarity = len(user_travel.intersection(other_travel)) / max(len(user_travel), len(other_travel))
                score += travel_similarity * 0.2  # Weight for travel type
            
            # Compare price range
            user_price = set(user_preferences.get("preferred_price_ranges", []))
            other_price = set(other_user.get("preferred_price_ranges", []))
            if user_price and other_price:
                price_similarity = len(user_price.intersection(other_price)) / max(len(user_price), len(other_price))
                score += price_similarity * 0.2  # Weight for price
            
            similarity_scores.append((other_user["user_id"], score))
        
        # Sort by similarity score and return top n
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        return similarity_scores[:n]
    
    def get_recommendations_from_reviews(self, top_n=5):
        """Get recommendations based on review data"""
        # Fill NaN values with 0
        filled_matrix = self.user_item_matrix.fillna(0)
        
        # Calculate similarity between users
        user_similarity = cosine_similarity(filled_matrix)
        user_similarity_df = pd.DataFrame(user_similarity, 
                                         index=filled_matrix.index, 
                                         columns=filled_matrix.index)
        
        # Get top hotels based on similar users' ratings
        recommendations = {}
        
        for user in filled_matrix.index:
            # Get similar users
            similar_users = user_similarity_df[user].sort_values(ascending=False)[1:6]  # Exclude self
            
            # Get weighted ratings
            weighted_ratings = pd.DataFrame()
            for similar_user, similarity in similar_users.items():
                if similarity <= 0:  # Skip negative similarities
                    continue
                    
                user_ratings = filled_matrix.loc[similar_user]
                weighted_ratings[similar_user] = user_ratings * similarity
            
            # Calculate average weighted rating
            if not weighted_ratings.empty:
                avg_ratings = weighted_ratings.mean(axis=1)
                
                # Filter out already rated hotels
                user_rated = filled_matrix.loc[user]
                unrated_hotels = user_rated[user_rated == 0].index
                recommendations[user] = avg_ratings[unrated_hotels].sort_values(ascending=False)[:top_n]
        
        return recommendations
    
    def get_recommendations_for_user(self, user_id, top_n=5):
        """Get personalized recommendations for a specific user"""
        user_preferences = self.preference_handler.get_user_preferences(user_id)
        if not user_preferences:
            # Return popular hotels if no preferences
            return self._get_popular_hotels(top_n)
        
        # Get similar users based on preferences
        similar_users = self._get_similar_users(user_id, n=5)
        if not similar_users:
            # Return content-based recommendations if no similar users
            return self._get_content_based_recommendations(user_preferences, top_n)
        
        # Get hotels liked by similar users
        scored_hotels = {}
        for similar_user_id, similarity in similar_users:
            similar_preferences = self.preference_handler.get_user_preferences(similar_user_id)
            if not similar_preferences:
                continue
                
            # Check if we have any review data for this user
            # For now, we'll use preferences as a proxy
            for _, hotel in self.hotels_df.iterrows():
                hotel_name = hotel['name']
                
                # Skip if already scored
                if hotel_name in scored_hotels:
                    continue
                
                # Calculate match score based on preferences
                match_score = self._calculate_preference_match(hotel, similar_preferences)
                
                # Weight by user similarity
                weighted_score = match_score * similarity
                
                # Add to scored hotels
                if hotel_name not in scored_hotels:
                    scored_hotels[hotel_name] = weighted_score
                else:
                    scored_hotels[hotel_name] += weighted_score
        
        # Sort hotels by score
        sorted_hotels = sorted(scored_hotels.items(), key=lambda x: x[1], reverse=True)
        
        # Get top N hotels
        top_hotels = [hotel for hotel, _ in sorted_hotels[:top_n]]
        
        # Return hotel details
        return self.hotels_df[self.hotels_df['name'].isin(top_hotels)]
    
    def _calculate_preference_match(self, hotel, preferences):
        """Calculate how well a hotel matches user preferences"""
        score = 0
        
        # Location match
        if hotel['location'] in preferences.get('preferred_locations', []):
            score += 0.3
        
        # Price range match
        if hotel['price_range'] in preferences.get('preferred_price_ranges', []):
            score += 0.2
        
        # Amenities match
        user_amenities = set(preferences.get('preferred_amenities', []))
        hotel_amenities = set(hotel['amenities'])
        if user_amenities and hotel_amenities:
            amenity_overlap = len(user_amenities.intersection(hotel_amenities))
            amenity_score = amenity_overlap / len(user_amenities) if user_amenities else 0
            score += amenity_score * 0.3
        
        # Rating bonus
        score += (hotel['rating'] / 5) * 0.2
        
        return score
    
    def _get_popular_hotels(self, top_n=5):
        """Get most popular hotels based on ratings"""
        # Calculate average rating and number of reviews
        hotel_stats = []
        for _, hotel in self.hotels_df.iterrows():
            avg_rating = hotel['rating']
            num_reviews = len(hotel['user_reviews'])
            # Calculate popularity score (weighted by number of reviews)
            popularity = avg_rating * (1 - np.exp(-num_reviews / 5))
            hotel_stats.append((hotel['name'], popularity))
        
        # Sort by popularity
        hotel_stats.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N hotels
        top_hotels = [hotel for hotel, _ in hotel_stats[:top_n]]
        
        # Return hotel details
        return self.hotels_df[self.hotels_df['name'].isin(top_hotels)]
    
    def _get_content_based_recommendations(self, user_preferences, top_n=5):
        """Get content-based recommendations based on user preferences"""
        scored_hotels = {}
        
        for _, hotel in self.hotels_df.iterrows():
            score = self._calculate_preference_match(hotel, user_preferences)
            scored_hotels[hotel['name']] = score
        
        # Sort hotels by score
        sorted_hotels = sorted(scored_hotels.items(), key=lambda x: x[1], reverse=True)
        
        # Get top N hotels
        top_hotels = [hotel for hotel, _ in sorted_hotels[:top_n]]
        
        # Return hotel details
        return self.hotels_df[self.hotels_df['name'].isin(top_hotels)]