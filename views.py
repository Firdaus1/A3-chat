import flask
import base64, os

from init import app,db
import models

@app.before_request
def setup_csrf():
    # make a cross-site request forgery preventing token
    if 'csrf_token' not in flask.session:
        flask.session['csrf_token'] = base64.b64encode(os.urandom(32)).decode('ascii')


@app.before_request
def setup_user():
    """
    Figure out if we have an authorized user, and look them up.
    This runs for every request, so we don't have to duplicate code.
    """
    if 'auth_user' in flask.session:
        user = models.User.query.get(flask.session['auth_user'])
        if user is None:
            # old bad cookie, no good
            del flask.session['auth_user']
        # save the user in `flask.g`, which is a set of globals for this request
        flask.g.user = user


@app.route('/')
def index():
    if 'auth_user' in flask.session:
        uid = flask.session['auth_user']
        app.logger.info('rendering homepage for user %d', uid)
        user = models.User.query.filter_by(id=uid).first()
        user.roomName = None
        user.tempRoomAssign = None
        user.wantToCreate = False
        db.session.commit()
        return flask.render_template('homepage.html')
    else:
        return flask.render_template('landing.html')

import views_auth