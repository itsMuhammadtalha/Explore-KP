import json
import os

class PreferenceHandler:
    def __init__(self, preferences_file_path="data/user_preferences.json"):
        self.preferences_file_path = preferences_file_path
        self.preferences = self._load_preferences()
    
    def _load_preferences(self):
        """Load preferences from JSON file or create empty structure if file doesn't exist"""
        if os.path.exists(self.preferences_file_path):
            try:
                with open(self.preferences_file_path, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {"preferences": []}
        else:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.preferences_file_path), exist_ok=True)
            return {"preferences": []}
    
    def _save_preferences(self):
        """Save preferences to JSON file"""
        with open(self.preferences_file_path, 'w') as file:
            json.dump(self.preferences, file, indent=4)
    
    def save_preferences(self, user_id, preferences_data):
        """Save user preferences"""
        # Check if user already has preferences
        for pref in self.preferences["preferences"]:
            if pref["user_id"] == user_id:
                # Update existing preferences
                pref.update(preferences_data)
                self._save_preferences()
                return True, "Preferences updated successfully"
        
        # Create new preferences
        new_preferences = {
            "user_id": user_id,
            **preferences_data
        }
        
        self.preferences["preferences"].append(new_preferences)
        self._save_preferences()
        return True, "Preferences saved successfully"
    
    def get_user_preferences(self, user_id):
        """Get preferences for a specific user"""
        for pref in self.preferences["preferences"]:
            if pref["user_id"] == user_id:
                return pref
        return None 