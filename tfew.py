from datetime import datetime, timedelta, date
import pytz
from models import db, Alliance, Player, War, Score, Opponent

class TFEW():
    """ Holds global information for the app """

    def __init__(self):
        self.alliance = 2
        self.player_id = 0
        self.player = None
        self.opponent = ''
        self.start_day = None
        self.end_day = None

        self.alliances = []
        self.opponents = []
        self.players = []
        self.wars = []
        self.filt = []

    def setRequests(self, request, dateWindow=0):
        self.filt = []
        if request.args:
            rplayer = request.args.get('player_id')
            ralliance = request.args.get('alliance_id')
            opp_id = request.args.get('opponent_id')
            self.opponent = request.args.get('opponent')
            self.start_day = request.args.get('start_day')
            self.end_day = request.args.get('end_day')

            if rplayer:
                self.player_id = int(rplayer)
                self.filt.append(getattr(Player, 'id') == self.player_id)

            if ralliance:
                self.alliance = int(ralliance)

            if self.opponent:
                opp_id = getIDbyName(Opponent, self.opponent)
            elif self.opponent is None:
                self.opponent = ''

            if opp_id:
                self.filt.append(getattr(War, 'opponent_id') == int(opp_id))
                if not self.opponent:
                    self.opponent = getNamebyID(Opponent, int(opp_id))

            if self.start_day or self.end_day:
                self.filt.append(War.date.between(self.start_day, self.end_day))
      
        if dateWindow and not self.filt:
            self.end_day = datetime.now(pytz.timezone('US/Central')).date()
            self.start_day = self.end_day - timedelta(days=dateWindow)
            self.filt = [War.date.between(self.start_day, self.end_day)]

        if self.alliance != 9999:
            self.filt.append(getattr(War, 'alliance_id') == self.alliance)

    def setAlliances(self):
        self.alliances = Alliance.query.all()

    def setOpponents(self):
        self.opponents = [opp.name for opp in Opponent.query.order_by('name').all()]

    def setPlayers(self):
        self.players = db.session.query(Player).order_by(Player.name).all()

    def setPlayer(self):
        self.player = db.session.query(Player).get(self.player_id)

    def setWars(self):
        self.wars = War.query.order_by(War.date.desc()).filter(*self.filt).all()

    def setWarsByPlayer(self):
        self.wars = War.query.join(Score).join(Player).order_by(War.date.desc()).filter(*self.filt).all()

    def setPlayersByWar(self):
        self.players = Player.query.join(Score).join(War).order_by(Player.name).filter(*self.filt).all()

    def buildAverages(self, player):
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
        for war in self.wars:
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

        # Save the final averages, rounded for display
        player.totalAvg = round(totalAvg)
        player.untrackedAvg = round(untrackedAvg)
        player.trackedAvg = round(trackedAvg)
        player.primeAvg = round(primeAvg)

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
