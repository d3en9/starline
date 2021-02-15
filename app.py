from flask import Flask
from flask import render_template
from apiClient import Client
import redis
import os
from datetime import datetime, timedelta
from config import *

app = Flask(__name__)


def _get_client():
    slid_token = os.environ.get(SLID_TOKEN_KEY)

    if slid_token:
        return Client(slid_token=slid_token)
    else:
        r = redis.Redis(host=REDIS_HOST, decode_responses=True)
        slid_token = r.get(SLID_TOKEN_KEY)
        if slid_token:
            return Client(slid_token=slid_token)
    app_id = os.environ.get(APP_ID_KEY)
    app_secret = os.environ.get(APP_SECRET_KEY)
    user_login = os.environ.get(USER_LOGIN_KEY)
    user_password = os.environ.get(USER_PASSWORD_KEY)
    client = Client(app_id, app_secret, user_login, user_password)
    client.auth()
    r = redis.Redis(host=REDIS_HOST)
    slid_token = r.set(SLID_TOKEN_KEY, client.slid_token, ex=364 * 24 * 60 * 60)
    return client


def _get_devices():
    client = _get_client()
    user_info = client.get_user_info()
    for device in user_info["shared_devices"]:
        device["obd_params"] = client.get_obd_params(device["device_id"])["obd_params"]
    return user_info


@app.route('/')
def main():
    return render_template('obd.html', model=_get_devices())


@app.route('/json')
def json():
    return _get_devices()


if __name__ == '__main__':
    app.run()
