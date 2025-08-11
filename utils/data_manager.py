import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_user_data_file(self, username, sheet_name):
        """Get user-specific data file path"""
        user_dir = os.path.join(self.data_dir, f"user_{username}")
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return os.path.join(user_dir, f"{sheet_name}.json")
    
    def save_user_data(self, username, sheet_name, data, columns):
        """Save data for specific user and sheet"""
        try:
            file_path = self.get_user_data_file(username, sheet_name)
            user_data = {
                "columns": columns,
                "data": data,
                "last_updated": datetime.now().isoformat(),
                "user": username
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")
            return False
    
    def load_user_data(self, username, sheet_name):
        """Load data for specific user and sheet"""
        try:
            file_path = self.get_user_data_file(username, sheet_name)
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                return user_data.get("data", []), user_data.get("columns", [])
            else:
                return [], []
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return [], []
    
    def get_all_users_data(self, sheet_name):
        """Get consolidated data from all users for a specific sheet"""
        all_data = []
        columns = []
        
        if os.path.exists(self.data_dir):
            for user_dir in os.listdir(self.data_dir):
                if user_dir.startswith("user_"):
                    username = user_dir.replace("user_", "")
                    user_data, user_columns = self.load_user_data(username, sheet_name)
                    
                    if user_data and user_columns:
                        if not columns:
                            columns = user_columns
                        
                        # Add user info to each row
                        for row in user_data:
                            row_with_user = [username] + row
                            all_data.append(row_with_user)
        
        if columns:
            columns = ["Encoder"] + columns
        
        return all_data, columns
    
    def user_has_data(self, username):
        """Check if a user has any data in any sheet"""
        try:
            user_dir = os.path.join(self.data_dir, f"user_{username}")
            if not os.path.exists(user_dir):
                return False
            
            # Check all possible sheet files
            sheet_names = [
                "Business Owner", "Business Profile", "Client", "Business Registration",
                "Business Financial Structure", "Market Import", "Product Service Lines",
                "Employment Statistics", "Assistance", "Market Export", "Jobs Generated",
                "Business Contact Information", "Market Domestic"
            ]
            
            for sheet_name in sheet_names:
                file_path = os.path.join(user_dir, f"{sheet_name}.json")
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            user_data = json.load(f)
                        data = user_data.get("data", [])
                        if data and len(data) > 0:
                            return True
                    except:
                        continue
            
            return False
        except Exception as e:
            return False

# Global data manager instance
data_manager = DataManager()
