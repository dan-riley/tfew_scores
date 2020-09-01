import os
from datetime import datetime
import json
import csv
from functools import wraps
import pytz
from flask import Flask, render_template, flash, request, send_file, jsonify, make_response, redirect, url_for
from flask_script import Manager
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
import ocr
from models import db, Player, OCR, War, Score, Alliance
from forms import LoginForm, SignupForm
import tfew

app = Flask(__name__, instance_relative_config=True)
manager = Manager(app)
login_manager = LoginManager(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'mp4', 'mov'])
app.config.from_object('config.Config')
app.config.from_pyfile('config.py')
db.init_app(app)
login_manager.init_app(app)

# Initialize our class that holds data for easier access
t = tfew.TFEW(current_user)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def officer_required(f):
    # Determine if the logged in user is logged in and an officer
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not current_user.officer:
            flash('You must be an officer to view that page')
            return redirect(url_for('home_page'))
        return f(*args, **kwargs)
    return decorated_view

def self_required(f):
    # Determine if the logged in user is logged in and the requested player or an officer
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not current_user.officer and request.args.get('player_id') and current_user.id != int(request.args.get('player_id')):
            flash('You must be the requested player or an officer to view that page')
            return redirect(url_for('home_page'))
        return f(*args, **kwargs)
    return decorated_view

@app.context_processor
def inject_today():
    return {'today': datetime.now(pytz.timezone('US/Central')).date()}

@login_manager.user_loader
def load_user(user_id):
    return Player.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page')
    return redirect(url_for('login', next=url_for(request.endpoint)))

@app.route("/login", methods=["GET", "POST"])
def login():
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = Player.query.filter_by(name=form.name.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home_page'))
        flash('Invalid username/password combination')
        return redirect(url_for('login'))
    return render_template('login.html', t=t, form=form)

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect(url_for('home_page'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    t.setPlayersList()
    form = SignupForm()
    if form.validate_on_submit():
        user = Player.query.filter_by(name=form.name.data).first()
        # If the user exists and does NOT have a password allow the password setting
        if user and user.password_hash is None and form.auth.data == app.config['AUTH_CODE']:
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home_page'))
        if not user:
            flash('This is not a user')
        elif user and not user.password_hash is None:
            flash('This user already has a password')
        elif form.auth.data != app.config['AUTH_CODE']:
            flash('Incorrect Auth Code')

    return render_template('signup.html', t=t, form=form)

@app.route('/')
def home_page():
    # Default page for a logged in user is the scoreboard.  Otherwise login.
    if current_user.is_authenticated:
        if current_user.officer:
            return redirect(url_for('scoreboard'))
        else:
            return redirect(url_for('player_view'))

    return redirect(url_for('login'))

@app.route('/scoreboard')
@login_required
def scoreboard():
    # Set all of the parameters based on URL params, with a default date window
    t.setRequests(request, dateWindow=28)

    # Load lists for the template
    t.setAlliances()
    # Pull the data we need from the database
    t.setWars()
    t.setPlayersByWar()

    # Build the player averages
    for player in t.players:
        t.buildAverages(player)

    if t.flash:
        flash(t.flash)
    return render_template('scoreboard.html', t=t)

@app.route('/history')
@login_required
def history():
    # Set all of the parameters based on URL params
    t.setRequests(request)

    # Load lists for the template
    t.setAlliances()
    # Pull the data we need from the database
    t.setWars()

    # Process data
    totals, overall = t.getHistory()

    return render_template('history.html', t=t, overall=overall, totals=totals)

@app.route('/player')
@self_required
def player_view():
    # Set all of the parameters based on URL params
    t.setRequests(request, True)

    # Load lists for the template
    t.setAlliances()
    t.setPlayersList()
    # Pull the data we need from the database
    t.setWarsByPlayer()
    t.setPlayer()

    # Process data
    t.buildAverages(t.player)

    return render_template('player.html', t=t)

@app.route('/player_editor', methods=['GET', 'POST'])
@officer_required
def player_editor():
    t.setAlliances()
    t.setPlayers()

    if request.method == 'GET':
        t.setRequestsPlayerEditor(request)

    if request.method == 'POST':
        t.updatePlayers(request.get_json())
        return make_response(jsonify({"message": "Changes sucessfully submitted"}), 200)

    return render_template('player_editor.html', t=t)

@app.route('/move_player', methods=['GET', 'POST'])
@officer_required
def move_player():
    t.setPlayers()
    t.setPlayersList()

    if request.method == 'POST':
        t.movePlayer(request.get_json())
        return make_response(jsonify({"message": "Changes sucessfully submitted" + t.flash}), 200)

    return render_template('move_player.html', t=t)

@app.route('/war_editor', methods=['GET', 'POST'])
@officer_required
def war_editor():
    t.setAlliances()
    t.setAlliancesList()

    if request.method == 'GET':
        war, missing_players = t.setRequestsWarEditor(request)

    elif request.method == 'POST':
        t.updateWar(request.get_json())
        return make_response(jsonify({"message": "War submitted"}), 200)

    return render_template('war_editor.html', t=t, war=war, missing_players=missing_players)

@app.route('/delete_war', methods=['GET'])
@officer_required
def delete_war():
    if request.method == 'GET':
        if request.args:
            t.deleteWar(int(request.args.get('war_id')))

    return redirect(url_for('home_page'))

@app.route('/issues', methods=['GET', 'POST'])
@login_required
def issues():
    if request.method == 'POST':
        t.submitIssue(request.form['request'])

    t.setIssues()

    return render_template('issues.html', t=t)

@app.route('/upload', methods=['GET', 'POST'])
@officer_required
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
@officer_required
def loadScores():
    if request.method == 'POST':
        with open(os.path.join(app.root_path, 'scores.json'), 'r') as fo:
            scores = json.load(fo)

            return make_response(jsonify(scores), 200)

    return render_template('upload.html')

@app.route('/download')
@officer_required
def downloadFile():
    path = os.path.join(app.root_path, 'output.csv')
    return send_file(path, as_attachment=True)

@app.route('/import_tfw_scores')
@officer_required
def importTFWScores():
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

                        newocr = OCR()
                        newocr.ocr_string = name.strip().upper()
                        player.ocr.append(newocr)

                        db.session.add(player)

                    wplayers.append(player)

                count += 1
            else:
                newwar = War()
                opponent = tfew.getIDbyNameCSV(Alliance, row[0])
                if opponent != '':
                    newwar.opponent_id = opponent
                else:
                    newopp = Alliance()
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

@app.route('/import_sector_scores')
@officer_required
def importSectorScores():
    players = Player.query.order_by('name').all()
    playersDict = dict(zip([player.name.upper() for player in players], players))

    alliances = Alliance.query.order_by('name').all()
    alliancesDict = dict(zip([alliance.name.upper() for alliance in alliances], alliances))

    html = []
    with open(os.path.join(app.root_path, 'data/sectorwars-scores-update2.csv'), 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            name = row[1].strip()
            score = int(row[2].strip())
            alliance = row[4].strip()
            wardate = datetime.strptime(row[5].strip(), '%m/%d/%Y').date()
            our_score = int(row[7].strip())
            opp_score = int(row[8].strip())
            opponent = row[9].strip()
            league = row[10].strip()
            tracked = row[11].strip()
            if row[3] == '':
                attempts = 0
            else:
                attempts = int(row[3].strip())

            alliance_id = alliancesDict[alliance].id
            if name not in playersDict:
                player = Player()
                aname = name.split()
                player.name = ''
                for cname in aname:
                    player.name += cname.capitalize() + ' '

                player.name = player.name.strip()
                html.append('adding player ' + player.name)

                player.alliance_id = alliance_id

                newocr = OCR()
                newocr.ocr_string = name
                player.ocr.append(newocr)

                playersDict[name] = player
                db.session.add(player)

            if opponent not in alliancesDict:
                newopp = Alliance()
                aname = opponent.split()
                newopp.name = ''
                for cname in aname:
                    newopp.name += cname.capitalize() + ' '

                newopp.name = newopp.name.strip()
                html.append('opponent ' + newopp.name + ' added')
                alliancesDict[opponent] = newopp
                db.session.add(newopp)

            newwar = None
            for war in alliancesDict[alliance].wars:
                if war.date == wardate and war.opponent.id == alliancesDict[opponent].id:
                    newwar = war
                    break

            if not newwar:
                newwar = War()
                newwar.opponent = alliancesDict[opponent]

                if league == 'PRIME':
                    newwar.league = 8
                elif league == 'CYBERTRON':
                    newwar.league = 7
                elif league == 'CAMINUS':
                    newwar.league = 6
                elif league == 'PLATINUM':
                    newwar.league = 5

                newwar.alliance_id = alliance_id
                newwar.date = wardate
                newwar.our_score = our_score
                newwar.opp_score = opp_score

                if tracked == 'No':
                    newwar.tracked = 0
                elif tracked == 'Yes':
                    newwar.tracked = 1
                elif tracked == 'Optional':
                    newwar.tracked = 2
                else:
                    newwar.tracked = 0

                html.append('war added ' + str(newwar.date) + ' ' + alliance + ' ' + opponent)
                alliancesDict[alliance].wars.append(newwar)

            newscore = Score()
            newscore.score = score
            if attempts == 3 and score == 0:
                newscore.no_attempts = True
            elif attempts > 0:
                newscore.attempts_left = True
            newscore.player = playersDict[name]
            newwar.scores.append(newscore)

            db.session.add(newscore)

    db.session.commit()
    return render_template('utility.html', html=html)

@app.route('/import_blanks')
@officer_required
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

@app.route('/check_player_alliance')
@officer_required
def checkPlayerAlliance():
    html = []
    players = Player.query.all()

    for player in players:
        if len(player.wars) > 1:
            if player.alliance_id and player.wars[-1].alliance_id != player.alliance_id:
                html.append(player.name + ' ' + str(player.alliance_id) + ' ' + str(player.wars[-1].alliance_id))
                player.alliance_id = player.wars[-1].alliance_id
                db.session.add(player)

    # db.session.commit()

    return render_template('utility.html', html=html)

if __name__ == "__main__":
    manager.run()
