from flask import Flask, request, jsonify, render_template
from flask.ext.basicauth import BasicAuth
from pymongo import MongoClient
import os
import json
import datetime

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'SIGFOX'
app.config['BASIC_AUTH_PASSWORD'] = 'twitterbird2016'
basic_auth = BasicAuth(app)

client = MongoClient(os.getenv("MONGODB_ADDON_URI"))
db = client.bkkui1juebikood
print 'Connected to Database...'
collection = db.tempCollection
data = db.data
# client = MongoClient()
# db = client.tempDatabase
# print 'Connected to Database...'
# print db
# collection = db['tempCollection']
# print 'Connected to Collection...'

@app.route('/data', methods=['POST'])
@basic_auth.required
def update_webpage():

    content = request.json
    device = content['device']
    time = int(content['time'])
    content['time'] = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    print content
    try:
        data_id = data.insert_one(content).inserted_id
    except:
        print 'Error loading data into collection'
        return('', 400)

    print device
    print data_id
    return('', 200)


@app.route('/', methods=['GET'])
def load_data():

    mydataset = list(db.data.find().sort("_id",-1).limit(10))

    temperature = []
    humidity = []
    airquality = []
    timeStore = []
    battery = []

    # print mydata
    for mydata in mydataset:
        battery.append(mydata['bat'])
        humidity.append(mydata['hum'])
        temperature.append(mydata['temp'])
        airquality.append(mydata['air'])
        timeStore.append(mydata['time'])

    return render_template("index.html",bats=battery,hums=humidity,temps=temperature,airs=airquality,dates=timeStore)

if __name__ == '__main__':
    # port = int(os.environ.get('PORT', 5000))
    port = 2000
    app.run(host= '0.0.0.0', port=port ,debug=True)
