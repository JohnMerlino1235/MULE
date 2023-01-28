from flask import Flask
from db.model.database_user import DatabaseUserModel

app = Flask(__name__)

@app.route('/fetch_user_from_db')
def fetch_user_from_db(email):
    temporary_user_model = DatabaseUserModel(email, 'somePassword', 'someFirstName', 'someLastName')
    print("User fetched from database with email ", temporary_user_model.email)
    return temporary_user_model.fetch_user_from_database()

@app.route('/upsert_user_to_db')
def upsert_user_to_db(email, password, first_name, last_name):
    temporary_user_model = DatabaseUserModel(email, password, first_name, last_name)
    temporary_user_model.upsert_user_to_database()
    print("User upserted to database with email ", temporary_user_model.email)
    return
