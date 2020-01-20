import os
from flask import Flask, render_template, request, send_file, jsonify, make_response
from flask_script import Manager
from werkzeug.utils import secure_filename
import json
import ocr
from models import db, Player, OCR, War

app = Flask(__name__)
manager = Manager(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'upload')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'mp4', 'mov'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tfew_scores:tfw2005scores@localhost/tfew_scores'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home_page():
    players = db.session.query(Player).order_by(Player.name).all()
    return render_template('index.html', players = players)

@app.route('/player_editor', methods=['GET', 'POST'])
def player_editor():
    players = db.session.query(Player).order_by(Player.name).all()
    factive = ''
    fnames = ''
    fplayers = ''
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

            # Edit the OCR strings
            i = 0
            for ocr in player.ocr:
                if ocr.ocr_string != fplayer['ocr'][i]:
                    ocr.ocr_string = fplayer['ocr'][i];
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

        db.session.commit()
        return make_response(jsonify({"message": "Changes sucessfully submitted"}), 200)

    return render_template('player_editor.html', players = players)

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
            response =  make_response(jsonify(scores), 200)
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

if __name__ == "__main__":
    manager.run()
