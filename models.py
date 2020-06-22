from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Score(db.Model):
    __tablename__ = 'scores'
    player_id = db.Column(db.Integer(), db.ForeignKey('players.id'), primary_key=True)
    war_id = db.Column(db.Integer(), db.ForeignKey('wars.id'), primary_key=True)
    score = db.Column(db.Integer())
    excused = db.Column(db.Boolean())
    attempts_left = db.Column(db.Boolean())
    no_attempts = db.Column(db.Boolean())
    player = db.relationship('Player', back_populates='scores')
    war = db.relationship('War', back_populates='scores')


class Player(UserMixin, db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    officer = db.Column(db.Boolean(), default=0)
    password_hash = db.Column(db.String(128))

    scores = db.relationship('Score', back_populates='player')
    wars = db.relationship('War', secondary='scores')
    ocr = db.relationship('OCR', backref='player')
    actions = db.relationship('PlayerAction', order_by='PlayerAction.date', backref='player')

    def score(self, war_id):
        return Score.query.filter(Score.player_id == self.id, Score.war_id == war_id).first()

    def active_day(self, day):
        active = False
        for action in self.actions: # pylint: disable=not-an-iterable
            if action.date <= day:
                active = bool(action.action < 4)

        return active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        else:
            return False


class PlayerAction(db.Model):
    __tablename__ = 'player_actions'
    dummy_id = db.Column(db.Integer(), primary_key=True)
    player_id = db.Column(db.Integer(), db.ForeignKey('players.id'))
    alliance_id = db.Column(db.Integer(), db.ForeignKey('alliances.id'))
    date = db.Column(db.Date(), nullable=False)
    action = db.Column(db.Integer(), nullable=False)


class OCR(db.Model):
    dummy_id = db.Column(db.Integer(), primary_key=True)
    player_id = db.Column(db.Integer(), db.ForeignKey('players.id'))
    ocr_string = db.Column(db.String(255), nullable=False)


class War(db.Model):
    __tablename__ = 'wars'
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.Date(), nullable=False)
    league = db.Column(db.Integer(), nullable=False)
    alliance_id = db.Column(db.Integer(), db.ForeignKey('alliances.id'))
    opponent_id = db.Column(db.Integer(), db.ForeignKey('opponents.id'))
    tracked = db.Column(db.Integer())
    our_score = db.Column(db.Integer())
    opp_score = db.Column(db.Integer())
    b1 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    b2 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    b3 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    b4 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    b5 = db.Column(db.Integer(), db.ForeignKey('players.id'))
    b1p = db.relationship('Player', foreign_keys='War.b1')
    b2p = db.relationship('Player', foreign_keys='War.b2')
    b3p = db.relationship('Player', foreign_keys='War.b3')
    b4p = db.relationship('Player', foreign_keys='War.b4')
    b5p = db.relationship('Player', foreign_keys='War.b5')
    alliance = db.relationship('Alliance', backref='war')
    opponent = db.relationship('Opponent', backref='war')
    scores = db.relationship('Score', back_populates='war', cascade='delete, delete-orphan')
    players = db.relationship('Player', secondary='scores', order_by='Player.name')
    #players = association_proxy('scores', 'players')

    def winClass(self):
        if self.our_score > self.opp_score:
            r = 'win'
        else:
            r = 'loss'
        return r

    def trackedClass(self):
        if not self.tracked:
            r = 'untracked'
        elif self.tracked == 1:
            r = 'tracked'
        else:
            r = 'untracked'
        return r

    def trackedText(self):
        if not self.tracked:
            r = 'No'
        elif self.tracked == 1:
            r = 'Yes'
        else:
            r = 'Optional'
        return r

    def leagueText(self):
        if self.league == 8:
            r = 'Prime'
        elif self.league == 7:
            r = 'Cybertron'
        elif self.league == 6:
            r = 'Caminus'
        return r


class Opponent(db.Model):
    __tablename__ = 'opponents'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Alliance(db.Model):
    __tablename__ = 'alliances'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
