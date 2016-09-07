from flask import Flask, request, jsonify, render_template
import datetime

app = Flask(__name__)

tempStore = []
dateStore = []

@app.route('/data/<sensor>', methods=['POST'])
def add_message(sensor):

    content = request.json
    time = int(content['time'])
    time = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    tempStore.append(content['temp'])
    dateStore.append(time)
    if len(tempStore) > 10:
        del tempStore[0]
        del dateStore[0]
    print tempStore
    print time
    print content['device']
    return ('', 200)

@app.route('/')
def show_graph():

    return render_template('index.html', temps=tempStore, dates=dateStore)

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
