import os
from datetime import datetime
import json
import csv
import pytz
from flask import Flask, render_template, request, send_file, jsonify, make_response, redirect
from flask_script import Manager
from flask_login import LoginManager
from werkzeug.utils import secure_filename
import ocr
from models import db, Player, PlayerAction, OCR, War, Score, Opponent
import tfew

app = Flask(__name__)
manager = Manager(app)
login = LoginManager(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'upload')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'mp4', 'mov'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://***REMOVED***'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize our class that holds data for easier access
t = tfew.TFEW()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_today():
    return {'today': datetime.now(pytz.timezone('US/Central')).date()}

@app.route('/')
def home_page():
    # Set all of the parameters based on URL params, with a default date window
    t.setRequests(request, 21)

    # Load lists for the template
    t.setAlliances()
    t.setOpponents()
    # Pull the data we need from the database
    t.setWars()
    t.setPlayersByWar()

    # Build the player averages
    for player in t.players:
        t.buildAverages(player)

    return render_template('index.html', t=t)

@app.route('/history')
def history():
    # Set all of the parameters based on URL params
    t.setRequests(request)

    # Load lists for the template
    t.setAlliances()
    t.setOpponents()
    # Pull the data we need from the database
    t.setWars()

    # Process data
    totals, overall = t.getHistory()

    return render_template('history.html', t=t, overall=overall, totals=totals)

@app.route('/player')
def player_view():
    # Set all of the parameters based on URL params
    t.setRequests(request)

    # Load lists for the template
    t.setAlliances()
    t.setOpponents()
    t.setPlayers()
    # Pull the data we need from the database
    t.setWarsByPlayer()
    t.setPlayer()

    # Process data
    t.buildAverages(t.player)

    return render_template('player.html', t=t)

@app.route('/player_editor', methods=['GET', 'POST'])
def player_editor():
    t.setPlayers()

    if request.method == 'POST':
        t.updatePlayers(request.get_json())
        return make_response(jsonify({"message": "Changes sucessfully submitted"}), 200)

    return render_template('player_editor.html', t=t)

@app.route('/war_editor', methods=['GET', 'POST'])
def war_editor():
    t.setAlliances()
    t.setOpponents()

    if request.method == 'GET':
        war, missing_players = t.setRequestsWarEditor(request)

    elif request.method == 'POST':
        t.updateWar(request.get_json())
        return make_response(jsonify({"message": "War submitted"}), 200)

    return render_template('war_editor.html', t=t, war=war, missing_players=missing_players)

@app.route('/delete_war', methods=['GET'])
def delete_war():
    if request.method == 'GET':
        if request.args:
            t.deleteWar(int(request.args.get('war_id')))

    return redirect('/')

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

    return render_template('upload.html', t=t)

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
                opponent = tfew.getIDbyNameCSV(Opponent, row[0])
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

                b1 = tfew.getIDbyNameCSV(Player, row[6])
                if b1:
                    newwar.b1 = b1
                b2 = tfew.getIDbyNameCSV(Player, row[7])
                if b2:
                    newwar.b2 = b2
                b3 = tfew.getIDbyNameCSV(Player, row[8])
                if b3:
                    newwar.b3 = b3
                b4 = tfew.getIDbyNameCSV(Player, row[9])
                if b4:
                    newwar.b4 = b4
                b5 = tfew.getIDbyNameCSV(Player, row[10])
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
