import flask
from flask_socketio import join_room, leave_room, send
import models
# we need both app and socketio
from init import app, db, socketio

names = []
totalUsers = models.User.query.filter_by(roomName = "user-5").all()
print('length of ' + str(len(totalUsers)))
for a in totalUsers:
    names.append(a.name)

for a in names:
    print(a)
