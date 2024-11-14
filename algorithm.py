import numpy as np
import pandas as pd

k = 0.5
k1 = 2
rankingWeight = 0.65

class Player: 
    def __init__(self, gameData, positionAvg, positionDev, zMin, zMax, ranking, numPlayers):
        self.gameData = gameData
        self.df = pd.DataFrame(self.gameData)
        self.positionAvg = positionAvg
        self.positionDev = positionDev
        self.zMin = zMin
        self.zMax = zMax 
        self.ranking = ranking
        self.numPlayers = numPlayers
        self.avgPoints = 0 
        self.zScore = 0
        self.pointScore = 0
        self.streakiness = 0
        self.rankingScore = 0
        self.totalScore = 0

        self.avgPointsCalculator()
        self.streakinessCalculator()
        self.zScoreCalculator()
        self.pointScoreCalculator()
        self.rankingScoreCalculator()
        self.totalScoreCalculator()

    def avgPointsCalculator(self):
        length = len(self.df)
        totalPoints = 0 
        totalGames = length + 1.5 
        points = self.df.iloc[:, 0]
        strength = self.df.iloc[:, 1]
        # Convert each to strength factor 
        strength = strength.apply(lambda x: 1 - ((k * x - k) / 31))
        # Adjust points
        points = points * strength

        # Recent games with 1.5 weight
        totalPoints = points.iloc[0:length-3].sum()
        totalPoints += points.iloc[length-3:].sum() * 1.5
        self.avgPoints = totalPoints / totalGames
    
    def streakinessCalculator(self):
        q1 = self.df.iloc[:, 0].quantile(0.25)
        lowOutlierCount = (self.df.iloc[:, 0] < q1).sum()
        lowOutlierPct = lowOutlierCount / len(self.df)
        self.streakiness = lowOutlierPct

    def zScoreCalculator(self):
        self.zScore = (self.avgPoints - self.positionAvg) / self.positionDev

    # Convert z-score to a rating out of 100
    def pointScoreCalculator(self):
        adjustedZScore = self.zScore + self.zMin
        self.pointScore = (adjustedZScore * 100) / self.zMax
        self.pointScore *= self.streakiness
    
    def rankingScoreCalculator(self):
        percentile = (self.numPlayers - self.ranking) / (self.numPlayers - 1)
        self.rankingScore = percentile * 100

    def totalScoreCalculator(self):
        pointWeight = (1 - rankingWeight) * self.pointScore
        rankingWeightWeighted = rankingWeight * self.rankingScore
        self.totalScore = pointWeight + rankingWeightWeighted


class Trade: 
    def __init__(self, teamA, teamB):
        # Lists of players from each side of the trade
        self.teamA = teamA
        self.teamB = teamB
        # Adjusted sums of players
        self.sumA = 0
        self.sumB = 0
        self.sumTeams(k1)

    def sumTeams(self, k):
        lengthA = len(self.teamA)
        lengthB = len(self.teamB)
        for i in range(lengthA):
            self.sumA += self.teamA[i].totalScore
        for i in range(lengthB):
            self.sumB += self.teamB[i].totalScore
        # Adjust for unequal player counts
        factor = (lengthB / lengthA) ** (1 / k)
        self.sumA *= factor



# testing
#WR
player1_data = pd.DataFrame({
    'points': [10, 20, 15, 30, 25, 18, 22],
    'schedule_strength': [5, 10, 8, 20, 12, 15, 10]
})

#WR
player2_data = pd.DataFrame({
    'points': [12, 17, 9, 28, 23, 14, 19],
    'schedule_strength': [7, 11, 5, 21, 13, 14, 9]
})

#TE
player3_data = pd.DataFrame({
    'points': [8, 25, 13, 20, 30, 15, 10],
    'schedule_strength': [3, 8, 9, 25, 15, 16, 11]
})

#QB
player4_data = pd.DataFrame({
    'points': [14, 18, 16, 29, 26, 20, 12],
    'schedule_strength': [6, 9, 7, 18, 14, 10, 8]
})

#RB
player5_data = pd.DataFrame({
    'points': [5, 19, 22, 27, 24, 17, 11],
    'schedule_strength': [4, 12, 6, 22, 16, 13, 10]
})

#WR
player6_data = pd.DataFrame({
    'points': [11, 15, 10, 23, 21, 16, 14],
    'schedule_strength': [8, 10, 7, 19, 12, 18, 9]
})
wrAvg = 13
rbAvg = 17
qbAvg = 18
teAvg = 11
wrDev = 2.5
rbDev = 2
qbDev =1
teDev = 3
zMin = -2.5
zMax = 2.5
numPlayers = 6
#init: gameData,  positionAvg, positionDev, zMin, zMax, ranking, numPlayers
player1 = Player(player1_data, wrAvg, wrDev, zMin, zMax, 3, numPlayers)
player2 = Player(player2_data, wrAvg, wrDev, zMin, zMax, 4, numPlayers)
player3 = Player(player3_data, teAvg, teDev, zMin, zMax, 5, numPlayers)
player4 = Player(player4_data, qbAvg, qbDev, zMin, zMax, 1, numPlayers)
player5 = Player(player5_data, rbAvg, rbDev, zMin, zMax, 2, numPlayers)
player6 = Player(player6_data, wrAvg, wrDev, zMin, zMax, 6, numPlayers)


teamA = [player2, player4]
teamB = [player5, player1]

# Perform Trade
trade1 = Trade(teamA, teamB)
print("Trade 1:")
print("Team A Score:", trade1.sumA)
print("Team B Score:", trade1.sumB)