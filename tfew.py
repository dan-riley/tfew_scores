from datetime import datetime, timedelta, date
import pytz
from models import db, Alliance, Player, OCR, War, Score, Issue, PrimeEffect

class TFEW():
    """ Holds global information for the app """

    def __init__(self, user):
        self.user = user
        # Version control to force reload of static files
        self.version = 'v1.17'
        # Defaults for request parameters.  Need to set based on logged in user.
        self.alliance = 2
        self.player_id = 0
        self.player = None
        self.war = None
        self.playerName = ''
        self.start_day = None
        self.end_day = None

        self.alliances = []
        self.alliancesList = []
        self.playersList = []
        self.opp_ids = []
        self.players = []
        self.wars = []
        self.filt = []
        self.issues = []
        # Display messages
        self.flash = None

    def setRequests(self, request, defPlayer=False, dateWindow=0):
        self.filt = []
        if request.args:
            player_id = request.args.get('player_id')
            self.playerName = request.args.get('player')
            ralliance = request.args.get('alliance_id')
            self.opp_ids = list(map(int, request.args.getlist('opponent_id')))
            self.start_day = request.args.get('start_day')
            self.end_day = request.args.get('end_day')

            if ralliance:
                self.alliance = int(ralliance)

            if self.playerName:
                player_id = getIDbyName(Player, self.playerName)
            elif self.playerName is None:
                self.playerName = ''

            if player_id:
                self.setPlayerArg(player_id)

            if self.opp_ids:
                self.filt.append(War.opponent_id.in_(self.opp_ids))

            if self.start_day or self.end_day:
                self.filt.append(War.date.between(self.start_day, self.end_day))
        else:
            # Set to logged in user's alliance, and player id if requested
            self.alliance = self.user.alliance_id
            if defPlayer:
                self.setPlayerArg(self.user.id)
            else:
                self.player_id = 0
                self.playerName = ''
            self.player = None
            self.opp_ids = []
            self.playersList = []
            self.alliancesList = []
            self.start_day = None
            self.end_day = None

        if dateWindow and not self.filt:
            self.end_day = datetime.now(pytz.timezone('US/Central')).date()
            self.start_day = self.end_day - timedelta(days=dateWindow)
            self.filt = [War.date.between(self.start_day, self.end_day)]

        if self.alliance != 9999:
            self.filt.append(getattr(War, 'alliance_id') == self.alliance)
        elif self.alliance == 9999 and 'history' in request.url_rule.rule:
            # Remove TFW from the All selector in History
            self.filt.append(getattr(War, 'alliance_id') != 1)

    def setRequestsWarEditor(self, request):
        self.alliance = self.user.alliance_id
        defaultWar = True
        if request.args:
            rwar_id = request.args.get('war_id')
            ralliance = request.args.get('alliance_id')

            if rwar_id:
                defaultWar = False
                war_id = int(rwar_id)
                war = War.query.get(war_id)
                self.alliance = war.alliance_id
                self.setPlayersAlliance(war.alliance_id)
                missing_players = [player for player in self.players if player not in war.players]
                self.players = war.players

            if ralliance:
                self.alliance = int(ralliance)

        if defaultWar:
            war = War()
            self.setPlayersAlliance(self.alliance)
            missing_players = []

        return war, missing_players

    def setRequestsPlayerEditor(self, request):
        if request.args:
            ralliance = request.args.get('alliance_id')
            if ralliance:
                self.alliance = int(ralliance)
        else:
            self.alliance = self.user.alliance_id

        if self.alliance != 9999:
            self.setPlayersAlliance(self.alliance)

    def setAlliances(self):
        self.alliances = Alliance.query.order_by(Alliance.name).all()

    def setAlliancesList(self):
        self.alliancesList = [alli.name for alli in Alliance.query.order_by('name').all()]

    def setPlayersList(self):
        self.playersList = [player.name for player in Player.query.order_by('name').all()]

    def setPlayerArg(self, player_id):
        self.player_id = int(player_id)
        self.filt.append(getattr(Player, 'id') == self.player_id)
        if not self.playerName:
            self.playerName = getNamebyID(Player, int(player_id))

    def setPlayers(self):
        self.players = Player.query.order_by(Player.name).all()

    def setPlayersAlliance(self, alliance_id):
        self.players = Player.query.order_by(Player.name).filter(Player.alliance_id == alliance_id).all()

    def setPlayer(self):
        self.player = Player.query.get(self.player_id)

    def setWars(self):
        self.wars = War.query.order_by(War.date.desc()).filter(*self.filt).all()

    def setWarsByPlayer(self):
        self.wars = War.query.join(Score).join(Player).order_by(War.date.desc()).filter(*self.filt).all()

    def setPlayersByWar(self):
        self.players = Player.query.join(Score).join(War).order_by(Player.name).filter(*self.filt).all()

    def setIssues(self):
        self.issues = Issue.query.all()

    def setPrimeEffects(self):
        filt = []
        if self.start_day and self.end_day:
            filt = [PrimeEffect.date.between(self.start_day, self.end_day)]
        self.primeEffects = PrimeEffect.query.order_by(PrimeEffect.date.desc()).filter(*filt).all()

    def buildAverages(self, player):
        allScore = 0
        allCount = 0
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
        cyberScore = 0
        cyberCount = 0
        cyberMin = 300
        player.scoresRange = {}

        # Get the scores and initial averages for this player
        for war in self.wars:
            score = player.score(war.id)
            player.scoresRange[war.id] = score

            if score and score.score is not None and not score.excused:
                allScore += score.score
                allCount += 1
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
                elif war.league == 7 and war.tracked != 2:
                    cyberScore += score.score
                    cyberCount += 1
                    if score.score < cyberMin:
                        cyberMin = score.score

        # Remove the minimum scores if we have enough
        if allCount > 3:
            allScore -= totalMin
            allCount -= 1

        if untrackedCount > 3:
            untrackedScore -= untrackedMin
            untrackedCount -= 1

        if trackedCount > 3:
            trackedScore -= trackedMin
            trackedCount -= 1

        if primeCount > 3:
            primeScore -= primeMin
            primeCount -= 1

        if cyberCount > 3:
            cyberScore -= cyberMin
            cyberCount -= 1

        # Get the initial averages without optional wars
        allAvg = allScore / allCount if allCount else allScore
        untrackedAvg = untrackedScore / untrackedCount if untrackedCount else untrackedScore
        trackedAvg = trackedScore / trackedCount if trackedCount else trackedScore
        primeAvg = primeScore / primeCount if primeCount else primeScore
        cyberAvg = cyberScore / cyberCount if cyberCount else cyberScore

        # Go back and add in optional scores
        for war in self.wars:
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
        cyberAvg = cyberScore / cyberCount if cyberCount else cyberScore

        # Save the final averages, rounded for display
        player.allAvg = round(allAvg)
        player.untrackedAvg = round(untrackedAvg)
        player.trackedAvg = round(trackedAvg)
        player.primeAvg = round(primeAvg)
        player.cyberAvg = round(cyberAvg)

    def updatePlayers(self, fplayers):
        for player in self.players:
            changed = False
            try:
                fplayer = fplayers['players'][player.id]
            except IndexError:
                continue
            if fplayer is None:
                continue

            # Edit the name
            if player.name != fplayer['name']:
                player.name = fplayer['name']
                changed = True

            # Set whether the player is an officer, but only if they've logged in before
            if 'officer' in fplayer:
                if not player.officer and player.password_hash:
                    player.officer = True
                    changed = True
            else:
                if player.officer:
                    player.officer = False
                    changed = True

            if str(player.alliance_id) != fplayer['alliance']:
                player.alliance_id = fplayer['alliance']
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
            player_id = getIDbyName(Player, fplayers['newName'])
            if player_id:
                player = Player.query.get(player_id)
                player.alliance_id = fplayers['newAlliance']
                db.session.add(player)
            else:
                newplayer = Player()
                newplayer.name = fplayers['newName']
                newplayer.alliance_id = fplayers['newAlliance']

                # For now we require a player to have logged in before giving officer rights
                # if 'newOfficer' in fplayers:
                #     newplayer.officer = True

                newocr = OCR()
                newocr.ocr_string = fplayers['newName'].upper()
                newplayer.ocr.append(newocr)

                db.session.add(newplayer)

        db.session.commit()

    def movePlayer(self, fplayer):
        player_from = Player.query.get(fplayer['player_from'])
        player_to = Player.query.get(fplayer['player_to'])
        self.flash = ''

        while player_from.scores:
            for score in player_from.scores:
                player_to.scores.append(score)

        if player_to.alliance_id == 0:
            player_to.alliance_id = player_from.alliance_id

        db.session.add(player_to)
        db.session.commit()
        db.session.delete(player_from)
        db.session.commit()

    def updateScore(self, fplayer, score):
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

    def updateWar(self, fwar):
        # Get the war from the database, or create a new one
        if fwar['war_id'] != 'None':
            war = War.query.get(fwar['war_id'])
        else:
            war = War()

        if fwar['opponent_id'] != '':
            war.opponent_id = fwar['opponent_id']
        else:
            opponent = getIDbyName(Alliance, fwar['opponent_new'])
            if opponent:
                war.opponent_id = opponent
            else:
                newopp = Alliance()
                newopp.name = fwar['opponent_new'].strip()
                war.opponent = newopp

        war.alliance_id = fwar['alliance_id']
        war.league = fwar['league']
        war.tracked = fwar['tracked']

        war.date = fwar['date']
        war.opp_score = fwar['opp_score'] if fwar['opp_score'] != '' else 0
        war.our_score = fwar['our_score'] if fwar['our_score'] != '' else 0

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

        # If no scores were added when war was initially created, this can be empty so check
        if 'players' not in fwar:
            fwar['players'] = []

        if war.scores:
            for score in war.scores:
                fplayer = fwar['players'][score.player_id]
                self.updateScore(fplayer, score)
        else:
            for fplayer in fwar['players']:
                if fplayer:
                    if (fplayer['score'] or 'excused' in fplayer or
                                            'attempts_left' in fplayer or
                                            'no_attempts' in fplayer):
                        newscore = Score()
                        self.updateScore(fplayer, newscore)
                        newscore.player = Player.query.get(fplayer['id'])
                        war.scores.append(newscore)

        for fplayer in fwar['missing_players']:
            if fplayer:
                if (fplayer['score'] or 'excused' in fplayer or
                                        'attempts_left' in fplayer or
                                        'no_attempts' in fplayer):
                    newscore = Score()
                    self.updateScore(fplayer, newscore)
                    newscore.player = Player.query.get(fplayer['id'])
                    war.scores.append(newscore)

        db.session.add(war)
        db.session.commit()

    def deleteWar(self, war_id):
        war = War.query.get(war_id)
        db.session.delete(war)
        db.session.commit()

    def updatePrimeEffects(self, fprime):
        for pe in self.primeEffects:
            changed = False
            try:
                fpe = fprime['pes'][pe.id]
            except IndexError:
                continue
            if fpe is None:
                continue

            # Edit the date
            if str(pe.date) != fpe['date']:
                pe.date = fpe['date']
                changed = True

            # Edit the effects
            if pe.effects != fpe['effects']:
                pe.effects = fpe['effects']
                changed = True

            if changed:
                db.session.add(pe)

        if fprime['new_effects']:
            newprime = PrimeEffect()
            newprime.date = fprime['new_date']
            newprime.effects = fprime['new_effects']

            db.session.add(newprime)

        db.session.commit()

    def getHistory(self):
        totals = {}
        for war in self.wars:
            # Setup totals object
            year = war.date.year
            month = war.date.month
            if year not in totals:
                totals[year] = {}
            if month not in totals[year]:
                totals[year][month] = MonthlyTotal()
                totals[year][month].month = datetime.strftime(war.date, '%b')
                totals[year][month].year = datetime.strftime(war.date, '%y')

            # Add up wins, losses and total averages
            wins = 0
            losses = 0
            average = war.our_score

            if war.our_score > war.opp_score:
                wins = 1
            else:
                losses = 1

            # Setup triple spark times
            if date(2020, 3, 24) < war.date < date(2020, 5, 13):
                multiplier = 3
            else:
                multiplier = 1

            # Add to the totals depending on league
            total = totals[year][month]
            if war.league == 8:
                total.prime_wins += wins
                total.prime_losses += losses
                total.prime_average += average
                if wins:
                    total.spark += 30000 * multiplier
                else:
                    total.spark += 10000 * multiplier
            elif war.league == 7:
                total.cyber_wins += wins
                total.cyber_losses += losses
                total.cyber_average += average
                if wins:
                    total.spark += 15000 * multiplier

        # Get the overall totals, and finish averages
        overall = MonthlyTotal()
        for year in totals:
            for month in totals[year]:
                total = totals[year][month]
                overall.prime_wins += total.prime_wins
                overall.prime_losses += total.prime_losses
                overall.prime_average += total.prime_average
                overall.cyber_wins += total.cyber_wins
                overall.cyber_losses += total.cyber_losses
                overall.cyber_average += total.cyber_average
                overall.spark += total.spark

                total_prime_wars = total.prime_wins + total.prime_losses
                total_cyber_wars = total.cyber_wins + total.cyber_losses
                if total_prime_wars:
                    total.prime_average = round(total.prime_average / total_prime_wars)
                if total_cyber_wars:
                    total.cyber_average = round(total.cyber_average / total_cyber_wars)

        overall_prime_wars = overall.prime_wins + overall.prime_losses
        overall_cyber_wars = overall.cyber_wins + overall.cyber_losses

        if overall_prime_wars:
            overall.prime_average = round(overall.prime_average / overall_prime_wars)
        if overall_cyber_wars:
            overall.cyber_average = round(overall.cyber_average / overall_cyber_wars)

        return totals, overall

    def submitIssue(self, issueText):
        issue = Issue()
        issue.requester = self.user.id
        issue.request = issueText
        db.session.add(issue)
        db.session.commit()


class MonthlyTotal:
    """ Helper class for tracking totals in history """
    def __init__(self):
        self.month = 0
        self.year = 0
        self.prime_wins = 0
        self.prime_losses = 0
        self.prime_average = 0
        self.cyber_wins = 0
        self.cyber_losses = 0
        self.cyber_average = 0
        self.spark = 0


def getIDbyName(table, name):
    result = db.session.query(table).filter(table.name == name.strip()).first()
    if result:
        return result.id
    else:
        return False

def getNamebyID(table, search_id):
    result = db.session.query(table).filter(table.id == search_id).first()
    if result:
        return result.name
    else:
        return False

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
