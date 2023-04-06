from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from database import User, Data, db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["content-type"])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.database'

db.init_app(app)
with app.app_context():
    db.create_all()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
    response.headers.add("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    return response

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        print("ERROR:login: User not found in database")
        return jsonify({'success': False, 'message': 'User not found in database'})
    if password != user.password:
        print("ERROR:login: User passwords do not match")
        return jsonify({'success': False, 'message': 'Passwords do not match'})

    print(f'SUCCESS:login: {email} has logged in!')
    return jsonify({'success': True})

@app.route('/signup', methods=['POST'])
def signup():
    email = request.json.get('email')
    password = request.json.get('password')
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')

    # Check if user already exists in database
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print("ERROR:singup: User already exists in database")
        return jsonify({'success': False, 'message': 'User already exists in database'})

    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    print(f'SUCCESS:signup: {email} has signed up!')
    return jsonify({"success": True})

@app.route('/changepassword', methods=['POST'])
def changepassword():
    email = request.json.get('email')
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')

    user = User.query.filter_by(email=email).first()

    if not user:
        print("ERROR:changepassword: User not found in database")
        return jsonify({'success': False, 'message': 'User not found in database'})

    if old_password != user.password:
        print("ERROR:changepassword: Old password does not match password from database")
        return jsonify({'success': False, 'message': 'Old password does not match password from database'})

    if new_password == user.password:
        print("ERROR:changepassword: New password matches old password")
        return jsonify({'success': False, 'message': 'New password matches old password'})

    user.password = new_password
    db.session.commit()
    print(f'SUCCESS:changepassword: {email} changed their password')
    return jsonify({"success": True})

@app.route('/device_pairing', methods=['GET', 'POST'])
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

@app.route('/read_data', methods=['GET', 'POST'])
def read_data():
    import serial
    from serial.tools import list_ports
    import itertools
    com_port = request.json.get('com_port')

    #check if com port provided is valid
    comport_list = [c.name for c in list_ports.comports()]
    if com_port not in comport_list:
        return jsonify({'success': False, 'error': 'Comport not available on this PC. Maybe re-pair...'})
    with serial.Serial(port=com_port, baudrate=9600) as ser:
        data_list = list(itertools.islice(map(lambda x: x.decode().split(), ser), 3000))
    return jsonify({'success': True, 'data': data_list})
    
@app.route('/data_filter', methods=['GET', 'POST'])
def data_filter():
    import numpy as np
    import scipy 
    from scipy.signal import butter
    from datetime import datetime
    import pandas as pd
    email = request.json.get('email')
    data_list = request.json.get('data_list')
    data_list = data_list[100:2900]

    arr = np.array(data_list, dtype=object)
    emg1, emg2, emg3 = [], [], []
    for row in arr:
        try:
            emg1_val = float(row[0])
            emg2_val = float(row[1])
            emg3_val = float(row[2])
            emg1.append(emg1_val)
            emg2.append(emg2_val)
            emg3.append(emg3_val)
        except:
            continue
    emg1 = np.array(emg1)
    emg2 = np.array(emg2)
    emg3 = np.array(emg3)

    e1 = emg1[:3000] #cut emg1 to 30 seconds
    e2 = emg2[:3000] #cut emg2 to 30 seconds
    e3 = emg3[:3000] #cut emg3 to 30 seconds

    #convert the raw emg signal to mV
    e1 = (((e1/1034-0.5)*3.3)/1009)*100 
    e2 = (((e2/1034-0.5)*3.3)/1009)*100
    e3 = (((e3/1024-0.5)*3.3)/1009)*100 

    # bandpass butterworth filter (20-350Hz), rectified signal for emg
    Band = np.dot((2/1000),[20, 350]) #bandpass - low end: 20 mV, high end: 350 mV (to eliminate Gaussian noise)
    B, A = scipy.signal.butter(2, Band, 'Bandpass') #second order butterworth bandpass filter
    emg1_filt = scipy.signal.filtfilt(B, A, e1)
    emg2_filt = scipy.signal.filtfilt(B, A, e2)
    emg3_filt = scipy.signal.filtfilt(B, A, e3)

    emg1_mean = abs(np.mean(emg1_filt))
    emg2_mean = abs(np.mean(emg2_filt))
    emg3_mean = abs(np.mean(emg3_filt))
    
    mean_data = [emg1_mean, emg2_mean, emg3_mean]

    new_data = Data(email=email,
                    emg_1=emg1_mean,
                    emg_2=emg2_mean,
                    emg_3=emg3_mean,
                    time_recorded=datetime.utcnow())
    db.session.add(new_data)
    db.session.commit()
    
    return jsonify({'success': True, 'data_list': mean_data})

@app.route('/get_data', methods=['GET', 'POST'])
def get_data():
    import numpy as np
    import matplotlib.pyplot as plt

    email = request.json.get('email')
    found_user_data = Data.query.filter_by(email=email).order_by(Data.time_recorded).all()
    if not found_user_data:
        print(f'ERROR:get_data: {email} has no data stored in database')
        return jsonify({'success': False, 'message': "No data found for user"})

    data_list = [d.__dict__ for d in found_user_data]

    print(f'SUCCESS:get_data: Data found for {email}')

    emg1 = np.array()
    emg2 = np.array()
    emg3 = np.array()
    time = []
    for entry in found_user_data:
        np.append(emg1, entry.emg_1)
        np.append(emg2, entry.emg_2)
        np.append(emg3, entry.emg_3)
        time.append(entry.time_recorded)

    plt.plot(time,emg1,label='Quadriceps')
    plt.plot(time,emg2,label='Vastus Lateralis')
    plt.plot(time,emg3,label='Soleus')
    plt.xlabel('Exercise Date')
    plt.ylabel('Muscle Activation')
    plt.show()

    return jsonify({'success': True, 'user_data': data_list})