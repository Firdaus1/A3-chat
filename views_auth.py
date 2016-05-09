import flask
import bcrypt
from init import app, db
import models


@app.route('/login')
def login_form():
    # GET request to /login - send the login form
    return flask.render_template('login.html')

@app.route('/logout')
def logout():
    # GET request to /login - send the login form
    del flask.session['auth_user']
    return flask.render_template('login.html')


@app.route('/login', methods=['POST'])
def handle_login():
    # POST request to /login - check user
    email = flask.request.form['email']
    password = flask.request.form['password']
    # try to find user
    user = models.User.query.filter_by(email=email).first()
    if user is not None:
        # hash the password the user gave us
        # for verifying, we use their real hash as the salt
        pw_hash = bcrypt.hashpw(password.encode('utf8'), user.pw_hash)
        # is it good?
        if pw_hash == user.pw_hash:
            # yay!
            flask.session['auth_user'] = user.id
            # And redirect to '/', since this is a successful POST
            user.roomName = None
            user.tempRoomAssign = None
            user.wantToCreate = None
            return flask.redirect(flask.request.form['url'], 303)

    # if we got this far, either username or password is no good
    # For an error in POST, we'll just re-show the form with an error message
    return flask.render_template('landing.html', error="Invalid username or password")


@app.route('/create_user', methods=['POST'])
def create_user():
    email = flask.request.form['email']
    name = flask.request.form['name']
    password = flask.request.form['password']
    # do the passwords match?
    error = None
    if password != flask.request.form['confirm']:
        error = "Passwords don't match"
    # is the login ok?
    if len(email) > 100:
        error = "E-mail address too long"
    # search for existing user
    existing = models.User.query.filter_by(email=email).first()
    if existing is not None:
        # oops
        error = "Username already taken"

    if error:
        return flask.render_template('landing.html', error=error)

    # create user
    user = models.User()
    user.email = email
    user.name = name
    # hash password
    user.pw_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(15))

    # save user
    db.session.add(user)
    db.session.commit()

    flask.session['auth_user'] = user.id

    # It's all good!
    return flask.redirect(flask.url_for('index'), 303)