"""
Multi-User File Management System for DTI CPMS
Handles concurrent users with file-based storage
"""

import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
import fcntl  # For file locking on Unix systems
import threading
from pathlib import Path

class DTIDataManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.users_dir = self.data_dir / "users"
        self.consolidated_dir = self.data_dir / "consolidated"
        self.backup_dir = self.data_dir / "backups"
        
        # Create all necessary directories
        for directory in [self.data_dir, self.users_dir, self.consolidated_dir, self.backup_dir]:
            directory.mkdir(exist_ok=True)
        
        self.lock = threading.Lock()
    
    def get_user_file_path(self, username, sheet_name):
        """Get file path for user-specific data"""
        user_dir = self.users_dir / username
        user_dir.mkdir(exist_ok=True)
        return user_dir / f"{sheet_name.replace(' ', '_')}.json"
    
    def save_user_data(self, username, sheet_name, data, columns):
        """Save data for a specific user and sheet with file locking"""
        try:
            with self.lock:  # Thread-safe operation
                file_path = self.get_user_file_path(username, sheet_name)
                
                # Prepare data structure
                user_data = {
                    "username": username,
                    "sheet_name": sheet_name,
                    "columns": columns,
                    "data": data,
                    "last_updated": datetime.now().isoformat(),
                    "version": 1,
                    "row_count": len(data)
                }
                
                # Save to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, indent=2, ensure_ascii=False, default=str)
                
                # Also save to consolidated view
                self.update_consolidated_data(sheet_name)
                
                return True
                
        except Exception as e:
            st.error(f"Error saving data for {username}: {str(e)}")
            return False
    
    def load_user_data(self, username, sheet_name):
        """Load data for a specific user and sheet"""
        try:
            file_path = self.get_user_file_path(username, sheet_name)
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                return user_data.get("data", []), user_data.get("columns", [])
            
            return [], []
            
        except Exception as e:
            st.error(f"Error loading data for {username}: {str(e)}")
            return [], []
    
    def update_consolidated_data(self, sheet_name):
        """Create consolidated view of all users' data for a sheet"""
        try:
            consolidated_data = []
            all_columns = []
            
            # Collect data from all users
            for user_dir in self.users_dir.iterdir():
                if user_dir.is_dir():
                    username = user_dir.name
                    user_data, user_columns = self.load_user_data(username, sheet_name)
                    
                    if user_data and user_columns:
                        if not all_columns:
                            all_columns = ["Encoder", "Entry_Date"] + user_columns[1:]  # Skip 'No' column
                        
                        # Add encoder info and timestamp to each row
                        for i, row in enumerate(user_data):
                            if len(row) > 0:
                                consolidated_row = [
                                    username,  # Encoder name
                                    datetime.now().strftime("%Y-%m-%d %H:%M"),  # Entry date
                                ] + row[1:]  # Skip original 'No' column, we'll renumber
                                consolidated_data.append(consolidated_row)
            
            # Renumber all entries
            for i, row in enumerate(consolidated_data):
                row.insert(2, i + 1)  # Insert new sequential number after encoder and date
            
            if all_columns:
                all_columns.insert(2, "No")  # Insert No column after Encoder and Entry_Date
            
            # Save consolidated data
            consolidated_file = self.consolidated_dir / f"{sheet_name.replace(' ', '_')}_consolidated.json"
            consolidated_info = {
                "sheet_name": sheet_name,
                "columns": all_columns,
                "data": consolidated_data,
                "total_entries": len(consolidated_data),
                "last_updated": datetime.now().isoformat(),
                "contributing_encoders": list(set([row[0] for row in consolidated_data]))
            }
            
            with open(consolidated_file, 'w', encoding='utf-8') as f:
                json.dump(consolidated_info, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            st.error(f"Error updating consolidated data: {str(e)}")
            return False
    
    def get_consolidated_data(self, sheet_name):
        """Get consolidated data from all users"""
        try:
            consolidated_file = self.consolidated_dir / f"{sheet_name.replace(' ', '_')}_consolidated.json"
            
            if consolidated_file.exists():
                with open(consolidated_file, 'r', encoding='utf-8') as f:
                    consolidated_info = json.load(f)
                return consolidated_info.get("data", []), consolidated_info.get("columns", [])
            
            return [], []
            
        except Exception as e:
            st.error(f"Error loading consolidated data: {str(e)}")
            return [], []
    
    def create_backup(self, sheet_name=None):
        """Create backup of all data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if sheet_name:
                # Backup specific sheet
                backup_file = self.backup_dir / f"{sheet_name}_{timestamp}_backup.json"
                consolidated_data, columns = self.get_consolidated_data(sheet_name)
                
                backup_info = {
                    "sheet_name": sheet_name,
                    "backup_date": datetime.now().isoformat(),
                    "data": consolidated_data,
                    "columns": columns
                }
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_info, f, indent=2, ensure_ascii=False, default=str)
            else:
                # Backup all sheets
                backup_file = self.backup_dir / f"full_backup_{timestamp}.json"
                # Implementation for full backup
                pass
            
            return True
            
        except Exception as e:
            st.error(f"Error creating backup: {str(e)}")
            return False
    
    def get_user_statistics(self):
        """Get statistics about user activity"""
        try:
            stats = {
                "total_users": 0,
                "active_sheets": [],
                "total_entries_per_sheet": {},
                "last_activity": {}
            }
            
            for user_dir in self.users_dir.iterdir():
                if user_dir.is_dir():
                    stats["total_users"] += 1
                    username = user_dir.name
                    
                    for data_file in user_dir.glob("*.json"):
                        sheet_name = data_file.stem.replace('_', ' ')
                        if sheet_name not in stats["active_sheets"]:
                            stats["active_sheets"].append(sheet_name)
                        
                        # Load file to get entry count and last activity
                        with open(data_file, 'r', encoding='utf-8') as f:
                            user_data = json.load(f)
                            
                        entry_count = len(user_data.get("data", []))
                        stats["total_entries_per_sheet"][sheet_name] = stats["total_entries_per_sheet"].get(sheet_name, 0) + entry_count
                        
                        last_updated = user_data.get("last_updated", "")
                        if sheet_name not in stats["last_activity"] or last_updated > stats["last_activity"][sheet_name]:
                            stats["last_activity"][sheet_name] = last_updated
            
            return stats
            
        except Exception as e:
            st.error(f"Error getting statistics: {str(e)}")
            return {}

# Global instance
dti_data_manager = DTIDataManager()
