import flask
from flask_socketio import join_room, leave_room, send
import models
# we need both app and socketio
from init import app, db, socketio
import datetime


def check_request():
    token = flask.session['csrf_token']
    if flask.request.form['_csrf_token'] != token:
        app.logger.warn('invalid CSRF token')
        flask.abort(400)
    if flask.session.get('auth_user') != int(flask.request.form['initiator_id']):
        app.logger.warn('requesting user %s not logged in (%s)',
                        flask.request.form['initiator_id'],
                        flask.session.get('auth_user'))
        flask.abort(403)

@socketio.on('connect')
def on_connect():
    # get the connecting user's user ID
    # flask.session works in socket IO handlers :)
        uid = flask.session.get('auth_user', None)
        if uid is None:
            app.logger.warn('received socket connection from unauthed user')
            return

        user = models.User.query.filter_by(id = uid).first()
        if user.wantToCreate is True:
            print("a user used create new room feature")
            app.logger.info('new client connected for user %d', uid)
            # add this connection to the user's 'room', so we can send to all
            # the user's open browser tabs
            socketio.emit('message', user.name + " connected to room: " + user.roomName, room=user.roomName)
            socketio.emit("users",user.name,room=user.roomName)
            join_room(user.roomName)
            user.wantToCreate = False
        if user.tempRoomAssign is not None:
            user.roomName = user.tempRoomAssign
            app.logger.info('new client connected for user %d', uid)
            print("A user joined room " + user.roomName)
            # add this connection to the user's 'room', so we can send to all
            # the user's open browser tabs
            send(user.name + " joined the room: " + user.tempRoomAssign, room=user.tempRoomAssign)
            socketio.emit("users",user.name,room=user.tempRoomAssign)
            join_room(user.tempRoomAssign)
            user.tempRoomAssign = None
            db.session.commit()
        #create a new room
        else:
            return


@socketio.on('disconnect')
def on_disconnect():
    app.logger.info('client disconnected')

# app.route says 'call function when this URL is requested'
@app.route('/index', methods=['POST'])
def mainChat():
    roomName = flask.request.form['roomCreate']
    check = models.User.query.filter_by(roomName = roomName)
    if check is not None:
        flask.render_template('homepage.html', check = 0)
    id = flask.session.get('auth_user', None)
    user = models.User.query.filter_by(id = id).first()
    name = user.name
    user.roomName = roomName
    user.wantToCreate = True
    db.session.commit()
    return flask.render_template('index.html', roomName = str(roomName), singleName = name)

@app.route('/index/leave')
def on_leave():
    uid = flask.session.get('auth_user',None)
    user = models.User.query.filter_by(id=uid).first()
    username = user.name
    room = user.roomName
    print(username + ' has left the room')
    user.roomName = None
    db.session.commit()
    socketio.emit("message",username + ' has left the room.', room=room)
    return flask.render_template('homepage.html')
    #send(username + ' has left the room.', room=room)

@app.route('/joinRoom', methods=['POST'])
def handle_joinRoom():
    uid = flask.session.get('auth_user',None)
    user = models.User.query.filter_by(id= uid).first()
    roomAssign = flask.request.form['roomAssign']
    user.tempRoomAssign = str(roomAssign)
    singleName = user.name
    user.wantToCreate = False;
    db.session.commit()

    names = []
    totalUsers = models.User.query.filter_by(roomName = roomAssign).all()
    for a in totalUsers:
        names.append(a.name)
    #temp = "user-" + str(roomAssign)
    #join_room("user-" + str(roomAssign))

    return flask.render_template('index.html', roomName = str(roomAssign),singleName = singleName, names = names)

# socketio.on says 'call function when this kind of event comes in'
@socketio.on('message')
def message(msg):
    # since this is a 'message' event, msg is a string
    # if it were on event 'json', it would be json

    uid = flask.session.get('auth_user',None)
    user = models.User.query.filter_by(id=uid).first()
    room = user.roomName
    # get response from eliza
    print(msg + " at room : " + str(room))
    today = datetime.datetime.today().replace(microsecond=0)
    msg = user.name + ": " + msg + "     posted on " + str(today)
    # send it to client
    # flask_socketio.send sends a message to whatever client called us

    #socketio.emit('chat message', {room:room, msg: msg})
    #socketio.emit("message",msg, room=room)
    #socketio.emit(msg, room=room)
    send(msg, room=room)

