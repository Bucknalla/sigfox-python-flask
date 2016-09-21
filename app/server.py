from flask import Flask, request, jsonify, render_template
import flask_login
from pymongo import MongoClient
from basicauth import decode
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
    date = content['values'][0]['date']
    temp = content['values'][0]['value']
    hum = content['values'][1]['value']

    # time = int(content['time'])
    payload = {'date': date, 'temp': temp, 'humidity' : hum}
    # content['time'] = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    try:
        data_id = data.insert_one(payload).inserted_id
    except:
        print 'Error loading data into collection'
        return('', 400)

    print date
    print temp
    return('', 200)


@app.route('/', methods=['GET'])
def load_data():

    mydataset = list(db.data.find().sort("_id",1).limit(10))

    temperature = []
    humidity = []
    dates = []

    for mydata in mydataset:

        humidity.append(float(mydata['humidity']))
        temperature.append(float(mydata['temp']))
        dates.append(mydata['date'])
        

    # return jsonify(bats=battery,hums=humidity,temps=temperature,airs=airquality,dates=timeStore)
    # return render_template("index.html",bats=battery,hums=humidity,temps=temperature,airs=airquality,dates=timeStore)
    return render_template("index.html",hum=humidity,temps=temperature,dates=dates)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # port = 2000
    app.run(host= '0.0.0.0', port=port ,debug=True)
