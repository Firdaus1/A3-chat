import hashlib
import datetime
from init import app, db

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///A3.db'
class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    pw_hash = db.Column(db.String(50))
    roomName = db.Column(db.String(50),default=None)
    tempRoomAssign = db.Column(db.String(50),default=None)
    wantToCreate = db.Column(db.Boolean, default=False)
db.create_all(app=app)