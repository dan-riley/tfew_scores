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
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
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
        t.flash = None
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
    # Get the Prime Effects
    t.setPrimeEffects()

    # Process data
    totals, overall = t.getHistory()

    if t.flash:
        flash(t.flash)
        t.flash = None
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

    if t.flash:
        flash(t.flash)
        t.flash = None
    return render_template('player.html', t=t)

@app.route('/player_editor', methods=['GET', 'POST'])
@officer_required
def player_editor():
    t.setAlliances()
    t.setPlayers()
    t.setPlayersList()

    if request.method == 'GET':
        t.setRequestsPlayerEditor(request)

    if request.method == 'POST':
        json = request.get_json()
        if 'confirmed' in json and 'true' in json['confirmed']:
            t.updatePlayersConfirm(json)
            return make_response(jsonify({"message": "Changes sucessfully submitted"}), 200)
        else:
            t.updatePlayers(json)
            return make_response(jsonify(t.updates), 201)

    if t.flash:
        flash(t.flash)
        t.flash = None
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

    if t.flash:
        flash(t.flash)
        t.flash = None
    return render_template('war_editor.html', t=t, war=war, missing_players=missing_players)

@app.route('/delete_war', methods=['GET'])
@officer_required
def delete_war():
    if request.method == 'GET':
        if request.args:
            t.deleteWar(int(request.args.get('war_id')))

    return redirect(url_for('home_page'))

@app.route('/alliance_editor', methods=['GET', 'POST'])
@officer_required
def alliance_editor():
    t.setAlliances()
    t.setAlliancesList()

    if request.method == 'POST':
        json = request.get_json()
        if 'confirmed' in json and 'true' in json['confirmed']:
            t.updateAlliancesConfirm(json)
            return make_response(jsonify({"message": "Changes sucessfully submitted"}), 200)
        else:
            t.updateAlliances(json)
            return make_response(jsonify(t.updates), 201)

    if t.flash:
        flash(t.flash)
        t.flash = None
    return render_template('alliance_editor.html', t=t)

@app.route('/move_alliance', methods=['GET', 'POST'])
@officer_required
def move_alliance():
    t.setAlliances()
    t.setAlliancesList()

    if request.method == 'POST':
        t.moveAlliance(request.get_json())
        return make_response(jsonify({"message": "Changes sucessfully submitted" + t.flash}), 200)

    return render_template('move_alliance.html', t=t)

@app.route('/prime_editor', methods=['GET', 'POST'])
@officer_required
def prime_editor():
    t.start_day = None
    t.end_day = None
    t.setPrimeEffects()

    if request.method == 'POST':
        json = request.get_json()
        if 'confirmed' in json and 'true' in json['confirmed']:
            t.updatePrimeEffectsConfirm(json)
            return make_response(jsonify({"message": "Prime Effects updated"}), 200)
        else:
            t.updatePrimeEffects(json)
            return make_response(jsonify(t.updates), 201)

    if t.flash:
        flash(t.flash)
        t.flash = None
    return render_template('prime_editor.html', t=t)

@app.route('/ore_calculator')
@login_required
def ore_calculator():
    return render_template('ore_calculator.html', t=t)

@app.route('/war_calculator')
@login_required
def war_calculator():
    return render_template('war_calculator.html', t=t)

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

@app.route('/export')
@officer_required
def export():
    scores = Score.query.join(War).order_by(War.date).all()
    output = []
    output.append('Date,Player ID,Player Name,Alliance ID,Alliance Name,'
                  'Opponent ID,Opponent Name,League,Tracked,Our Score,Opp Score,'
                  'Excused,Minor Infraction,Broke Protocol,Score')
    for score in scores:
        excused = '1' if score.excused else '0'
        minor_infraction = '1' if score.minor_infraction else '0'
        broke_protocol = '1' if score.broke_protocol else '0'
        tscore = '' if score.score is None else score.score

        output.append(str(score.war.date) + ',' +
                      str(score.player.id) + ',' + score.player.name + ',' +
                      str(score.war.alliance_id) + ',' + score.war.alliance.name + ',' +
                      str(score.war.opponent_id) + ',' + score.war.opponent.name + ',' +
                      score.war.leagueText() + ',' + str(score.war.tracked) + ',' +
                      str(score.war.our_score) + ',' + str(score.war.opp_score) + ',' +
                      excused + ',' + minor_infraction + ',' + broke_protocol + ',' + str(tscore)
                      )

    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'export.csv'), 'w') as fo:
        fo.write('\n'.join(output))

    path = os.path.join(app.config['UPLOAD_FOLDER'], 'export.csv')
    return send_file(path, as_attachment=True)

@app.route('/ml')
@officer_required
def ml():
    html = []
    num_wars = 24
    predict_tracked = False
    # pred_opps = (53, 107, 19, 159, 104, 28)
    pred_opps = (53, 107, 19, 159, 104, 28, 88, 31, 152, 43)
    valid_wars = (0, 1172)

    players = Player.query.all()
    train_full = []
    train_valid = []
    valid = []
    train_avg = []
    train_avg_valid = []
    valid_avg = []
    cols = 'pid,'
    # Header for per war version
    for i in range(1, num_wars + 1):
        si = '_' + str(i)
        cols += ('league' + si + ',tracked' + si + ',our_score' + si + ',opp_score' + si +
                 ',minor_infraction' + si + ',broke_protocol' + si + ',score' + si + ',')
    train_full.append(cols + 'tracked_avg,' + 'pred_score')
    train_valid.append(cols + 'tracked_avg,' + 'pred_score')
    valid.append(cols + 'tracked_avg,' + 'pred_score')
    # Header for averages version
    cols = 'pid,our_score,opp_score,all,tracked,optional,untracked,league_1,league_2,league_3,league_4,'
    cols += 'league_5,league_6,league_7,league_8,minor_infraction_tracked,broke_protocol_tracked,'
    cols += 'minor_infraction_opt,broke_protocol_opt,minor_infraction_untracked,broke_protocol_untracked,'
    train_avg.append(cols + 'tracked_avg,' + 'pred_score')
    train_avg_valid.append(cols + 'tracked_avg,' + 'pred_score')
    valid_avg.append(cols + 'tracked_avg,' + 'pred_score')

    for player in players:
        player.scores.sort(key=lambda x: x.war.date)
        pid = str(player.id) + ','
        for idx, pred_score in enumerate(player.scores):
            # Set either Top 5 or any tracked war
            if predict_tracked:
                predictor = pred_score.war.tracked
            else:
                predictor = pred_score.war.opponent_id in pred_opps

            # Find each top 5 or tracked war the player competed in, but need at least num_wars
            if idx > num_wars and not pred_score.excused and predictor:
                # Now add each score to the data
                x = ''
                our_score = 0
                opp_score = 0
                league = {}
                league_count = {}
                for i in range(1, 9):
                    league[i] = 0
                    league_count[i] = 0
                count = 0
                all_score = 0
                untracked_score = 0
                untracked_count = 0
                tracked_score = 0
                tracked_count = 0
                optional_score = 0
                optional_count = 0
                minor_infraction_tracked = 0
                broke_protocol_tracked = 0
                minor_infraction_untracked = 0
                broke_protocol_untracked = 0
                minor_infraction_optional = 0
                broke_protocol_optional = 0
                cidx = idx - 1
                while count < num_wars and cidx >= 0:
                    score = player.scores[cidx]
                    if not (score.excused and (score.score is None or score.score < 90)):
                        count += 1
                        # Correct for None in these
                        minor_infraction = 1 if score.minor_infraction else 0
                        broke_protocol = 1 if score.broke_protocol else 0

                        if score.war.tracked == 1:
                            tracked_score += score.score
                            tracked_count += 1
                            minor_infraction_tracked += minor_infraction
                            broke_protocol_tracked += broke_protocol
                        elif score.war.tracked == 0:
                            untracked_score += score.score
                            untracked_count += 1
                            minor_infraction_untracked += minor_infraction
                            broke_protocol_untracked += broke_protocol
                        elif score.war.tracked == 2:
                            optional_score += score.score
                            optional_count += 1
                            minor_infraction_optional += minor_infraction
                            broke_protocol_optional += broke_protocol

                        # Total war totals
                        our_score += score.war.our_score
                        opp_score += score.war.opp_score
                        all_score += score.score

                        # Total each league
                        league[score.war.league] += score.score
                        league_count[score.war.league] += 1

                        if score.war.tracked == 1:
                            tracked = '2'
                        elif score.war.tracked == 2:
                            tracked = '1'
                        else:
                            tracked = '0'

                        x += (str(score.war.league) + ',' + tracked + ',' +
                              str(score.war.our_score) + ',' + str(score.war.opp_score) + ',' +
                              str(minor_infraction) + ',' + str(broke_protocol) + ',' + str(score.score) + ','
                             )

                    cidx -= 1

                if count == num_wars:
                    if tracked_count:
                        tracked_avg = tracked_score / tracked_count
                        str_tracked_avg = str(int(tracked_avg))
                        minor_infraction_tracked_avg = str(minor_infraction_tracked / tracked_count)
                        broke_protocol_tracked_avg = str(broke_protocol_tracked / tracked_count)
                    else:
                        tracked_avg = '0'
                        str_tracked_avg = '0'
                        minor_infraction_tracked_avg = '0'
                        broke_protocol_tracked_avg = '0'

                    # Add to the full training data
                    train_full.append(pid + x + str_tracked_avg + ',' + str(pred_score.score))

                    # Build the average version
                    all_score = str(all_score / count)
                    tracked_avg = str(tracked_avg)
                    if untracked_count:
                        untracked_avg = str(untracked_score / untracked_count)
                        minor_infraction_untracked_avg = str(minor_infraction_untracked / untracked_count)
                        broke_protocol_untracked_avg = str(broke_protocol_untracked / untracked_count)
                    else:
                        untracked_avg = '0'
                        minor_infraction_untracked_avg = '0'
                        broke_protocol_untracked_avg = '0'

                    if optional_count:
                        optional_avg = str(optional_score / optional_count)
                        minor_infraction_opt_avg = str(minor_infraction_optional / optional_count)
                        broke_protocol_opt_avg = str(broke_protocol_optional / optional_count)
                    else:
                        optional_avg = '0'
                        minor_infraction_opt_avg = '0'
                        broke_protocol_opt_avg = '0'

                    # Add
                    our_avg = our_score / count
                    opp_avg = opp_score / count

                    league_text = ''
                    for i in range(1, 9):
                        if league_count[i]:
                            league_text += str(league[i] / league_count[i]) + ','
                        else:
                            league_text += '0,'

                    avg_line = (pid + str(our_avg) + ',' + str(opp_avg) + ',' + all_score + ',' +
                                tracked_avg + ',' + optional_avg + ',' + untracked_avg + ',' +
                                league_text +
                                minor_infraction_tracked_avg + ',' + broke_protocol_tracked_avg + ',' +
                                minor_infraction_opt_avg + ',' + broke_protocol_opt_avg + ',' +
                                minor_infraction_untracked_avg + ',' + broke_protocol_untracked_avg + ',' +
                                str_tracked_avg + ',' + str(pred_score.score))

                    train_avg.append(avg_line)

                    # Separate the validation wars from the training data
                    if pred_score.war.id in valid_wars:
                        valid.append(pid + x + str_tracked_avg + ',' + str(pred_score.score))
                        valid_avg.append(avg_line)
                    else:
                        train_valid.append(pid + x + str_tracked_avg + ',' + str(pred_score.score))
                        train_avg_valid.append(avg_line)

                elif count < num_wars:
                    html.append('not enough for ' + pred_score.player.name + ' ' + str(count))

    if predict_tracked:
        pre = 'tracked_'
    else:
        pre = 'top5_'
    with open(os.path.join(app.root_path, pre + 'training_full.csv'), 'w') as fo:
        fo.write('\n'.join(train_full))

    with open(os.path.join(app.root_path, pre + 'training_valid.csv'), 'w') as fo:
        fo.write('\n'.join(train_valid))

    with open(os.path.join(app.root_path, pre + 'valid.csv'), 'w') as fo:
        fo.write('\n'.join(valid))

    with open(os.path.join(app.root_path, pre + 'training_avg.csv'), 'w') as fo:
        fo.write('\n'.join(train_avg))

    with open(os.path.join(app.root_path, pre + 'training_avg_valid.csv'), 'w') as fo:
        fo.write('\n'.join(train_avg_valid))

    with open(os.path.join(app.root_path, pre + 'valid_avg.csv'), 'w') as fo:
        fo.write('\n'.join(valid_avg))

    html.append('Success!')
    return render_template('utility.html', html=html)

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
    allCaps = True
    players = Player.query.order_by('name').all()
    alliances = Alliance.query.order_by('name').all()

    if allCaps:
        playersDict = dict(zip([player.name.upper() for player in players], players))
        alliancesDict = dict(zip([alliance.name.upper() for alliance in alliances], alliances))
    else:
        playersDict = dict(zip([player.name for player in players], players))
        playersDictUpper = dict(zip([player.name.upper() for player in players], players))
        alliancesDict = dict(zip([alliance.name for alliance in alliances], alliances))

    html = []
    with open(os.path.join(app.root_path, 'data/vector_scores.csv'), 'r') as f:
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
                if not allCaps and name.upper() in playersDictUpper:
                    playersDictUpper[name.upper()].name = name
                    playersDict[name] = playersDictUpper[name.upper()]
                    html.append('fixed player name ' + name)
                    db.session.add(playersDictUpper[name.upper()])
                else:
                    player = Player()
                    if allCaps:
                        aname = name.split()
                        player.name = ''
                        for cname in aname:
                            player.name += cname.capitalize() + ' '

                        player.name = player.name.strip()
                    else:
                        player.name = name
                    html.append('adding player ' + player.name)

                    player.alliance_id = alliance_id

                    newocr = OCR()
                    newocr.ocr_string = name
                    player.ocr.append(newocr)

                    playersDict[name] = player
                    db.session.add(player)
            else:
                for war in playersDict[name].wars:
                    if war.date == wardate:
                        html.append('player already exists ' + name)

            if opponent not in alliancesDict:
                newopp = Alliance()
                if allCaps:
                    aname = opponent.split()
                    newopp.name = ''
                    for cname in aname:
                        newopp.name += cname.capitalize() + ' '

                    newopp.name = newopp.name.strip()
                else:
                    newopp.name = opponent
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

                if league in ('PRIME', 'Prime'):
                    newwar.league = 8
                elif league in ('CYBERTRON', 'Cybertron', 'CYBER'):
                    newwar.league = 7
                elif league in ('CAMINUS', 'Caminus'):
                    newwar.league = 6
                elif league in ('PLATINUM', 'Platinum'):
                    newwar.league = 5
                elif league in ('GOLD', 'Gold'):
                    newwar.league = 4

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
                newscore.broke_protocol = True
            elif attempts > 0:
                newscore.minor_infraction = True
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
