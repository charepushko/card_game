#! /usr/bin/python
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, models, forms

from app.forms import LoginForm, SignUpForm
from app.models import User

import random, datetime
from random import random, randint
import json
from hashlib import md5

from flask_socketio import SocketIO, join_room, leave_room, send, emit


socketio = SocketIO(app)

MAX_PLAYERS = 2

class Gamestate(object):
    def __init__(self):
        super(Gamestate, self).__init__()
        self.room = 0
        self.num_players = 0
        self.turn = True
	self.creator = 0
	self.round = 0
        self.players = []
	self.used_cards = [0 for i in range(40)]
	self.score = [0 for i in range(42)]

    def get_creator(self):
        u = load_user(self.creator)
        return u.nickname


class GameSessionManager(object):
    def __init__(self):
        super(GameSessionManager, self).__init__()
        self.games = {}

    def add_game(self, id):
        self.games[id] = Gamestate()

    def game_ids(self):
        return self.games #.keys()

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

#    return render_template('game.html', game_id=game_id)
    return render_template('front.html', game_id=game_id)


@app.route('/create_game')
def create_game():
    id = hash(random())
    GM.add_game(id)
    GM.games[id].creator = g.user.id
    return redirect(url_for('game', game_id=id))



@socketio.on('join', namespace='/ws')
def on_join(data):
    print 'join triggered by %s in %d' % (data['username'], data['room'])
    username = data['username']
    game_id = room = data['room']
    game = GM.get_game(game_id)
    game.room = room # if game.room != 0 else game.room
    join_room(room)
    game.players.append(username)
    if (game.num_players == MAX_PLAYERS):
	cr = game.creator
	ndata = json.dumps({'creator_id' : cr})
	print 'creator id %d' %(cr)
        emit('start_game', ndata, room=room, namespace='/ws', broadcast=True)
#	turn(json.dumps({'room' : room}))

@socketio.on('change_user', namespace='/ws')
def turn(data):
	room = data['room']
	game = GM.get_game(room)
	game.turn = not game.turn
	print 'turn of %d' %(game.turn)
	turn = game.turn
	data = json.dumps({'turn' : turn})
        emit('user_change', data, room=room, namespace='/ws', broadcast=True)


@socketio.on('need_round', namespace='/ws')
def rounding(data):
    room = data['room']
    user_round = data['round']
    game = GM.get_game(room)
    if (user_round == game.round):
        sum = 0
        for i in range(40):
	    sum += game.used_cards[i]
        if (sum == 0):
            max = 10
        elif (sum < 40):
            max = 6
        else:
            max = 0
            emit('end_game', room=room,  namespace='/ws', broadcast=True)
        if max:
            pics = [0 for i in range(max)]
            for i in range(max):
                picnum = randint(10, 49)
                while (game.used_cards[picnum-10] != 0 ):
                    picnum = randint(10, 49)
                game.used_cards[picnum-10] = 1
                pics[i] = picnum
            game.round += 1
            data = json.dumps({'array_cards' : pics, 'round' : game.round})
            emit('round', data, room=room, namespace='/ws', broadcast=True)

@socketio.on('card_laid', namespace='/ws')
def lay(data):
	room = data['room']
	emit('card_laid', data, room=room, namespace='/ws', broadcast=True)

@socketio.on('card_drag', namespace='/ws')
def drag(data):
	room = data['room']
	emit('card_drag', data, room=room, namespace='/ws', broadcast=True)

@socketio.on('card_taken', namespace='/ws')
def take(data):
	room = data['room']
	username = data['username']
	game = GM.get_game(room)
	user = load_user(game.creator)
	if (user.nickname == username):
	    flag = 1
	else:
	    flag = 2
	summator = json.loads(data['taken'])
	for i in summator:
	    game.score[i-10] = flag
	data = json.dumps({'username' : username, 'taken' : summator})
	emit('card_taken', data, room=room, namespace='/ws', broadcast=True)

@socketio.on('scopa', namespace='/ws')
def on_scopa(data):
	room = data['room']
	username = data['username']
	game = GM.get_game(room)
	user = load_user(game.creator)
	if (user.nickname == username):
	    flag = 1
	else:
	    flag = 2
	game.score[39 + flag] += 1
	emit('scopa', data, room=room, namespace='/ws', broadcast=True)

@socketio.on('color', namespace='/ws')
def on_color(data):
	room = data['room']
	card = data['card']
	username = data['username']
	print data
	newd = json.dumps({'username' : username, 'card' : card})
	print "colured card =  ", card
	emit('card_color', newd, room=room, namespace='/ws', broadcast=True)

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







if __name__ == "__main__":
#    app.run(host='0.0.0.0')
    socketio.run(app, host='0.0.0.0', use_reloader=True, debug=True)
