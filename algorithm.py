import numpy as np
import pandas as pd

class PlayerProductionRating:
    def __init__(self, player_data, position_avg, position_std, num_players, ranking):
        """
        Initialize the class with player data and other constants.

        player_data: DataFrame with columns ['points', 'schedule_strength']
        position_avg: float, average points for player's position
        position_std: float, standard deviation of points for player's position
        num_players: int, total number of players
        ranking: int, ranking of the player
        """
        self.player_data = player_data
        self.position_avg = position_avg
        self.position_std = position_std
        self.num_players = num_players
        self.ranking = ranking
        self.production_rating = 0
        self.ranking_rating = 0
        self.total_score = 0

    def calculate_production_rating(self):
        # Assign weights for recent games and calculate weighted points
        weights = np.array([1.5 if i >= len(self.player_data) - 3 else 1 for i in range(len(self.player_data))]) #1.5 weight of recent games
        weighted_points = np.dot(self.player_data['points'], weights) / weights.sum()

        # Adjust points by schedule strength and calculate weighted average
        schedule_adjustment = 1 - .1*(self.player_data['schedule_strength'] - 1) / 31 #set k = .1 for now 
        adjusted_points = self.player_data['points'] * schedule_adjustment
        weighted_avg_points = np.dot(adjusted_points, weights) / weights.sum()

        # Calculate production rating based on z-score
        z_score = (weighted_avg_points - self.position_avg) / self.position_std
        z_score += 3 #Assume minimum z-score of negative 3 for now 
        self.production_rating = z_score*(100/6)  # Assume max z-score of 3 for now 

        # Apply penalty for low performance outliers
        q1 = self.player_data['points'].quantile(0.25)
        penalty_factor = max(0, 1 - 0.1 * (self.player_data['points'] < q1).mean()) #set k = .1 for now 
        self.production_rating *= penalty_factor

    def calculate_ranking_rating(self):
        # Calculate percentile ranking out of 100
        self.ranking_rating = ((self.num_players - self.ranking) / (self.num_players - 1)) * 100

    def calculate_total_score(self, w1=0.6, w2=0.4, future_schedule_strength=16):
        # Calculate weighted average of production and ranking ratings
        base_score = (w1 * self.production_rating + w2 * self.ranking_rating) / (w1 + w2)

        # Adjust for future schedule strength
        factor = 1 - 0.1 + 0.1 * (future_schedule_strength - 1) / 31
        self.total_score = base_score * factor

    def analyze_trade(self, players_side_a, players_side_b, k=0.1):
        """
        Analyze trade by comparing total scores for each side.

        players_side_a: list of total scores for players on side A
        players_side_b: list of total scores for players on side B
        k: penalty factor for unequal players in trade
        """
        score_a, score_b = sum(players_side_a), sum(players_side_b)

        # Apply penalty for unequal player count if necessary
        if len(players_side_a) != len(players_side_b):
            score_a *= (len(players_side_b) / len(players_side_a)) ** (1 / k)

        return score_a, score_b

# Example Usage
player_data = pd.DataFrame({
    'points': [10, 20, 15, 30, 25, 18, 22],
    'schedule_strength': [5, 10, 8, 20, 12, 15, 10]
})

# Initialize with hypothetical data
player = PlayerProductionRating(player_data, position_avg=20.0, position_std=5.0, num_players=100, ranking=20)

# Calculate ratings and scores
player.calculate_production_rating()
print("Production Rating:", player.production_rating)

player.calculate_ranking_rating()
print("Ranking Rating:", player.ranking_rating)

player.calculate_total_score()
print("Total Score:", player.total_score)

# Analyze trade scenario
players_side_a = [player.total_score, 40]
players_side_b = [player.total_score, 100]
trade_result = player.analyze_trade(players_side_a, players_side_b)
print("Trade Scores (Side A, Side B):", trade_result)


# n1, n2 