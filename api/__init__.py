# import os
# import uuid
#
# import firebase_admin
# from dotenv import load_dotenv, dotenv_values
# from firebase_admin import credentials, firestore, storage
# from flask import Flask
# from flask_restful import Api
# from flask_sqlalchemy import SQLAlchemy
#
# from api.config import Config
#
# load_dotenv()
#
# firebase_cred = {
#     "type": os.getenv("FIREBASE_TYPE"),
#     "project_id": os.getenv("FIREBASE_PROJECT_ID"),
#     "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
#     "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
#     "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
#     "client_id": os.getenv("FIREBASE_CLIENT_ID"),
#     "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
#     "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
#     "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
#     "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
# }
#
# cred = credentials.Certificate(firebase_cred)
# firebase_admin.initialize_app(cred, {'storageBucket': f"{os.getenv('FIREBASE_PROJECT_ID')}.appspot.com"})
# bucket = storage.bucket()
#
# db = SQLAlchemy()
#
# uuid = uuid
#
#
# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_mapping(dotenv_values())
#     db.init_app(app)
#
#     from api import models
#
#     with app.app_context():
#         db.drop_all()
#         db.create_all()
#
#     api = Api(app)
#
#     from api.resource import UserResource
#     api.add_resource(UserResource, "/api/user")
#
#     from api.resource import Quest
#     api.add_resource(Quest, "/api/quest")
#
#     return app
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import hmac
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
SECRET_KEY = "6329580650:AAFy9JCT62aHwTVqHJDFCwfG9skvw_MEiEw"
BOT_USERNAME = 'kazan_game_bot'


def check_auth(data):
    hash_str = data.pop('hash')
    sorted_data = sorted(data.items())
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_data])
    secret_key = hashlib.sha256(SECRET_KEY.encode()).digest()
    h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
    return h.hexdigest() == hash_str


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    if check_auth(data):
        session['authenticated'] = True
        session['username'] = data['username']
        return jsonify({"status": "authenticated", "username": data['username']})
    else:
        session['authenticated'] = False
        return jsonify({"status": "error", "message": "you are hacker"})


if __name__ == "__main__":
    app.run(debug=True)
