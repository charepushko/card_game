from app import db

opponents = db.Table('opponents',
    db.Column('game_id', db.Integer, primary_key=True, unique=True),
    db.Column('opponent1_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('opponent2_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(100), index=True, unique=True)
    password = db.Column(db.String(100), index=True)
    scopas = db.Column(db.Integer, index=True)
    score = db.Column(db.Integer, index=True)
    games = db.Column(db.Integer, index=True)
    wins = db.Column(db.Integer, index=True)

    # who have fighted with
    fighted = db.relationship('User',
        secondary = opponents,
        primaryjoin = (opponents.c.opponent1_id == id),
        secondaryjoin = (opponents.c.opponent2_id == id),
        backref = db.backref('opponents', lazy='dynamic'),
        lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def is_active(self):
        return True;

    def is_authenticated(self):
        return True;

    def get_id(self):
        return str(self.id).encode('utf-8')
