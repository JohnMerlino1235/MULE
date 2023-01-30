from flask import Flask, jsonify
from flask_cors import CORS
from db.model.database_user import DatabaseUserModel

app = Flask(__name__)
CORS(app)

@app.route('/fetch_user_from_db/<email>', methods=['POST'])
def fetch_user_from_db(email):
    # temporary_user_model = DatabaseUserModel(email, 'somePassword', 'someFirstName', 'someLastName')
    print("User fetched from database with email ", email)
    response = jsonify({'email': email})
    return response
    # return temporary_user_model.fetch_user_from_database()

@app.route('/upsert_user_to_db')
def upsert_user_to_db(email, password, first_name, last_name):
    # temporary_user_model = DatabaseUserModel(email, password, first_name, last_name)
    # temporary_user_model.upsert_user_to_database()
    print("User upserted to database with email")
    return

@app.route('/register_user/<email>', methods=['POST'])
def register_user(email, password, first_name, last_name):
    user_database_model = DatabaseUserModel(email, password, first_name, last_name)
    fetched_user_from_db = user_database_model.fetch_user_from_database()
    # First we fetch the user from our database to check to see if they are already registered
    if fetched_user_from_db:
        print("User already registered in our database")
        return
    user_database_model.upsert_user_to_database()

    print("User successfully registered")
    return

@app.route('/login_user/<email>', methods=['POST'])
def login_user(email, password):
    user_database_model = DatabaseUserModel(email, password)
    fetched_user_from_db = user_database_model.fetch_user_from_database()
    if not fetched_user_from_db:
        print("User not found in database")
        return
    print("User logged in with following details ", fetched_user_from_db.email,
          fetched_user_from_db.password, fetched_user_from_db.first_name, fetched_user_from_db.last_name)

    return
