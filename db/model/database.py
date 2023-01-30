from mysql.connector import connect
from db.model.database_user import DatabaseUserModel


class Database:
    def __init__(self):
        self.database = connect(
            host='localhost',
            user='root',
            password='rootroot',
            database='lams'
        )

    def fetch_user_by_email(self, email):
        fetch_user_query = """
            SELECT * FROM users
            WHERE email = %s
        """
        user_info = []
        params = (email,)
        with self.database.cursor() as cursor:
            cursor.execute(fetch_user_query, params)
            for row in cursor:
                user_info.append(row)
        if len(user_info) == 0:
            print("No users found with email")
            return None

        fetched_user = user_info[0]

        return DatabaseUserModel(fetched_user[0], fetched_user[1], fetched_user[2], fetched_user[3])

    def upsert_user_to_database(self, email, password, first_name, last_name):
        if not password:
            print("Password was never set")
            return
        if not first_name:
            print("First Name was never set")
            return
        if not last_name:
            print("Last Name was never set")
            return
        upsert_user_query = """
            INSERT INTO users
            VALUES (%s, %s, %s, %s)
        """
        user_data_to_upsert = (email, password, first_name, last_name)
        with self.database.cursor() as cursor:
            cursor.execute(upsert_user_query, user_data_to_upsert)
            self.database.commit()
        print("User successfully upserted to database")
        return None

