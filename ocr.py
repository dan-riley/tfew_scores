import sys
import os
import csv
import re
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/home/olevelo/bin/tesseract'

class Player(object):

    def __init__(self, name, pot_names):
        self.name = name
        self.names = pot_names
        self.score = ''
        self.order = 99
        self.line = ''

    def serialize(self):
        return {
                'name': self.name,
                'score': self.score,
                'order': str(self.order)
                }


class OCRTF(object):

    def __init__(self, root_path, filename):
        self.filename = filename
        self.imgs = []
        self.output = ''
        self.unmatched = ''
        self.alliance = 'TFW2005'
        self.count = 1
        self.order = 0

        if self.filename[-3:] == "mp4":
            self.ocr_vid()
        else:
            print("Loading file(s)..." + filename, file=sys.stderr)
            tmpfile = cv2.imread(filename)
            print("Appending file...", file=sys.stderr)
            self.imgs.append(tmpfile)

        print("File loaded...", file=sys.stderr)
        # Get the potential names
        self.players = []
        with open(os.path.join(root_path, 'data/tfw2005_players.csv'), 'r') as f:
            csv_reader = csv.reader(f, delimiter=',')
            for row in csv_reader:
                self.players.append(Player(row[0], row[1:]))

    def getFrame(self, vid, sec):
        vid.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        success, img = vid.read()
        if success:
            self.imgs.append(img)
            # cv2.imwrite("images/image" + str(len(self.imgs)) + ".jpg", img)

        return success

    def ocr_vid(self):
        vid = cv2.VideoCapture(self.filename)

        sec = 0
        frameRate = 1
        success = self.getFrame(vid, sec)
        while success:
            sec = sec + frameRate
            sec = round(sec, 2)
            success = self.getFrame(vid, sec)

    def ocr_img(self, img):
        # Crop image to read easier
        height, width = img.shape[0:2]
        img = img[0:height, 0:int(width / 2)]

        # Invert image so text is black
        img = cv2.bitwise_not(img)

        # Save the processed image for review
        # cv2.imwrite('processed/cvo' + str(self.count) + '.jpg', img)
        self.count += 1

        # Get the raw text
        return pytesseract.image_to_string(img)

    def processText(self, text):
        unmatched = []
        start = False
        for line in text.splitlines():
            # Only include the line if it has enough text to be useful
            if start and len(line) > 5:
                keep = True
                # Check each rule but stop checking if we match one
                if 'Soldier' in line:
                    keep = False
                elif 'Officer' in line:
                    keep = False
                elif 'Commander' in line:
                    keep = False

                added = False
                # Add the line if none of the rules were hit
                # Could make this a final elif, but this seems cleaner
                if keep:
                    for player in self.players:
                        for name in player.names:
                            if name in line:
                                rest = line.split(name)[1]
                                scores = re.findall(r'\d+', rest)
                                if scores:
                                    score = scores[-1]
                                    if int(score) % 5 or int(score) > 225:
                                        score = ''
                                else:
                                    score = ''

                                if player.order == 99:
                                    self.order += 1
                                    player.score = score
                                    player.order = self.order
                                    player.line = line
                                    # print(str(player.order) + ' ' + player.name + ' ' + score);
                                elif score and (player.score == '' or score > player.score):
                                    # print('Duplicate: ')
                                    # print(player.name + ' old: ' + player.score + ' new: ' + score)
                                    player.score = score
                                    player.line = line

                                added = True
                                # Stop looking at this player
                                break

                        # Stop looking at other players because we matched already
                        if added:
                            break

                    if not added:
                        unmatched.append(line)

            # Ignore everything up to the alliance name
            if self.alliance in line:
                start = True

        # Put the lines back together
        return '\n'.join(unmatched)

    def processImages(self):
        print("Processing Image(s)...", file=sys.stderr)
        texts = []
        for img in self.imgs:
            text = self.ocr_img(img)
            unmatched = self.processText(text)
            if unmatched:
                texts.append(unmatched)

        self.unmatched = '\n'.join(texts)


def main(root_path, filename):

    ocr = OCRTF(root_path, filename)
    ocr.processImages()

    output = []
    output.append('Order,Player,Score')
    print('Data Review:\n')
    ocr.players.sort(key=lambda x: x.order)
    for player in ocr.players:
        if player.order != 99:
            print(player.name + ' ' + player.score)
            orders = str(player.order)
        else:
            orders = ''

        output.append(orders + ',' + player.name + ',' + player.score)

    # output.append('\nData Entry:\n')
    # ocr.players.sort(key=lambda x: x.name)
    # for player in ocr.players:
    #     output.append(player.name + ',' + player.score)

    print("\n\nUnmatched:")
    print(ocr.unmatched)
    # output.append(ocr.unmatched)

    with open(os.path.join(root_path, 'output.csv'), 'w') as fo:
        fo.write('\n'.join(output))

    return [player.serialize() for player in ocr.players]

if __name__ == "__main__":
    main('', sys.argv[1])
