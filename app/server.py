from flask import Flask, request, jsonify, render_template
import flask_login
from pymongo import MongoClient
from basicauth import decode
from bitstring import BitArray, BitStream
import os
import json

app = Flask(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

client = MongoClient(os.getenv("MONGODB_ADDON_URI"))
print client
db = client.bkkui1juebikood
print 'Connected to Database...'
data = db.data

class User(flask_login.UserMixin):
    # proxy for a database of users
    user_database = {os.getenv("TWITTER_USER"): (os.getenv("TWITTER_USER"), os.getenv("TWITTER_PASS"))}


    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls,id):
        return cls.user_database.get(id)

@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username, password = decode(token)
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0],user_entry[1])
            if (user.password == password):
                return user
    return None

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401


@app.route('/data', methods=['POST'])
@flask_login.login_required
def update_webpage():

    print flask_login.current_user.id
    content = request.json
    # device = content['device']
    datePayload = content['time']
    deviceIdPayload = content['deviceId']
    tempPayload = int(content['data']['temp'])
    humPayload = int(content['data']['hum'])
    battPayload = int(content['data']['batt'])
    modePayload = int(content['data']['mode'])

    batt = decodeBattery(modePayload,battPayload)
    temp = decodeTemperature(battPayload,tempPayload)
    hum = decodeHumidity(humPayload)
    mode = decodeMode(modePayload)

    # time = int(content['time'])
    payload = {'mode': mode, 'temperature': round(temp,2), 'humidity' : hum, 'battery' : round(batt,2), 'date' : datePayload, 'deviceId' : deviceIdPayload}

    print payload
    # content['time'] = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    try:
        data_id = data.insert_one(payload).inserted_id
    except:
        print 'Error loading data into collection'
        return('', 400)

    return('', 200)


@app.route('/', methods=['GET'])
def load_data():

    mydataset = list(db.data.find().sort("_id",1).limit(10))

    temperature = []
    humidity = []
    battery = []
    dates = []

    for mydata in mydataset:

        humidity.append(float(mydata['humidity']))
        temperature.append(float(mydata['temperature']))
        battery.append(mydata['battery'])
        dates.append(mydata['date'])


    # return jsonify(bats=battery,hums=humidity,temps=temperature,airs=airquality,dates=timeStore)
    # return render_template("index.html",bats=battery,hums=humidity,temps=temperature,airs=airquality,dates=timeStore)
    return render_template("index.html",hum=humidity,temps=temperature,dates=dates, batts=battery)

def decodeBattery(byte1,byte2):
    byte1 = BitArray(uint=byte1, length=8)
    byte2 = BitArray(uint=byte2, length=8)
    batt = byte1[0:1] + byte2[0:4]
    battery = batt.uint * 0.05 * 2.7
    return battery

def decodeTemperature(byte2,byte3):
    byte2 = BitArray(uint=byte2, length=8)
    byte3 = BitArray(uint=byte3, length=8)
    temp = byte2[4:] + byte3[2:]
    temperature = (temp.uint - 200) / 8
    return temperature

def decodeHumidity(byte4):
    humidity = byte4 * 0.5
    return humidity

def decodeMode(byte1):
    byte1 = BitArray(uint=byte1, length=8)
    mode = byte1[5:]
    timeframe = byte1[3:5]
    typeAction = byte1[1:4]
    print mode
    print timeframe
    print typeAction
    modeList = [mode.uint,timeframe.uint,typeAction.uint]
    return modeList

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # port = 2000
    app.run(host= '0.0.0.0', port=port ,debug=True)
