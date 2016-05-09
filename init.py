import os.path
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

app = flask.Flask(__name__)
db = SQLAlchemy(app)

app.config.from_pyfile('settings.py')

socketio = SocketIO(app)

recip_sockets = {}