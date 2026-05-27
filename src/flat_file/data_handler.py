from src.flat_file.user import User
from src.flat_file.flat_file_loader import Flat_file_loader

class Data_handler:
    users = []

    def __init__(self, flat_file_name="users.json", encryption_service=None):
        self.encryption_service = encryption_service
        self.flat_file_loader = Flat_file_loader(flat_file_name, encryption_service)
        self.users = self.flat_file_loader.load_memory_database_from_file()

    def get_number_of_users(self):
        return len(self.users)

    def get_user_by_id(self, user_id: int):
        foundUser = None
        for user in self.users:
            if user.person_id == user_id:
                foundUser = user
                break
        return foundUser
    
    def create_user(self, first_name, last_name, address, street_number, password):
        userId = len(self.users)
        enabled = True
        if self.encryption_service:
            password = self.encryption_service.hash_password(password)
        user = User(userId, first_name, last_name, address, street_number, password, enabled)
        self.users.append(user)
        self.flat_file_loader.save_memory_database_to_file(self.users)

    def verify_password(self, user_id: int, password: str) -> bool:
        user = self.get_user_by_id(user_id)
        if not user or not self.encryption_service:
            return False
        return self.encryption_service.verify_password(password, user.password)

    def clear_sensitive_data(self):
        """Fjerner dekrypteret brugerdata fra hukommelsen efter brug."""
        self.users.clear()

    def disable_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if user:
            user.enabled = False
            self.flat_file_loader.save_memory_database_to_file(self.users)

    def enable_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if user:
            user.enabled = True
            self.flat_file_loader.save_memory_database_to_file(self.users)

    def delete_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if user:
            self.users.remove(user)
            self.flat_file_loader.save_memory_database_to_file(self.users)

    def update_first_name(self, user_id, new_first_name):
        user = self.get_user_by_id(user_id)
        if user:
            user.first_name = new_first_name
            self.flat_file_loader.save_memory_database_to_file(self.users)

    def update_last_name(self, user_id, new_last_name):
        user = self.get_user_by_id(user_id)
        if user:
            user.last_name = new_last_name
            self.flat_file_loader.save_memory_database_to_file(self.users)

    def update_address(self, user_id, new_address):
        user = self.get_user_by_id(user_id)
        if user:
            user.address = new_address
            self.flat_file_loader.save_memory_database_to_file(self.users)

    def update_street_number(self, user_id, new_street_number):
        user = self.get_user_by_id(user_id)
        if user:
            user.street_number = new_street_number
            self.flat_file_loader.save_memory_database_to_file(self.users)

    def update_password(self, user_id, new_password):
        user = self.get_user_by_id(user_id)
        if user:
            user.password = new_password
            self.flat_file_loader.save_memory_database_to_file(self.users)