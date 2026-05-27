import os, json
from dataclasses import asdict
from src.flat_file.user import User


class Flat_file_loader:
    def __init__(self, database_file_name: str = "db_flat_file.json"):
        self.database_file_name = database_file_name


    def load_memory_database_from_file(self):
        users = []

        try:
            with open(self.database_file_name, "r", encoding="utf-8") as f:
                dict_data = json.load(f)
                users = [User(**user_dict) for user_dict in dict_data.get("users", [])]
        except:
            print(f"WARNING: file '{self.database_file_name}' don't exist or is corrupt")
        return users

    def save_memory_database_to_file(self, users):
        serializable_db = {
            "users": [asdict(user) for user in users]
        }
        with open(self.database_file_name, "w", encoding="utf-8") as f:
            json.dump(serializable_db, f, indent=2, ensure_ascii=False)