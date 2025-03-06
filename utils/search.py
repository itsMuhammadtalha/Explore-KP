from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class HotelSearch:
    def __init__(self, hotels_df):
        self.hotels_df = hotels_df
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2)  # Consider both unigrams and bigrams
        )
        self.search_matrix = None
        self.prepare_search_data()
    
    def prepare_search_data(self):
        """Prepare the search index from hotel data"""
        
        # Combine relevant fields for search
        search_texts = self.hotels_df.apply(
            lambda x: f"""
                {x['name']} 
                {x['description']} 
                {' '.join(x['amenities'])} 
                {' '.join(x['nearby_attractions'])}
                {x['location']}
            """,
            axis=1
        )
        
        # Create TF-IDF matrix
        self.search_matrix = self.vectorizer.fit_transform(search_texts)
    
    def search(self, query, top_k=5):
        """Search hotels based on query"""
        
        # Transform search query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.search_matrix)[0]
        
        # Get top results
        top_indices = similarities.argsort()[-top_k:][::-1]
        results = self.hotels_df.iloc[top_indices].copy()
        results['search_score'] = similarities[top_indices]
        
        return results 