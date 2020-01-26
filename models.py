from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Score(db.Model):
    __tablename__ = 'scores'
    player_id = db.Column(db.Integer(), db.ForeignKey('players.id'), primary_key = True)
    war_id = db.Column(db.Integer(), db.ForeignKey('wars.id'), primary_key = True)
    score = db.Column(db.Integer())
    excused = db.Column(db.Boolean())
    attempts_left = db.Column(db.Boolean())
    no_attempts = db.Column(db.Boolean())
    player = db.relationship('Player', back_populates = 'scores')
    war = db.relationship('War', back_populates = 'scores')


class Player(UserMixin, db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    active = db.Column(db.Boolean())
    officer = db.Column(db.Boolean(), default = 0)
    password_hash = db.Column(db.String(128))

    scores = db.relationship('Score', lazy = 'subquery', back_populates = 'player')
    wars = db.relationship('War', secondary = 'scores', lazy = 'subquery')
    ocr = db.relationship('OCR', lazy = 'subquery', backref = 'player')
    actions = db.relationship('PlayerAction', order_by='PlayerAction.date', lazy = 'subquery', backref = 'player')

    def score(self, war_id):
        return Score.query.join(Player).filter(Score.player_id == self.id, Score.war_id == war_id).first()

    def active_day(self, day):
        active = False
        for action in self.actions:
            if action.date <= day:
                if action.action < 4:
                    active = True
                else:
                    active = False

        return active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class PlayerAction(db.Model):
    __tablename__ = 'player_actions'
    dummy_id = db.Column(db.Integer(), primary_key = True)
    player_id = db.Column(db.Integer(), db.ForeignKey('players.id'))
    date = db.Column(db.Date(), nullable = False)
    action = db.Column(db.Integer(), nullable = False)


class OCR(db.Model):
    dummy_id = db.Column(db.Integer(), primary_key = True)
    player_id = db.Column(db.Integer(), db.ForeignKey('players.id'))
    ocr_string = db.Column(db.String(255), nullable = False)


class War(db.Model):
    __tablename__ = 'wars'
    id = db.Column(db.Integer(), primary_key = True)
    date = db.Column(db.Date(), nullable = False)
    league = db.Column(db.Integer(), nullable = False)
    opponent_id = db.Column(db.Integer(), db.ForeignKey('opponents.id'))
    tracked = db.Column(db.Integer())
    our_score = db.Column(db.Integer())
    opp_score = db.Column(db.Integer())
    b1 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    b2 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    b3 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    b4 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    b5 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    opponent = db.relationship('Opponent', lazy = 'subquery', backref = 'war')
    scores = db.relationship('Score', lazy = 'subquery', back_populates = 'war')
    players = db.relationship('Player', secondary = 'scores', order_by = 'Player.name', lazy = 'subquery')
    #players = association_proxy('scores', 'players')

class Opponent(db.Model):
    __tablename__ = 'opponents'
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(255), nullable = False)
