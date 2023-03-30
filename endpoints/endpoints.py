from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from database import User, db

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
def data_filter(data_list):
    import numpy as np
    import scipy 
    from scipy.signal import butter
    import pandas as pd

    arr = np.array(data_list, dtype=object)
    emg1, emg2, emg3, accx, accy, accz = [], [], [], [], [], []
    emg1 = np.array([float (row[0]) for row in arr])
    emg2 = np.array([float (row[1]) for row in arr])
    emg3 = np.array([float (row[2]) for row in arr])
    accx = np.array([float (row[3]) for row in arr])
    accy = np.array([float (row[4]) for row in arr])
    accz = np.array([float (row[5]) for row in arr])

    a1 = accx[:3000] #cut accx to 30 seconds
    a2 = accy[:3000] #Cut accy to 30 seconds
    a3 = accz[:3000] #cut accz to 30 seconds
    e1 = emg1[:3000] #cut emg1 to 30 seconds
    e2 = emg2[:3000] #cut emg2 to 30 seconds
    e3 = emg3[:3000] #cut emg3 to 30 seconds

    # Write a function to process EMG
    sampling_rate = 1000 #1000 samples per second (Hz)

    #convert the raw emg signal to mV
    e1 = (((e1/1034-0.5)*3.3)/1009)*100 
    e2 = (((e2/1034-0.5)*3.3)/1009)*100
    e3 = (((e3/1024-0.5)*3.3)/1009)*100 
    time = np.arange(0.001, 10.001, 0.001) #for plotting with time

    # bandpass butterworth filter (20-350Hz), rectified signal for emg
    Band = np.dot((2/1000),[20, 350]) #bandpass - low end: 20 mV, high end: 350 mV (to eliminate Gaussian noise)
    B, A = scipy.signal.butter(2, Band, 'Bandpass') #second order butterworth bandpass filter
    emg1_filt = scipy.signal.filtfilt(B, A, e1)
    emg2_filt = scipy.signal.filtfilt(B, A, e2)
    emg3_filt = scipy.signal.filtfilt(B, A, e3)

    #Butterworth filter for ACC data
    Fn = sampling_rate / 2
    passband = np.array([5.0, 20])/Fn
    stopband = np.array([0.1, 40])/Fn 
    passripple = 1
    stopripple = 10

    C, D = scipy.signal.buttord(passband, stopband, passripple, stopripple, analog=False,fs=None)
    acc1_filt = scipy.signal.filtfilt(D, C, a1)
    acc2_filt = scipy.signal.filtfilt(D, C, a2)
    acc3_filt = scipy.signal.filtfilt(D, C, a3)

    filtered_data = np.column_stack((acc1_filt, emg1_filt, emg2_filt, emg3_filt))

    emg1_mean = abs(np.mean(emg1_filt))
    emg2_mean = abs(np.mean(emg2_filt))
    emg3_mean = abs(np.mean(emg3_filt))


    acc_mean = abs(np.mean(acc1_filt, acc2_filt, acc3_filt))

    Y4 = np.fft.fft(acc_mean)
    PD = np.abs(Y4/3000)
    P4 = PD[:int(3000/2+1)]
    P4 = 2*P4
    
    #mean_data = [emg1_mean, emg2_mean, emg3_mean, P4]
    list = [[emg1_mean, emg2_mean, emg3_mean, P4]]
    df = pd.DataFrame(list, columns=['EMG 1', 'EMG 2', 'EMG 3', 'ACC'], dtype= float)
    
    return jsonify({'success': True, 'data_list': df})
