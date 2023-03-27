from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/login_user/<email>', methods=['POST'])
def login_user(email, password):
    from db.model.database_user import DatabaseUserModel
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
    from db.model.database import Database
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

@app.route('/read_data/<com_port>', methods=['GET', 'POST'])
def read_data(com_port):
    import serial
    from serial.tools import list_ports
    import itertools

    #check if com port provided is valid
    comport_list = [c.name for c in list_ports.comports()]
    if com_port not in comport_list:
        return jsonify({'success': False, 'error': 'Comport not available on this PC. Maybe re-pair...'})
    with serial.Serial(port=com_port, baudrate=9600) as ser:
        data_list = list(itertools.islice(map(lambda x: x.decode().split(), ser), 3000))
    return jsonify({'success': True, 'data': data_list})
    
@app.route('/data_filter', methods=['GET', 'POST'])
def data_filter(data_list):
    import math 
    import numpy as np
    import scipy 
    from scipy.signal import butter
    from scipy.signal import lfilter
    from scipy.signal import freqz
    from scipy.signal import find_peaks
    import matplotlib.pyplot as plt

    emg1, emg2, emg3, accx, accy, accz = [], [], [], [], [], []
    emg1 = np.array([float (row[0]) for row in data_list])
    emg2 = np.array([float (row[1]) for row in data_list])
    emg3 = np.array([float (row[2]) for row in data_list])
    accx = np.array([float (row[3]) for row in data_list])
    accy = np.array([float (row[4]) for row in data_list])
    accz = np.array([float (row[5]) for row in data_list])

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
    Band = np.dot((2/100),[20, 350]) #bandpass - low end: 20 mV, high end: 350 mV (to eliminate Gaussian noise)
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

    mean_data = np.column_stack((emg1_mean, emg2_mean, emg3_mean, P4))

    return jsonify({'success': True, 'data_list': mean_data})
