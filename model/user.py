from db.model.database_user import DatabaseUserModel
# User is an object that represents a standard User
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
        database_user_model = user_model_to_database_user_model(self)
        database_user_model.upsert_user_to_database()

    # fetch_user_from_database retrieves user information from the database
    def fetch_user_from_database(self):
        database_user_model = user_model_to_database_user_model(self)
        fetched_user = database_user_model.fetch_user_from_database()
        return fetched_user

# user_model_to_database_user_model is a mapper to convert from a model to a database model
def user_model_to_database_user_model(user_model):
    return DatabaseUserModel(user_model.email, user_model.password, user_model.first_name, user_model.last_name)

# database_user_model_to_user_model is a mapper to convert from a database model to model
def database_user_model_to_user_model(database_user_model):
    return User(database_user_model.email, database_user_model.password, database_user_model.first_name, database_user_model.last_name)