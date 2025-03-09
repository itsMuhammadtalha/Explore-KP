import json
import os
import uuid
from datetime import datetime

class UserManager:
    def __init__(self, users_file_path="data/users.json"):
        self.users_file_path = users_file_path
        self.users = self._load_users()
        
    def _load_users(self):
        """Load users from JSON file or create empty structure if file doesn't exist"""
        if os.path.exists(self.users_file_path):
            try:
                with open(self.users_file_path, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {"users": []}
        else:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.users_file_path), exist_ok=True)
            return {"users": []}
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(self.users_file_path, 'w') as file:
            json.dump(self.users, file, indent=4)
    
    def create_user(self, username, email, password):
        """Create a new user"""
        # Check if username or email already exists
        for user in self.users["users"]:
            if user["username"] == username:
                return False, "Username already exists"
            if user["email"] == email:
                return False, "Email already exists"
        
        # Create new user
        new_user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "password": password,  # In a real app, this should be hashed
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self.users["users"].append(new_user)
        self._save_users()
        return True, "User created successfully"
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        for user in self.users["users"]:
            if user["username"] == username and user["password"] == password:
                # Update last login
                user["last_login"] = datetime.now().isoformat()
                self._save_users()
                return True, user
        return False, "Invalid username or password"
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        for user in self.users["users"]:
            if user["id"] == user_id:
                return user
        return None
    
    def get_all_users(self):
        """Get all users"""
        return self.users["users"] 