# User is an object that represents a standard User
import mappers
class User:
    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    # get_email is a getter for a user's email
    def get_email(self):
        return self.email

    # get_password is a getter for a user's password
    def get_password(self):
        return self.password

    # get_first_name is a getter for a user's first name
    def get_first_name(self):
        return self.first_name

    # get_last_name is a getter for a user's first name
    def get_last_name(self):
        return self.last_name

    # upsert_user_to_database upserts user information to the database
    def upsert_user_to_database(self):
        database_user_model = mappers.user_model_to_database_user_model(self)
        return None

    # fetch_user_from_database retrieves user information from the database
    def fetch_user_from_database(self):
        database_user_model = mappers.user_model_to_database_user_model(self)
        return None
