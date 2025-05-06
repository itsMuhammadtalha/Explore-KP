import networkx as nx
import pandas as pd

file_path = "data/swat_complete_hotels.json"

class KnowledgeGraphRecommender:
    def __init__(self, data):
        self.graph = nx.Graph()
        self.data = data
        self.build_graph()

    def build_graph(self):
        for _, row in self.data.iterrows():
            hotel = row['name']
            self.graph.add_node(hotel, type='hotel')
            # Connect amenities
            for amenity in row['amenities']:
                self.graph.add_node(amenity, type='amenity')
                self.graph.add_edge(hotel, amenity, weight=1.0)
            # Connect location
            location = row['location']
            self.graph.add_node(location, type='location')
            self.graph.add_edge(hotel, location, weight=1.0)
            # Connect attractions
            for attraction in row['nearby_attractions']:
                self.graph.add_node(attraction, type='attraction')
                self.graph.add_edge(hotel, attraction, weight=1.0)
            # Connect price range
            price_range = row['price_range']
            self.graph.add_node(price_range, type='price')
            self.graph.add_edge(hotel, price_range, weight=1.0)
            # Connect rating
            rating_label = f"rating_{int(row['rating'])}"
            self.graph.add_node(rating_label, type='rating')
            self.graph.add_edge(hotel, rating_label, weight=1.0)

    def recommend(self, preferences, top_k=5):
        scores = {}
        for pref in preferences:
            if pref in self.graph:
                paths = nx.single_source_shortest_path_length(self.graph, pref, cutoff=2)
                for hotel, distance in paths.items():
                    if self.graph.nodes[hotel]['type'] == 'hotel' and distance > 0:
                        # Higher score for closer nodes
                        scores[hotel] = scores.get(hotel, 0) + (1 / distance)
        # Return top hotels by score
        ranked_hotels = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked_hotels[:top_k]

def load_data(file_path):
    df = pd.read_json(file_path)
    return df
