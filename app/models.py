from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(100), index=True, unique=True)
    password = db.Column(db.String(100), index=True)
    scopas = db.Column(db.Integer, index=True)
    score = db.Column(db.Integer, index=True)
    games = db.Column(db.Integer, index=True)
    wins = db.Column(db.Integer, index=True)


    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def is_active(self):
        return True;

    def is_authenticated(self):
        return True;

    def get_id(self):
        return str(self.id).encode('utf-8')
