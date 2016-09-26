from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, models, forms
# from run import socketio

from forms import LoginForm, SignUpForm
from models import User 
import random, datetime
from hashlib import md5

from flask_socketio import join_room, leave_room, send, emit

from random import random

MAX_PLAYERS = 2

class Gamestate(object):
    def __init__(self):
        super(Gamestate, self).__init__()
        self.room = 0
        self.num_players = 0
        self.turn = 0

class GameSessionManager(object):
    def __init__(self):
        super(GameSessionManager, self).__init__()
        self.games = {}

    def add_game(self, id):
        self.games[id] = Gamestate()

    def game_ids(self):
        return self.games.keys()

    def get_game(self, id):
        return self.games[id]

GM = GameSessionManager()

@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods =  ['GET', 'POST'])
@app.route('/index', methods =  ['GET', 'POST'])
@app.route('/rooms', methods =  ['GET', 'POST'])
def index():
    user = g.user
    if g.user is None or not g.user.is_authenticated:
        return redirect(url_for('login'))

    return render_template('index.html',
        games=GM.game_ids(),
    )


@lm.user_loader
def load_user(id):
    return models.User.query.filter_by(id=id).first()


@app.route('/login', methods =  ['GET', 'POST'])
def login():

    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form_l = LoginForm()
    form_s = SignUpForm()

    if form_l.validate_on_submit() and (len(form_l.openid.data) < 100) and (len(form_l.password.data) < 100):
        session['remember_me'] = form_l.remember_me.data
        user = db.session.query(User).filter(User.email == form_l.openid.data).filter(User.password == md5(form_l.password.data).hexdigest()).first()
        if user is not None:
            login_user(user, remember = form_l.remember_me.data)
            return redirect(url_for('index'))
        else:
            print("NOT FOUND")

    if form_s.validate_on_submit() and (len(form_s.email.data) < 100) and (len(form_s.login.data) < 50) and (len(form_s.password.data) < 100):
        k = False
        user = db.session.query(User).filter(User.email == form_s.email.data  or  User.nickname == form_s.login.data).first()
        if user is None:
            u = User(nickname=form_s.login.data, email=form_s.email.data, password=md5(form_s.password.data).hexdigest())
            db.session.add(u)
            db.session.commit()
#            db.session.add(u.follow(u))
#            db.session.commit()
            login_user(u)
            return redirect(url_for('index'))
        else:
            print("EXISTS")

    return render_template('login.html',
        form_l = form_l,
        form_s = form_s)


@app.route('/logout')
def logout():
    logout_user()
    print ("successfully logged out")
    return redirect(url_for('login'))


@app.route('/fighted')
def fighted():
    users = g.user.follows_you().all()
    return render_template("followers.html",
        users = users,
        user = g.user)


@app.route('/game/<game_id>')
def game(game_id):
    game_id = int(game_id)
    if not game_id in GM.game_ids():
        return redirect(url_for('index', games=GM.game_ids()))
    else:
        game = GM.get_game(game_id)
        if game.num_players < MAX_PLAYERS:
            game.num_players += 1
        else:
            redirect(url_for('index', games=GM.game_ids()))

    return render_template('game.html', game_id=game_id)


@app.route('/create_game')
def create_game():
    id = hash(random())
    GM.add_game(id)
    return redirect(url_for('game', game_id=id))


''' @socketio.on('connect', namespace='/ws')
def on_connect(data):
    emit('Responce', {'data': 'got it!'})

def ack():
    print 'Delivered'

@socketio.on('connect', namespace='/ws')
def test_connect():
    print "CONNECTED"

@socketio.on('join', namespace='/ws')
def on_join(data):
    username = g.user.nickname
    game_id = room = data['room']
    emit('join', username + ' has entered the room.', room=room,
                                                    namespace='/ws',
                                                    broadcast=True,
                                                    callback=ack)

    game = GM.get_game(game_id)
    game.room = room if game.room != 0 else game.room

    join_room(room)

@socketio.on('leave', namespace='/ws')
def on_leave(data):
    username = g.user.nickname
    game_id = room = data['room']
    emit('join', username + ' has left the room.', room=room,
                                                    namespace='/ws',
                                                    broadcast=True,
                                                    callback=ack)
    game = GM.get_game(game_id)
    game.players.remove(username)
    leave_room(room)
'''
