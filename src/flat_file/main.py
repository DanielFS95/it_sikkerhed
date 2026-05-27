from src.flat_file.rest_api import Rest_api

api = Rest_api(database_file_name="./users.json")
app = api.app

# Kør i terminal/console med:
# uvicorn src.flat_file.main:app --reload
#
# Kør i browser:
# http://127.0.0.1:8000/
#
# Documentation:
# http://127.0.0.1:8000/docs
