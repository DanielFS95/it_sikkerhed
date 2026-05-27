import os, json
from dataclasses import asdict
from src.flat_file.user import User
from src.flat_file.encryption_service import ENCRYPTED_FIELDS


class Flat_file_loader:
    def __init__(self, database_file_name: str = "db_flat_file.json", encryption_service=None):
        self.database_file_name = database_file_name
        self.encryption_service = encryption_service

    def load_memory_database_from_file(self):
        users = []
        try:
            with open(self.database_file_name, "r", encoding="utf-8") as f:
                dict_data = json.load(f)
                raw_users = dict_data.get("users", [])
                if self.encryption_service:
                    raw_users = [self._decrypt_user_dict(u) for u in raw_users]
                users = [User(**u) for u in raw_users]
        except:
            print(f"WARNING: file '{self.database_file_name}' don't exist or is corrupt")
        return users

    def save_memory_database_to_file(self, users):
        user_dicts = [asdict(user) for user in users]
        if self.encryption_service:
            user_dicts = [self._encrypt_user_dict(u) for u in user_dicts]
        with open(self.database_file_name, "w", encoding="utf-8") as f:
            json.dump({"users": user_dicts}, f, indent=2, ensure_ascii=False)

    def _encrypt_user_dict(self, user_dict: dict) -> dict:
        result = user_dict.copy()
        for field in ENCRYPTED_FIELDS:
            if field in result and result[field] is not None:
                result[field] = self.encryption_service.encrypt(str(result[field]))
        return result

    def _decrypt_user_dict(self, user_dict: dict) -> dict:
        result = user_dict.copy()
        for field in ENCRYPTED_FIELDS:
            if field in result and result[field] is not None:
                result[field] = self.encryption_service.decrypt(str(result[field]))
        return result