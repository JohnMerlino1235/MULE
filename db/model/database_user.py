from mysql.connector import connect

# DatabaseUserModel is an object that represents a standard User strictly for database operations
class DatabaseUserModel:
    def __init__(self, email, password=None, first_name=None, last_name=None):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.database = connect(
            host='localhost',
            user='root',
            password='rootroot',
            database='lams'
        )

    # upsert_user_to_database upserts user information to the database and adds a new row
    def upsert_user_to_database(self):
        if not self.password:
            print("Password was never set")
            return
        if not self.first_name:
            print("First Name was never set")
            return
        if not self.last_name:
            print("Last Name was never set")
            return
        upsert_user_query = """
            INSERT INTO users
            VALUES (%s, %s, %s, %s)
        """
        user_data_to_upsert = (self.email, self.password, self.first_name, self.last_name)
        with self.database.cursor() as cursor:
            cursor.execute(upsert_user_query, user_data_to_upsert)
            self.database.commit()
        print("User successfully upserted to database")
        return None

    # fetch_user_from_database retrieves user information from the database and returns a new database model with
    # the fetched information
    def fetch_user_from_database(self):
        fetch_user_query = """
            SELECT * FROM users
            WHERE email = %s
        """
        user_info = []
        params = (self.email, )
        with self.database.cursor() as cursor:
            cursor.execute(fetch_user_query, params)
            for row in cursor:
                user_info.append(row)
        if len(user_info) == 0:
            print("multiple users with same email")

        fetched_user = user_info[0]

        return DatabaseUserModel(fetched_user[0], fetched_user[1], fetched_user[2], fetched_user[3])
