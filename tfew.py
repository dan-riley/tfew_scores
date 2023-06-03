from datetime import datetime, timedelta, date
import pytz
from models import db, Alliance, Player, OCR, War, Score, Issue, PrimeEffect

class TFEW():
    """ Holds global information for the app """

    def __init__(self, user):
        self.user = user
        # Version control to force reload of static files
        self.version = 'v1.36'
        # Defaults for request parameters.  Need to set based on logged in user.
        self.alliance = 2
        self.player_id = 0
        self.player = None
        self.war = None
        self.playerName = ''
        self.start_day = None
        self.end_day = datetime.now(pytz.timezone('US/Central')).date()

        self.alliances = []
        self.alliancesList = []
        self.playersList = []
        self.opp_ids = []
        self.players = []
        self.wars = []
        self.filt = []
        self.issues = []
        self.updates = {}
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
                # When viewing rankings, don't show averages across the 2023 reorganization
                if (dateWindow and date.fromisoformat(self.start_day) < date(2023, 6, 1) and
                                   date.fromisoformat(self.end_day) > date(2023, 6, 1)):
                    self.start_day = date(2023, 6, 1)
                    self.flash = 'Start date automatically reset to reorganization date!'
                self.filt.append(War.date.between(self.start_day, self.end_day))

            if not self.end_day:
                self.end_day = datetime.now(pytz.timezone('US/Central')).date()
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
            self.end_day = datetime.now(pytz.timezone('US/Central')).date()

        if dateWindow and not self.filt:
            self.end_day = datetime.now(pytz.timezone('US/Central')).date()
            self.start_day = self.end_day - timedelta(days=dateWindow)
            # When viewing rankings, don't show averages across the 2023 reorganization
            # Don't need to check end_day since at this point it will always be after here
            if self.start_day < date(2023, 6, 1):
                self.start_day = date(2023, 6, 1)
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

    def setupRanker(self):
        # Default opponents
        if not self.opp_ids:
            self.opp_ids = [2,53,107,19,88,159,136,127]
        self.filt.append(War.opponent_id.in_(self.opp_ids))

        # Remove the alliance filter that may have been set by default
        self.alliance = 9999
        newfilt = []
        for filt in self.filt:
            if 'wars.alliance_id =' not in str(filt):
                newfilt.append(filt)
        self.filt = newfilt

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

        # Set the number of protocol strikes for this player
        player.setProtocol(self.alliance, self.end_day)
        # Set the total number of drops the player caused in these wars
        player.setDrops(self.wars)

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

        rawCount = trackedCount
        rawScore = trackedScore
        mulligan = False

        # If player doesn't have strikes, remove the minimum scores if we have enough
        if player.strikes == 0:
            if allCount > 3:
                allScore -= totalMin
                allCount -= 1

            if untrackedCount > 3:
                untrackedScore -= untrackedMin
                untrackedCount -= 1

            if trackedCount > 3:
                trackedScore -= trackedMin
                trackedCount -= 1
                mulligan = True

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
        rawAvg = rawScore / rawCount if rawCount else rawScore

        # Go back and add in optional scores
        for war in self.wars:
            if war.tracked == 2:
                score = player.scoresRange[war.id]
                if score and score.score is not None and not score.excused:
                    if score.score > trackedAvg:
                        trackedScore += score.score
                        trackedCount += 1

                    if score.score > rawAvg:
                        rawScore += score.score
                        rawCount += 1

                    if war.league == 8 and score.score > primeAvg:
                        primeScore += score.score
                        primeCount += 1

                    if war.league == 7 and score.score > cyberAvg:
                        cyberScore += score.score
                        cyberCount += 1

        # If there weren't enough tracked wars before, but there were
        # Optional wars counted, give the player their mulligan
        if not mulligan and player.strikes == 0 and trackedCount > 3:
            trackedScore -= trackedMin
            trackedCount -= 1

        # Recalculate the averages with the optional scores added
        trackedAvg = trackedScore / trackedCount if trackedCount else trackedScore
        primeAvg = primeScore / primeCount if primeCount else primeScore
        cyberAvg = cyberScore / cyberCount if cyberCount else cyberScore
        rawAvg = rawScore / rawCount if rawCount else rawScore

        # Deduct points for strikes
        if player.alliance_id in [2, 339, 340]:
            if player.strikes >= 2:
                trackedAvg -= 10
        else:
            if player.strikes == 1:
                trackedAvg -= 10
            elif player.strikes >= 2:
                trackedAvg -= 20

        # Save the final averages, rounded for display
        player.allAvg = round(allAvg)
        player.untrackedAvg = round(untrackedAvg)
        player.trackedAvg = round(trackedAvg)
        player.primeAvg = round(primeAvg)
        player.cyberAvg = round(cyberAvg)
        player.rawAvg = round(rawAvg)
        player.count = allCount

    def updatePlayers(self, fplayers):
        self.updates = {}
        for player in self.players:
            changed = False
            try:
                fplayer = fplayers['players'][player.id]
            except IndexError:
                continue
            if fplayer is None:
                continue

            pupdate = player.updater()
            if 'reset' in fplayer:
                pupdate['Reset'] = True
                changed = True

            # Edit the name
            newname = fplayer['name'].strip()
            if newname and player.name != newname:
                if newname in self.playersList:
                    pupdate['New_Name'] = 'New name already exists!'
                    pupdate['error'] = True
                else:
                    pupdate['New_Name'] = newname
                changed = True

            # Set whether the player is an officer, but only if they've logged in before
            if 'officer' in fplayer:
                if not player.officer and player.password_hash:
                    pupdate['Officer'] = True
                    changed = True
            else:
                if player.officer:
                    pupdate['Officer'] = False
                    changed = True

            if str(player.alliance_id) != fplayer['alliance']:
                alliance = Alliance.query.get(fplayer['alliance'])
                pupdate['Alliance'] = alliance.name
                changed = True

            # Edit the note
            newnote = fplayer['note'].strip()
            if newnote and player.note != newnote:
                pupdate['New_Note'] = newnote
                changed = True

            # Edit the OCR strings
            i = 0
            for pocr in player.ocr:
                if pocr.ocr_string != fplayer['ocr'][i]:
                    pupdate['OCR'][str(i)] = fplayer['ocr'][i]
                    changed = True
                i += 1

            if fplayer['newocr']:
                pupdate['New_OCR'] = fplayer['newocr']
                changed = True

            if changed:
                self.updates[player.id] = pupdate

        if fplayers['newName']:
            player_id = getIDbyName(Player, fplayers['newName'])
            if player_id:
                player = Player.query.get(player_id)
                pupdate = player.updater()
                alliance = Alliance.query.get(fplayers['newAlliance'])
                pupdate['Alliance'] = alliance.name
                pupdate['New_Note'] = fplayers['newNote']
                self.updates[player.id] = pupdate
            else:
                newplayer = Player()
                pupdate = newplayer.updater()
                pupdate['Name'] = 'New Player'
                pupdate['New_Name'] = fplayers['newName']
                alliance = Alliance.query.get(fplayers['newAlliance'])
                pupdate['Alliance'] = alliance.name
                pupdate['New_Note'] = fplayers['newNote']
                self.updates['new'] = pupdate

                # For now we require a player to have logged in before giving officer rights
                # if 'newOfficer' in fplayers:
                #     newplayer.officer = True

    def updatePlayersConfirm(self, fplayers):
        for player_id in fplayers:
            fplayer = fplayers[player_id]
            if player_id != 'confirmed' and player_id != 'new':
                player = Player.query.get(player_id)
                if fplayer['New_Name'] is not None:
                    player.name = fplayer['New_Name']

                if fplayer['Reset'] is not None:
                    player.password_hash = None

                if fplayer['Officer'] is not None:
                    player.officer = fplayer['Officer']

                if fplayer['Alliance'] is not None:
                    alliance_id = getIDbyName(Alliance, fplayer['Alliance'])
                    player.alliance_id = alliance_id

                if fplayer['New_Note'] is not None:
                    player.note = fplayer['New_Note']

                for oid in fplayer['OCR']:
                    if fplayer['OCR'][oid] is not None:
                        i = 0
                        for pocr in player.ocr:
                            if i == int(oid):
                                if fplayer['OCR'][oid]:
                                    pocr.ocr_string = fplayer['OCR'][oid]
                                else:
                                    db.session.delete(pocr)
                            i += 1

                if fplayer['New_OCR'] is not None:
                    newocr = OCR()
                    newocr.player_id = player.id
                    newocr.ocr_string = fplayer['New_OCR']
                    db.session.add(newocr)

                db.session.add(player)
            elif player_id == 'new':
                newplayer = Player()
                newplayer.name = fplayer['New_Name']
                newplayer.alliance_id = getIDbyName(Alliance, fplayer['Alliance'])
                newplayer.note = fplayer['New_Note']

                newocr = OCR()
                newocr.ocr_string = fplayer['New_Name'].upper()
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

    def updateAlliances(self, falliances):
        self.updates = {}
        for alliance in self.alliances:
            changed = False
            try:
                falliance = falliances['alliances'][alliance.id]
            except IndexError:
                continue
            if falliance is None:
                continue

            aupdate = alliance.updater()
            # Edit the name
            newname = falliance['name'].strip()

            if alliance.name != newname:
                if newname in self.alliancesList:
                    aupdate['New_Name'] = 'New name already exists!'
                    aupdate['error'] = True
                else:
                    aupdate['New_Name'] = newname
                changed = True

            # Set whether the alliance is a family alliance and so active
            if 'family' in falliance:
                if not alliance.active:
                    aupdate['Family'] = True
                    changed = True
            else:
                if alliance.active:
                    aupdate['Family'] = False
                    changed = True

            if changed:
                self.updates[alliance.id] = aupdate

        if falliances['newName']:
            alliance_id = getIDbyName(Alliance, falliances['newName'])
            if not alliance_id:
                newalliance = Alliance()
                aupdate = newalliance.updater()
                aupdate['Name'] = 'New Alliance'
                aupdate['New_Name'] = falliances['newName']

                if 'newFamily' in falliances:
                    aupdate['Family'] = True

                self.updates['new'] = aupdate

    def updateAlliancesConfirm(self, falliances):
        for alliance_id in falliances:
            falliance = falliances[alliance_id]
            if alliance_id != 'confirmed' and alliance_id != 'new':
                alliance = Alliance.query.get(alliance_id)
                if falliance['New_Name'] is not None:
                    alliance.name = falliance['New_Name']

                if falliance['Family'] is not None:
                    alliance.active = falliance['Family']

                db.session.add(alliance)
            elif alliance_id == 'new':
                newalliance = Alliance()
                newalliance.name = falliance['New_Name']

                if falliance['Family'] is not None:
                    newalliance.active = falliance['Family']

                db.session.add(newalliance)

        db.session.commit()

    def moveAlliance(self, falliance):
        alliance_from = Alliance.query.get(falliance['alliance_from'])
        alliance_to = Alliance.query.get(falliance['alliance_to'])
        self.flash = ''

        for war in alliance_from.oppwars:
            alliance_to.oppwars.append(war)

        db.session.add(alliance_to)
        db.session.commit()
        db.session.delete(alliance_from)
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

        if 'minor_infraction' in fplayer:
            if not score.minor_infraction:
                score.minor_infraction = True
        else:
            if score.minor_infraction:
                score.minor_infraction = False

        if 'broke_protocol' in fplayer:
            if not score.broke_protocol:
                score.broke_protocol = True
        else:
            if score.broke_protocol:
                score.broke_protocol = False

    def updateWar(self, fwar):
        # Get the war from the database, or create a new one
        if fwar['war_id'] != 'None':
            war = War.query.get(fwar['war_id'])
        else:
            war = War()

        if fwar['opponent_id'] != '':
            war.opponent_id = fwar['opponent_id']
        else:
            # TODO quick check to prevent blank names.  Need full error checking on this page!
            if fwar['opponent_new'].strip() == '':
                return

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

        if fwar['b1_drops']:
            war.b1_drops = fwar['b1_drops']
        else:
            war.b1_drops = None
        if fwar['b2_drops']:
            war.b2_drops = fwar['b2_drops']
        else:
            war.b2_drops = None
        if fwar['b3_drops']:
            war.b3_drops = fwar['b3_drops']
        else:
            war.b3_drops = None
        if fwar['b4_drops']:
            war.b4_drops = fwar['b4_drops']
        else:
            war.b4_drops = None
        if fwar['b5_drops']:
            war.b5_drops = fwar['b5_drops']
        else:
            war.b5_drops = None

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
                                            'minor_infraction' in fplayer or
                                            'broke_protocol' in fplayer):
                        newscore = Score()
                        self.updateScore(fplayer, newscore)
                        newscore.player = Player.query.get(fplayer['id'])
                        war.scores.append(newscore)

        for fplayer in fwar['missing_players']:
            if fplayer:
                if (fplayer['score'] or 'excused' in fplayer or
                                        'minor_infraction' in fplayer or
                                        'broke_protocol' in fplayer):
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
        self.updates = {}
        for pe in self.primeEffects:
            changed = False
            try:
                fpe = fprime['pes'][pe.id]
            except IndexError:
                continue
            if fpe is None:
                continue

            pupdate = pe.updater()
            # Edit the date
            if str(pe.date) != fpe['date']:
                pupdate['New_Date'] = fpe['date']
                # pe.date = fpe['date']
                changed = True

            # Edit the effects
            if pe.effects != fpe['effects']:
                pupdate['Effects'] = fpe['effects']
                # pe.effects = fpe['effects']
                changed = True

            if changed:
                self.updates[pe.id] = pupdate

        if fprime['new_effects']:
            newprime = PrimeEffect()
            pupdate = newprime.updater()
            pupdate['Date'] = 'New Effect'
            pupdate['New_Date'] = fprime['new_date']
            pupdate['Effects'] = fprime['new_effects']

            self.updates['new'] = pupdate

    def updatePrimeEffectsConfirm(self, fprime):
        for fpi in fprime:
            fpe = fprime[fpi]
            if fpi != 'confirmed' and fpi != 'new':
                pe = PrimeEffect.query.get(fpi)
                if fpe['New_Date'] is not None:
                    pe.date = fpe['New_Date']

                if fpe['Effects'] is not None:
                    pe.effects = fpe['Effects']

                db.session.add(pe)
            elif fpi == 'new':
                newprime = PrimeEffect()
                newprime.date = fpe['New_Date']
                newprime.effects = fpe['Effects']

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
            if (date(2019, 4, 24) < war.date < date(2019, 5, 2) or
                date(2020, 3, 24) < war.date < date(2020, 5, 13) or
                date(2020, 10, 7) < war.date < date(2020, 10, 15) or
                date(2020, 11, 11) < war.date < date(2020, 11, 19) or
                date(2020, 12, 16) < war.date < date(2020, 12, 24) or
                date(2021, 1, 20) < war.date < date(2021, 1, 28)):
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
