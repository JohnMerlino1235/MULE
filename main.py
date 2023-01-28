from mysql.connector import connect, Error
from model.user import User
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    newUser = User("testemail@gmail.com", "testPassword", "testFirstName", "testLastName")
    test = newUser.fetch_user_from_database()
    # try:
    #     conn = connect(
    #         host='localhost',
    #         user='root',
    #         password='rootroot',
    #         database='lams'
    #     )
    # except Error as e:
    #     print(e)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
