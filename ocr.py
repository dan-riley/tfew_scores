import sys
import os
import csv
import re
import cv2
import pytesseract
from rapidfuzz import fuzz
from models import Alliance, Player

class Player():
    # Convert a player object to a simplified version for OCR

    def __init__(self, player):
        self.id = player.id
        self.name = player.name
        self.score = ''
        self.altscores = []
        self.order = 99

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'score': self.score,
            'order': str(self.order)
            }


class OCRTF():

    def __init__(self, t, root_path, filename):
        self.t = t
        self.root_path = root_path
        self.filename = filename
        self.imgs = []
        self.matched = ''
        self.unmatched = ''
        self.alliance = Alliance.query.get(t.alliance).name.upper()
        self.count = 1
        self.order = 0
        self.tuningText = ''
        # Write the Tesseract output to a file to use for quicker algorithm tuning
        self.saveTuning = False
        # Read the tuning file previously saved, and not the uploaded file
        self.useTuning = False
        # Print debugging info to the log
        self.debug = False
        # Save debugging info to a file
        self.debugSave = False

        if self.useTuning:
            with open(os.path.join(root_path, 'upload/tuning.txt'), 'r') as f:
                self.tuningText = f.read()
        elif self.filename[-3:] == "mp4":
            self.dprint("Loading file(s)..." + filename)
            self.ocr_vid()
        else:
            self.dprint("Loading file(s)..." + filename)
            tmpfile = cv2.imread(filename)
            self.imgs.append(tmpfile)
        self.dprint("File loaded...")

        # Get the players for this alliance and rebuild for easier OCR processing
        self.players = []
        for player in t.players:
            self.players.append(Player(player))

    def getFrame(self, vid, frame):
        vid.set(cv2.CAP_PROP_POS_FRAMES, frame)
        success, img = vid.read()
        if success:
            self.imgs.append(img)
            # cv2.imwrite("images/image" + str(len(self.imgs)) + ".jpg", img)

        return success

    def ocr_vid(self):
        vid = cv2.VideoCapture(self.filename)

        # Read one frame per second.  Add a multiplier or divisor to fps to change.
        frame = 0
        fps = round(vid.get(cv2.CAP_PROP_FPS))
        success = self.getFrame(vid, frame)
        while success and frame + fps < vid.get(cv2.CAP_PROP_FRAME_COUNT):
            frame += fps
            success = self.getFrame(vid, frame)

    def ocr_img(self, img):
        # Crop image to read easier
        height, width = img.shape[0:2]
        img = img[0:height, 0:int(width / 2)]

        # Preprocess the image.  These settings seem to be the best after trial and error.
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        _,img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Save the processed image for review
        # cv2.imwrite('processed/cvo' + str(self.count) + '.jpg', img)
        self.count += 1

        # Get the raw text
        return pytesseract.image_to_string(img)

    def processText(self, text):
        # Analyze the raw text to find best matches in this alliance
        matched = []
        unmatched = []
        # Check for common strings that allow us to ignore further checks
        checks = [self.alliance, 'Soldier', 'Officer', 'Commander', 'WAR LEA', 'S70RCHED']

        for line in text.splitlines():
            # Only include the line if it has enough text to be useful,
            # it's not in the checks list, and there are at least 2 capital letters
            if len(line) > 5 and not any(ck in line for ck in checks) and re.findall(r'[A-Z]{2,}', line):
                # Set minimum confidence level for a match
                conf = 60
                player = None
                # Find the highest matched player for this line
                for tplayer in self.players:
                    fuzzy = fuzz.partial_ratio(tplayer.name.upper(), line)
                    # Only consider if it's not a short name and higher confidence
                    # than previous names, or if it's short, has 100% confidence
                    if (len(tplayer.name) > 3 and fuzzy >= conf) or fuzzy == 100:
                        conf = fuzzy
                        player = tplayer
                    if fuzzy == 100:
                        break

                # If we found a player, process it, otherwise add to unmatched
                if player:
                    # Pull the potential score from the end of the line
                    rest = line[-5:]
                    score = ''
                    scores = re.findall(r'\d+', rest)
                    if scores:
                        score = scores[-1]
                        # We know scores have be multiples of 5 and 300 or less
                        if int(score) % 5 or int(score) > 300:
                            score = ''

                    # Build a string for the debug output
                    save = '<b>' + str(round(conf)) + '% ' + player.name + ' ' + score + ':</b> ' + line
                    # Add players in order, whether there's a valid score or not
                    if player.order == 99:
                        self.order += 1
                        player.score = score
                        player.order = self.order
                        matched.append(save)
                    elif score:
                        # If they were already added, but we have a new score,
                        # add it if it was blank before, or save alternate scores
                        if player.score == '':
                            player.score = score
                            matched.append(save)
                        elif score not in player.altscores:
                            player.altscores.append(score)
                            matched.append(save)

                else:
                    unmatched.append(line)

        # Put the lines back together
        return '\n'.join(matched), '\n'.join(unmatched)

    def processImages(self):
        # Process each image and collate the text
        self.dprint("Processing Image(s)...")
        mt = []
        ut = []
        tuningTexts = []
        for img in self.imgs:
            # Get the text from the image
            text = self.ocr_img(img)
            # Find players and scores in the text
            matched, unmatched = self.processText(text)
            if matched:
                mt.append(matched)
            if unmatched:
                ut.append(unmatched)
            if self.saveTuning:
                tuningTexts.append(text)

        self.matched = '\n'.join(mt)
        self.unmatched = '\n'.join(ut)

        if self.saveTuning:
            with open(os.path.join(self.root_path, 'upload/tuning.txt'), 'w') as fo:
                fo.write('\n'.join(tuningTexts))

    def adjustScores(self):
        # Look for logical score changes based on the available data
        lastscore = ''
        nextscore = ''
        for player in self.players:
            # Don't try to guess players that weren't matched
            if player.order != 99:
                if player.order >= 2:
                    score = self.players[player.order - 2].score
                    # Save our last 'good' score
                    if score:
                        lastscore = score
                nextscore = self.players[player.order].score

                # Set defaults if there were blanks
                if not lastscore:
                    lastscore = '300'
                if not nextscore:
                    # Try one more after
                    nextscore = self.players[player.order + 1].score
                    if not nextscore:
                        nextscore = '0'

                # Fill in any obvious blanks (not always correct due to ordering but likely)
                if not player.score:
                    if lastscore == nextscore:
                        self.dprint('Adjusted blank ' + player.name + ' ' + lastscore)
                        player.score = lastscore

                curscore = player.score
                if not curscore:
                    curscore = '3000'

                # Find the alt score that's closest to the max of the previous or next score
                upper = max(int(lastscore), int(nextscore))
                max_test = abs(upper - int(curscore))
                altscore = None
                for score in player.altscores:
                    test = abs(upper - int(score))
                    if test < max_test:
                        max_test = test
                        altscore = score

                if altscore:
                    self.dprint('Adjusted alt ' + player.name + ' ' + player.score + ' ' + altscore)
                    player.altscores.append(player.score)
                    player.score = altscore

                if (len(player.score) == 2 and len(lastscore) == 3 and len(nextscore) == 3 and
                        lastscore[0] == nextscore[0] and lastscore[0] != '3'):
                    self.dprint('Appended ' + player.name + ' ' + player.score + ' ' + lastscore[0])
                    player.score = lastscore[0] + player.score


    def buildDebug(self):
        output = []
        output.append('Order,Player,Score')
        print('Data Review:\n')
        for player in self.players:
            if player.order != 99:
                altscores = ''
                for score in player.altscores:
                    altscores += ' ' + score
                print(player.name + ' ' + player.score + ' ' + altscores)

            output.append(str(player.order) + ',' + player.name + ',' + player.score)

        print("\n\nMatched:")
        print(self.matched)

        print("\n\nUnmatched:")
        print(self.unmatched)
        # output.append(self.unmatched)

        if self.debugSave:
            with open(os.path.join(root_path, 'output.csv'), 'w') as fo:
                fo.write('\n'.join(output))

    def dprint(self, text):
        if self.debug:
            print(text)


def main(t, root_path, filename):
    ocr = OCRTF(t, root_path, filename)
    if ocr.useTuning:
        ocr.matched, ocr.unmatched = ocr.processText(ocr.tuningText)
    else:
        ocr.processImages()

    ocr.players.sort(key=lambda x: x.order)
    ocr.adjustScores()

    if ocr.debug:
        ocr.buildDebug()

    return [player.serialize() for player in ocr.players], ocr.matched, ocr.unmatched

if __name__ == "__main__":
    main('', sys.argv[1])
