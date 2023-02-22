from db.model.database import Database
from db.model.database_user import DatabaseUserModel
from flask import Flask, jsonify
from flask_cors import CORS

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
    # to determine if a user has a valid account, we must fetch their username from the database.
    user_database_model = DatabaseUserModel(email, password)
    fetched_user_from_db = user_database_model.fetch_user_from_database()
    if not fetched_user_from_db:
        print("ERROR:login_user: User not found in database")
        response = jsonify({'success': False, 'error': 'User not found in database'})
        return response
    if password != fetched_user_from_db.password:
        print("ERROR:login_user: User passwords do not match")
        response = jsonify({'success': False, 'error': 'User passwords do not match'})
        return response

    # since passwords match, we can return user info
    print("login_user: User logged in with following details ", fetched_user_from_db.email,
          fetched_user_from_db.password, fetched_user_from_db.first_name, fetched_user_from_db.last_name)
    reponse = jsonify({'success': True, 'email': fetched_user_from_db.email, 'password': fetched_user_from_db.password,
                       'first_name': fetched_user_from_db.first_name, 'last_name': fetched_user_from_db.last_name})
    return reponse

@app.route('/sign_up', methods=['POST'])
def sign_up(email, password, first_name, last_name):
    database_connection = Database()

    # to ensure this user does not already have an account, we can do a quick db fetch based on the input email
    user = database_connection.fetch_user_by_email(email)
    if user:
        print("sign_up: User already registered in Database with email: ", email)
        response = jsonify({'success': False, 'error': 'User already registered in Database with input email'})
        return response

    # if user is not populated: we can proceed to upsert the user into our database - creating their account and
    # storing their information
    database_connection.upsert_user_to_database(email, password, first_name, last_name)
    print("sign_up: User successfully registered in Database with credentials", email, password, first_name, last_name)
    response = jsonify({'success': True, 'email': email, 'password': password, 'first_name': first_name, 'last_name': last_name})
    return response

@app.route('/device_pairing', methods=['POST'])
def device_pairing():
    from time import sleep
    from serial.tools import list_ports
    #figure out which com port the device is associated with
    #by checking available com ports before and after device is plugged in.
    comport_list_pre_plugin = list(list_ports.comports())
    print("Please plug in device now!")
    cnt = 0
    #give the user 30 seconds to plug the device in before exiting
    while True:
        #check for a timeout
        if cnt >= 30:
            print('Did not detect device...')
            return jsonify({'success': False, 'error': 'No device detected...'})
        #check if the available ports have changed
        comport_list_post_plugin = list(list_ports.comports())
        if len(comport_list_pre_plugin) < len(comport_list_post_plugin):
            for c in comport_list_post_plugin:
                if c not in comport_list_pre_plugin:
                    comport_name = c.name
                    break
            break
        cnt += 1
        sleep(1)
    return jsonify({'success': True, 'comport_name': comport_name})

@app.route('/read_data', methods=['POST'])
def read_data(com_port):
    import serial
    from serial.tools import list_ports
    #check if com port provided is valid
    comport_list = list(list_ports.comports())
    if com_port not in comport_list:
        return jsonify({'success': False, 'error': 'Comport not available on this PC. Maybe re-pair...'})
    #read data from com port
    ser = serial.Serial(port=com_port, baudrate=9600)
    num_data_points = 0
    data_list = []
    while(num_data_points < 100):
        data = ser.readline()
        decoded_data = data.decode()
        data_list.append(decoded_data)
        num_data_points += 1
    ser.close()
    return jsonify({'success': True, 'data': data_list})
    