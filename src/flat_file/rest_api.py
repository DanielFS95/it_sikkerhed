from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.flat_file.data_handler import Data_handler


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    address: str
    street_number: str
    password: str


class Rest_api:
    def __init__(self, database_file_name: str = "users.json"):
        self.data_handler = Data_handler(database_file_name)
        self.app = FastAPI()

        self.app.post("/user")(self.create_user)
        self.app.get("/user/{user_id}")(self.get_user)
        self.app.put("/user/{user_id}/disable")(self.disable_user)
        self.app.put("/user/{user_id}/enable")(self.enable_user)
        self.app.delete("/user/{user_id}")(self.delete_user)

    def create_user(self, user: UserCreate):
        self.data_handler.create_user(
            user.first_name, user.last_name,
            user.address, user.street_number, user.password
        )
        return {"status": "created", "code": 200}

    def get_user(self, user_id: int):
        user = self.data_handler.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id '{user_id}' not found")
        return {"status": "ok", "body": user}

    def disable_user(self, user_id: int):
        user = self.data_handler.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id '{user_id}' not found")
        self.data_handler.disable_user(user_id)
        return {"status": "disabled"}

    def enable_user(self, user_id: int):
        user = self.data_handler.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id '{user_id}' not found")
        self.data_handler.enable_user(user_id)
        return {"status": "enabled"}

    def delete_user(self, user_id: int):
        user = self.data_handler.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id '{user_id}' not found")
        self.data_handler.delete_user(user_id)
        return {"status": "deleted"}
