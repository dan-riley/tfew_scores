from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

war_scores = db.Table('scores',
    db.Column('player', db.Integer(), db.ForeignKey('players.id')),
    db.Column('war', db.Integer(), db.ForeignKey('wars.id')),
    db.Column('score', db.Integer()),
    db.Column('attempts_left', db.Boolean()),
    db.Column('no_attempts', db.Boolean())
)


class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    active = db.Column(db.Boolean())
    scores = db.relationship('War', secondary = war_scores, lazy = 'subquery', backref = 'player')
    ocr = db.relationship('OCR', lazy = 'subquery', backref = 'player')
    actions = db.relationship('PlayerAction', order_by='PlayerAction.date', lazy = 'subquery', backref = 'player')


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
    league = db.Column(db.String(255), nullable = False)
    opponent = db.Column(db.String(255), nullable = False)
    tracked = db.Column(db.Integer())
    our_score = db.Column(db.Integer())
    opp_score = db.Column(db.Integer())
    b1 = db.Column(db.Integer())
    b2 = db.Column(db.Integer())
    b3 = db.Column(db.Integer())
    b4 = db.Column(db.Integer())
    b5 = db.Column(db.Integer())
