# User is an object that represents a standard User strictly for database operations
class DatabaseUserModel:
    def __init__(self, email, password, first_name, last_name):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    # upsert_user_to_database upserts user information to the database
    def upsert_user_to_database(self):
        return None

    # fetch_user_from_database retrieves user information from the database
    def fetch_user_from_database(self):
        return None
