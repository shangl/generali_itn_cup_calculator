#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 13:02:17 2020

@author: Hangl Simon
"""

## TODO: the following sequence is not handled yet: win, wo, wo, wo
##   (this will probably lead to giving only one point; depending on how
##   how wo is indicated)

## TODO: b matches are missing

## TODO: cannot handle same names (e.g. christoph eder appears twice in the same draw)
##      therefore maximum rounds do not work anymore as well --> currently, at most 5 rounds are hard coded

import textract
from os import listdir
from os.path import isfile, join

class Player:
    def __init__(self, firstName, lastName):
        self._firstName = firstName
        self._lastName = lastName
        self._points = 0
        self._lastTournamentMatches = 0
        self._lastPlayedMatches = 0
        self._itn = "unknown"
        self._licenseNumber = "unknown"
        
    def getFirstName(self):
        return self._firstName
    
    def getLastName(self):
        return self._lastName
        
    def addPoints(self, points):
        self._points += points
        
    def getPoints(self):
        return self._points
    
    def setLicenseNumber(self, licenseNumber):
        self._licenseNumber = licenseNumber
        
    def setItn(self, itn):
        self._itn = itn
    
    ## these are the rounds the player appeared in
    def setLastTournamentMatches(self, matches):
        self._lastTournamentMatches = matches
        
    def getLastTournamentMatches(self):
        return self._lastTournamentMatches
    
    ## these are the rounds the player actually won
    def setLastWonMatches(self, matches):
        self._lastPlayedMatches = matches
        
    def getLastWonMatches(self):
        return self._lastPlayedMatches
    
    def getId(self):
        return self._firstName + "$" + self._lastName
    
    def __str__(self):
        return self._firstName + " " + self._lastName + "(" + self._licenseNumber + " / " + self._itn + "): " + str(self._points) + " points"

def extractSeeds(seeds):
    seeded = []
    for seedName in seeds:
        if len(seedName.split(", ")) >= 2 and "Name, Vorname" not in seedName and "erstellt am" not in seedName:
            extractedNN = seedName.split("NN ")
            if len(extractedNN) > 1:
                seeded.append(extractedNN[1])
            else:
                seeded.append(seedName)

    return seeded

def fetchPlayer(playerName, playersDict):
    lastName = playerName.split(", ")[0]
    firstName = playerName.split(", ")[1]
    newPlayer = Player(firstName, lastName)
    if newPlayer.getId() not in playersDict:
        playersDict[newPlayer.getId()] = newPlayer
    return playersDict[newPlayer.getId()]

def countPlayerOccurence(draw, player):
    occurences = 0
    wonMatches = 0
    lastName = player.getLastName()
    firstName = player.getFirstName()
    toSearch1 = lastName + " " + firstName[0] + "."
    ## adding the "(" to eliminate the cases where the b match is on the draw
    toSearch2 = lastName + ", " + firstName + " ("
    for contentIdx in range(len(draw)):
        contentLine = draw[contentIdx]
        if toSearch1 in contentLine or toSearch2 in contentLine:
            if toSearch2 in contentLine:
                licenseNumber = contentLine.split("(")[1].split(")")[0].split("/")[0]
                itn = contentLine.split("(")[1].split(")")[0].split("/")[1]
                player.setLicenseNumber(licenseNumber)
                player.setItn(itn)
            occurences += 1
        if toSearch1 in contentLine and contentIdx < (len(draw) - 1) and draw[contentIdx + 1] != "":
            wonMatches += 1

    player.setLastTournamentMatches(occurences)
    player.setLastWonMatches(wonMatches)
    return player

def extractPoints(player, maxRounds):

    if player.getLastTournamentMatches() == 0:
        return 0
    ## if you play less or equal than 1 round --> points are independent of the stage
    elif player.getLastTournamentMatches() >= 1 and player.getLastWonMatches() == 0:
        return 1

    matchesToWin = min(maxRounds, 5) - player.getLastTournamentMatches()
    if matchesToWin == 0:
        return 15
    elif matchesToWin == 1:
        return 11
    elif matchesToWin == 2:
        return 7
    elif matchesToWin == 3:
        return 4
    elif matchesToWin == 4:
        return 1
    
    print("unexpected input.")
    return 0

drawsPath = "/media/sf_data/priv/generali/"
allFiles = [f for f in listdir(drawsPath) if isfile(join(drawsPath, f))]
playersDict = {}

for currentFile in allFiles:
    print(currentFile)
    if(".pdf" not in currentFile):
        continue
    currentFile = textract.process(currentFile)
    content = currentFile.decode("utf-8").split("\n")
    
    seedStartIdx = content.index("Setzliste")
    drawContent = content[0:seedStartIdx]
    seedsContent = content[seedStartIdx::]
    
    seeds = extractSeeds(seedsContent)
    
    maxRounds = 0
    players = []
    for currentSeed in seeds:
        player = fetchPlayer(currentSeed, playersDict)
        countPlayerOccurence(drawContent, player)
        maxRounds = max(maxRounds, player.getLastTournamentMatches())
        players.append(player)
    
    for player in players:
        points = extractPoints(player, maxRounds)
        player.addPoints(points)

playersRanking = []
for player in playersDict:
    playersRanking.append(playersDict[player])

playersRanking = sorted(playersRanking, key = lambda player: player.getPoints())
for player in playersRanking:
    print(str(player))