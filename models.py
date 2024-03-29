from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

db = SQLAlchemy()

class Score(db.Model):
    __tablename__ = 'scores'
    player_id = db.Column(db.Integer(), db.ForeignKey('players.id'), primary_key=True)
    war_id = db.Column(db.Integer(), db.ForeignKey('wars.id'), primary_key=True)
    score = db.Column(db.Integer())
    airank = db.Column(db.Integer())
    excused = db.Column(db.Boolean())
    minor_infraction = db.Column(db.Boolean())
    broke_protocol = db.Column(db.Boolean())
    player = db.relationship('Player', back_populates='scores')
    war = db.relationship('War', back_populates='scores')


class Player(UserMixin, db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    alliance_id = db.Column(db.Integer(), db.ForeignKey('alliances.id'))
    officer = db.Column(db.Boolean(), default=0)
    password_hash = db.Column(db.String(128))
    note = db.Column(db.String(255), default='')

    scores = db.relationship('Score', back_populates='player')
    wars = db.relationship('War', secondary='scores', order_by='War.date', overlaps='player,scores,war')
    alliance = db.relationship('Alliance', foreign_keys='Player.alliance_id')
    strikes = 0
    drops = 0
    avg_drops = 0

    def score(self, war_id):
        return Score.query.filter(Score.player_id == self.id, Score.war_id == war_id).first()

    def setProtocol(self, palliance_id, date):
        # Find the number of strikes in the last 45 days, only in this alliance
        self.strikes = 0
        # Don't count infractions before this date
        protocolStart = datetime(2021,1,22).date()
        end_day = date
        if isinstance(end_day, str):
            end_day = datetime.strptime(end_day, "%Y-%m-%d").date()
        start_day = end_day - timedelta(days=45)
        if start_day < protocolStart:
            start_day = protocolStart

        # Find all tracked wars in the time period for this player, and count strikes
        pwars = War.query.join(Score).join(Player).filter(Player.id == self.id, War.alliance_id == palliance_id, War.tracked == 1, War.date.between(start_day, end_day)).all()
        for war in pwars:
            pscore = self.score(war.id)
            if pscore.broke_protocol:
                self.strikes += 1

    def setDrops(self, wars):
        count = 0
        for war in wars:
            if war.b1 == self.id and war.b1_drops != None:
                self.drops += war.b1_drops
                count += 1
            elif war.b2 == self.id and war.b2_drops != None:
                self.drops += war.b2_drops
                count += 1
            elif war.b3 == self.id and war.b3_drops != None:
                self.drops += war.b3_drops
                count += 1
            elif war.b4 == self.id and war.b4_drops != None:
                self.drops += war.b4_drops
                count += 1
            elif war.b5 == self.id and war.b5_drops != None:
                self.drops += war.b5_drops
                count += 1

        if count:
            self.avg_drops = self.drops / count

    def alliances(self):
        alliances = []
        lastAlliance = -1
        for score in sorted(self.scores, key=lambda x: x.war.date):
            if score.war.alliance_id != lastAlliance:
                lastAlliance = score.war.alliance_id
                alliances.append({'alliance': score.war.alliance, 'date': score.war.date})

        return alliances

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        else:
            return False

    def updater(self):
        update = {}
        update['Name'] = self.name
        update['New_Name'] = None
        update['Reset'] = None
        update['Officer'] = None
        update['Alliance'] = None
        update['Note'] = self.note
        update['New_Note'] = None

        return update


class War(db.Model):
    __tablename__ = 'wars'
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.Date(), nullable=False)
    league = db.Column(db.Integer(), nullable=False)
    alliance_id = db.Column(db.Integer(), db.ForeignKey('alliances.id'))
    opponent_id = db.Column(db.Integer(), db.ForeignKey('alliances.id'))
    tracked = db.Column(db.Integer())
    our_score = db.Column(db.Integer())
    opp_score = db.Column(db.Integer())
    b1_drops = db.Column(db.Integer())
    b2_drops = db.Column(db.Integer())
    b3_drops = db.Column(db.Integer())
    b4_drops = db.Column(db.Integer())
    b5_drops = db.Column(db.Integer())
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
    alliance = db.relationship('Alliance', foreign_keys='War.alliance_id')
    opponent = db.relationship('Alliance', foreign_keys='War.opponent_id')
    scores = db.relationship('Score', back_populates='war', cascade='delete, delete-orphan')
    players = db.relationship('Player', secondary='scores', order_by='Player.name', overlaps='player,scores,war,wars')
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
            r = 'optional'
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
        elif self.league == 5:
            r = 'Platinum'
        elif self.league == 4:
            r = 'Gold'
        elif self.league == 3:
            r = 'Silver'
        return r


class Alliance(db.Model):
    __tablename__ = 'alliances'
    id = db.Column(db.Integer(), primary_key=True)
    active = db.Column(db.Boolean())
    name = db.Column(db.String(255), nullable=False)
    wars = db.relationship('War', foreign_keys='War.alliance_id', overlaps='alliance')
    oppwars = db.relationship('War', foreign_keys='War.opponent_id', overlaps='opponent')

    def updater(self):
        update = {}
        update['Name'] = self.name
        update['New_Name'] = None
        update['Family'] = None

        return update


class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.Integer(), primary_key=True)
    complete = db.Column(db.Boolean())
    requester = db.Column(db.Integer(), db.ForeignKey('players.id'))
    request = db.Column(db.Text())
    comments = db.Column(db.Text())
    player = db.relationship('Player', foreign_keys='Issue.requester')


class PrimeEffect(db.Model):
    __tablename__ = 'prime_effects'
    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.Date(), nullable=False)
    effects = db.Column(db.Text())

    def updater(self):
        update = {}
        if self.date:
            update['Date'] = self.date.isoformat()
        else:
            update['Date'] = ''
        update['New_Date'] = None
        update['Effects'] = None

        return update
