from flask import Flask
from flask import render_template
from apiClient import Client
import os

app = Flask(__name__)


SLID_TOKEN_ENV = "slid_token"

def get_devices():
    slid_token = os.environ.get(SLID_TOKEN_ENV)
    client = Client(slid_token=slid_token)
    user_info = client.get_user_info()
    for device in user_info["devices"]:
        device["obd_params"] = client.get_obd_params(device["device_id"])["obd_params"]
    return user_info

@app.route('/')
def main():

    return render_template('obd.html', model = get_devices())

@app.route('/json')
def json():
    return get_devices()



if __name__ == '__main__':
    app.run()
