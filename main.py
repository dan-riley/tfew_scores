import os
from datetime import datetime, timedelta
import json
import csv
import pytz
import operator
from flask import Flask, render_template, request, send_file, jsonify, make_response
from flask_script import Manager
from flask_login import LoginManager
from werkzeug.utils import secure_filename
import ocr
from models import db, Player, PlayerAction, OCR, War, Score, Opponent, Alliance

app = Flask(__name__)
manager = Manager(app)
login = LoginManager(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'upload')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'mp4', 'mov'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tfew_scores:tfw2005scores@localhost/tfew_scores'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getIDbyName(table, name):
    result = db.session.query(table).filter(table.name == name.strip()).first()
    if result:
        return result.id
    else:
        return False

@app.context_processor
def inject_today():
    return {'today': datetime.now(pytz.timezone('US/Central')).date()}

@app.route('/')
def home_page():
    # Default alliance.  May want a better way of setting this based on user permissions.
    alliance = 2

    # Templates for converting database entries to text
    templates = {}
    templates['players'] = {}
    templates['leagues'] = {8: 'Prime', 7: 'Cybertron', 6: 'Caminus'}
    templates['tracked'] = {0: 'No', 1: 'Yes', 2: 'Optional'}

    filt = []
    if request.args:
        ralliance = request.args.get('alliance_id')
        opp = request.args.get('war_opponent')
        start_day = request.args.get('start_day')
        end_day = request.args.get('end_day')

        if ralliance:
            alliance = int(ralliance)

        if opp:
            filt.append(getattr(War, 'opponent_id') == int(opp))

        if start_day:
            filt.append(War.date.between(start_day, end_day))

    if not filt:
        end_day = datetime.now(pytz.timezone('US/Central')).date()
        start_day = end_day - timedelta(days=21)
        filt = [War.date.between(start_day, end_day)]

    filt.append(getattr(War, 'alliance_id') == alliance)
    templates['alliance'] = alliance
    templates['start_day'] = start_day
    templates['end_day'] = end_day

    alliances = Alliance.query.all()
    wars = War.query.order_by(War.date.desc()).filter(*filt).all()
    players = Player.query.order_by(Player.name).join(Score).join(War).filter(*filt).all()

    # Set the classes for formatting
    for war in wars:
        if war.our_score > war.opp_score:
            war.winClass = 'win'
        else:
            war.winClass = 'loss'

        if not war.tracked:
            war.trackedClass = 'untracked'
        elif war.tracked == 1:
            war.trackedClass = 'tracked'
        else:
            war.trackedClass = 'optional'

    # Build the player names index for base names and get averages
    for player in players:
        templates['players'][player.id] = player.name

        totalScore = 0
        totalCount = 0
        totalMin = 300
        untrackedScore = 0
        untrackedCount = 0
        untrackedMin = 300
        trackedScore = 0
        trackedCount = 0
        trackedMin = 300
        primeScore = 0
        primeCount = 0
        primeMin = 300
        player.scoresRange = {}
        # Get the scores and initial averages for this player
        for war in wars:
            score = player.score(war.id)
            player.scoresRange[war.id] = score

            if score and score.score is not None and not score.excused:
                totalScore += score.score
                totalCount += 1
                if score.score < totalMin:
                    totalMin = score.score

                if war.tracked == 0:
                    untrackedScore += score.score
                    untrackedCount += 1
                    if score.score < untrackedMin:
                        untrackedMin = score.score
                elif war.tracked == 1:
                    trackedScore += score.score
                    trackedCount += 1
                    if score.score < trackedMin:
                        trackedMin = score.score

                if war.league == 8 and war.tracked != 2:
                    primeScore += score.score
                    primeCount += 1
                    if score.score < primeMin:
                        primeMin = score.score

        # Remove the minimum scores if we have enough
        if totalCount > 5:
            totalScore -= totalMin
            totalCount -= 1

        if untrackedCount > 5:
            untrackedScore -= untrackedMin
            untrackedCount -= 1

        if trackedCount > 5:
            trackedScore -= trackedMin
            trackedCount -= 1

        if primeCount > 5:
            primeScore -= primeMin
            primeCount -= 1

        # Get the initial averages without optional wars
        totalAvg = totalScore / totalCount if totalCount else totalScore
        untrackedAvg = untrackedScore / untrackedCount if untrackedCount else untrackedScore
        trackedAvg = trackedScore / trackedCount if trackedCount else trackedScore
        primeAvg = primeScore / primeCount if primeCount else primeScore

        # Go back and add in optional scores
        for war in wars:
            if war.tracked == 2:
                score = player.scoresRange[war.id]
                if score and score.score is not None and not score.excused:
                    if score.score > trackedAvg:
                        trackedScore += score.score
                        trackedCount += 1

                    if war.league == 8 and score.score > primeAvg:
                        primeScore += score.score
                        primeCount += 1

        # Recalculate the averages with the optional scores added
        trackedAvg = trackedScore / trackedCount if trackedCount else trackedScore
        primeAvg = primeScore / primeCount if primeCount else primeScore

        # Save the final averages, rounded for display
        player.totalAvg = round(totalAvg)
        player.untrackedAvg = round(untrackedAvg)
        player.trackedAvg = round(trackedAvg)
        player.primeAvg = round(primeAvg)

    return render_template('index.html', alliances=alliances, players=players, wars=wars, templates=templates)

@app.route('/player_editor', methods=['GET', 'POST'])
def player_editor():
    players = db.session.query(Player).order_by(Player.name).all()

    if request.method == 'POST':
        fplayers = request.get_json()
        for player in players:
            changed = False
            fplayer = fplayers['players'][player.id]

            # Edit the name
            if player.name != fplayer['name']:
                player.name = fplayer['name']
                changed = True

            # Set the active state
            if 'active' in fplayer:
                if not player.active:
                    player.active = True
                    changed = True
            else:
                if player.active:
                    player.active = False
                    changed = True

            # Edit the last action or add new last action
            lastAction = player.actions[-1]
            if (str(lastAction.date) != fplayer['lastDate'] and
                    str(lastAction.action) != fplayer['lastAction']):
                newAction = PlayerAction()
                newAction.player_id = player.id
                newAction.date = fplayer['lastDate']
                newAction.action = fplayer['lastAction']
                db.session.add(newAction)
                changed = True
            elif (str(lastAction.date) != fplayer['lastDate'] and
                  str(lastAction.action) == fplayer['lastAction']):
                lastAction.date = fplayer['lastDate']
                changed = True
            elif (str(lastAction.action) != fplayer['lastAction'] and
                  str(lastAction.date) == fplayer['lastDate']):
                lastAction.action = fplayer['lastAction']
                changed = True

            # Edit the OCR strings
            i = 0
            for pocr in player.ocr:
                if pocr.ocr_string != fplayer['ocr'][i]:
                    pocr.ocr_string = fplayer['ocr'][i]
                    changed = True
                i += 1

            if fplayer['newocr']:
                newocr = OCR()
                newocr.player_id = player.id
                newocr.ocr_string = fplayer['newocr']
                db.session.add(newocr)
                changed = True

            if changed:
                db.session.add(player)

        if fplayers['newName']:
            newplayer = Player()
            newplayer.name = fplayers['newName']
            newplayer.active = True

            newaction = PlayerAction()
            newaction.date = fplayers['newActionDate']
            newaction.action = fplayers['newAction']
            newplayer.actions.append(newaction)

            newocr = OCR()
            newocr.ocr_string = fplayers['newName'].upper()
            newplayer.ocr.append(newocr)

            db.session.add(newplayer)

        db.session.commit()
        return make_response(jsonify({"message": "Changes sucessfully submitted"}), 200)

    return render_template('player_editor.html', players=players)

@app.route('/war_editor', methods=['GET', 'POST'])
def war_editor():
    alliance_id = 2
    alliances = Alliance.query.all()

    if request.method == 'GET':
        if request.args:
            war_id = int(request.args.get('war_id'))
            war = War.query.get(war_id)
            alliance_id = war.alliance_id
            players = war.players
            ids = (player.id for player in players)
            missing_players = Player.query.order_by(Player.name).filter(Player.active, ~Player.id.in_(ids)).all()
        else:
            war = War()
            players = Player.query.order_by(Player.name).filter(Player.active).all()

    elif request.method == 'POST':
        fwar = request.get_json()

        # Get the war from the database, or create a new one
        if fwar['war_id'] != 'None':
            war = War.query.get(fwar['war_id'])
        else:
            war = War()

        opponent = getIDbyName(Opponent, fwar['opponent'])
        if opponent:
            war.opponent_id = opponent
        else:
            newopp = Opponent()
            newopp.name = fwar['opponent'].strip()
            war.opponent = newopp

        war.alliance_id = fwar['alliance_id']
        war.league = fwar['league']
        war.tracked = fwar['tracked']

        war.date = fwar['date']
        war.opp_score = fwar['opp_score']
        war.our_score = fwar['our_score']

        if fwar['b1']:
            war.b1 = fwar['b1']
        else:
            war.b1 = None
        if fwar['b2']:
            war.b2 = fwar['b2']
        else:
            war.b2 = None
        if fwar['b3']:
            war.b3 = fwar['b3']
        else:
            war.b3 = None
        if fwar['b4']:
            war.b4 = fwar['b4']
        else:
            war.b4 = None
        if fwar['b5']:
            war.b5 = fwar['b5']
        else:
            war.b5 = None

        if war.scores:
            for score in war.scores:
                fplayer = fwar['players'][score.player_id]
                if fplayer['score']:
                    score.score = int(fplayer['score'].strip())
                else:
                    score.score = None

                # Get all of the checkboxes
                if 'excused' in fplayer:
                    if not score.excused:
                        score.excused = True
                else:
                    if score.excused:
                        score.excused = False

                if 'attempts_left' in fplayer:
                    if not score.attempts_left:
                        score.attempts_left = True
                else:
                    if score.attempts_left:
                        score.attempts_left = False

                if 'no_attempts' in fplayer:
                    if not score.no_attempts:
                        score.no_attempts = True
                else:
                    if score.no_attempts:
                        score.no_attempts = False
        else:
            for fplayer in fwar['players']:
                if fplayer:
                    # TODO It doesn't look like checkboxes work on the first submit?!
                    newscore = Score()
                    if fplayer['score']:
                        newscore.score = int(fplayer['score'].strip())
                    else:
                        newscore.score = None
                    newscore.player = Player.query.get(fplayer['id'])
                    war.scores.append(newscore)

        for fplayer in fwar['missing_players']:
            if fplayer:
                if fplayer['score'] or 'excused' in fplayer or 'attempts_left' in fplayer or 'no_attempts' in fplayer:
                    newscore = Score()
                    if fplayer['score']:
                        newscore.score = int(fplayer['score'].strip())
                    else:
                        newscore.score = None
                    newscore.player = Player.query.get(fplayer['id'])
                    war.scores.append(newscore)

        db.session.add(war)
        db.session.commit()
        return make_response(jsonify({"message": "War submitted"}), 200)

    return render_template('war_editor.html', alliance_id=alliance_id, alliances=alliances, war=war, players=players, missing_players=missing_players)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            fullfile = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(fullfile)

            # Process the video or image and return the result to javascript
            scores = ocr.main(app.root_path, fullfile)
            response = make_response(jsonify(scores), 200)
            with open(os.path.join(app.root_path, 'scores.json'), 'w') as fo:
                json.dump(scores, fo)

            os.remove(fullfile)
        else:
            response = make_response(jsonify({"message": "Invalid file type"}), 300)

        return response

    return render_template('upload.html')

@app.route('/load_scores', methods=['GET', 'POST'])
def loadScores():
    if request.method == 'POST':
        with open(os.path.join(app.root_path, 'scores.json'), 'r') as fo:
            scores = json.load(fo)

            return make_response(jsonify(scores), 200)

    return render_template('upload.html')

@app.route('/download')
def downloadFile():
    path = os.path.join(app.root_path, 'output.csv')
    return send_file(path, as_attachment=True)

def getIDbyNameCSV(table, name):
    name = name.split('-')
    name = name[0]

    if name.strip() == 'Tomcat14':
        name = 'Preacher'

    result = db.session.query(table).filter(table.name == name.strip()).first()
    if result:
        return result.id
    else:
        return ''

@app.route('/import_scores')
def importScores():
    with open(os.path.join(app.root_path, 'data/jan2_scores.csv'), 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        count = 0
        wplayers = []
        for row in csv_reader:
            if count == 0:
                for name in row[13:]:
                    if name.strip() == 'Tomcat14':
                        name = 'Preacher'
                    player = db.session.query(Player).filter(Player.name == name.strip()).first()
                    if not player:
                        player = Player()
                        player.name = name.strip()
                        player.active = False

                        newaction = PlayerAction()
                        newaction.alliance_id = 2
                        newaction.date = '2020-01-17'
                        newaction.action = 3
                        player.actions.append(newaction)

                        newocr = OCR()
                        newocr.ocr_string = name.strip().upper()
                        player.ocr.append(newocr)

                        db.session.add(player)

                    wplayers.append(player)

                count += 1
            else:
                newwar = War()
                opponent = getIDbyNameCSV(Opponent, row[0])
                if opponent != '':
                    newwar.opponent_id = opponent
                else:
                    newopp = Opponent()
                    newopp.name = row[0].strip()
                    newwar.opponent = newopp

                league = row[1].strip()
                if league == 'Prime':
                    newwar.league = 8
                elif league == 'Cybertron':
                    newwar.league = 7
                elif league == 'Caminus':
                    newwar.league = 6

                newwar.alliance_id = 2
                newwar.date = row[2]
                newwar.opp_score = int(row[3].replace(',', ''))

                b1 = getIDbyNameCSV(Player, row[6])
                if b1:
                    newwar.b1 = b1
                b2 = getIDbyNameCSV(Player, row[7])
                if b2:
                    newwar.b2 = b2
                b3 = getIDbyNameCSV(Player, row[8])
                if b3:
                    newwar.b3 = b3
                b4 = getIDbyNameCSV(Player, row[9])
                if b4:
                    newwar.b4 = b4
                b5 = getIDbyNameCSV(Player, row[10])
                if b5:
                    newwar.b5 = b5

                tracked = row[11].strip()
                if tracked == 'No':
                    newwar.tracked = 0
                elif tracked == 'Yes':
                    newwar.tracked = 1
                elif tracked == 'Optional':
                    newwar.tracked = 2
                else:
                    newwar.tracked = 3

                our_score = 0
                newscores = row[13:]
                for i in range(len(newscores)):
                    if newscores[i].strip():
                        newscore = Score()
                        newscore.score = int(newscores[i].strip())
                        our_score += newscore.score
                        newscore.player = wplayers[i]
                        newwar.scores.append(newscore)

                newwar.our_score = our_score
                db.session.add(newwar)

    db.session.commit()
    return render_template('import_scores.html')

@app.route('/import_blanks')
def importBlanks():
    with open(os.path.join(app.root_path, 'data/jan2_scores.csv'), 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        count = 0
        wplayers = []
        for row in csv_reader:
            if count == 0:
                for name in row[13:]:
                    if name.strip() == 'Tomcat14':
                        name = 'Preacher'
                    player = db.session.query(Player).filter(Player.name == name.strip()).first()
                    wplayers.append(player)

                count += 1
            else:
                add = False
                war = War.query.filter(War.date == row[2]).first()
                newscores = row[13:]
                for i in range(len(newscores)):
                    if not newscores[i].strip() and wplayers[i].active_day(war.date):
                        if wplayers[i] not in war.players:
                            newscore = Score()
                            newscore.excused = True
                            newscore.player = wplayers[i]
                            war.scores.append(newscore)
                            add = True

                if add:
                    db.session.add(war)

    db.session.commit()
    return render_template('import_scores.html')

if __name__ == "__main__":
    manager.run()
