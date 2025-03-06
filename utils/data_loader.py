import json
import pandas as pd

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.df = None
        self.load_data()
    
    def load_data(self):
        with open(self.file_path, 'r') as file:
            self.data = json.load(file)
            self.df = pd.DataFrame(self.data)
    
    def get_price_ranges(self):
        return self.df['price_range'].unique()
    
    def get_locations(self):
        return self.df['location'].unique()
    
    def get_amenities(self):
        # Flatten all amenities lists and get unique values
        all_amenities = set()
        for amenities in self.df['amenities']:
            all_amenities.update(amenities)
        return sorted(list(all_amenities))
