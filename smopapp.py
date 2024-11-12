import os
import datetime
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

# Function to create a folder with today's date if it doesn't exist
def create_directory_for_today():
    today = datetime.date.today()
    folder_name = today.strftime('%Y-%m-%d')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

# Function to calculate the probability of score lines and return as a dictionary
def calculate_probability_above_lines(points_estimated, points_lines, std_dev):
    probabilities = {}
    for line in points_lines:
        z_score = (line - points_estimated) / std_dev
        prob_below = norm.cdf(z_score)
        prob_above = 1 - prob_below
        probabilities[line] = prob_above  # Leave as a fraction for now
    return probabilities

# Function to prompt for recent points and opponents' points
def get_team_data(team_name):
    print(f"\nEnter data for {team_name}")
    recent_points = [int(x) for x in input(f"Enter {team_name}'s points scored in recent games (space-separated): ").split()]
    opponent_points = [int(x) for x in input(f"Enter opponents' points against {team_name} in recent games (space-separated): ").split()]
    return recent_points, opponent_points

# Function to get H2H adjustments
def get_h2h_adjustments():
    print("\nEnter head-to-head (H2H) adjustments for specific score combinations.")
    h2h_adjustments = {}
    while True:
        score_a_input = input("Enter Team A score for H2H adjustment (or type 'done' to finish): ").strip()
        if score_a_input.lower() == 'done':
            break
        try:
            score_a = int(score_a_input)
            score_b = int(input("Enter Team B score for H2H adjustment: ").strip())
            adjustment = float(input(f"Enter adjustment factor for score ({score_a}, {score_b}) (e.g., 1.2): ").strip())
            h2h_adjustments[(score_a, score_b)] = adjustment
        except ValueError:
            print("Invalid input. Please enter integers for scores and a decimal for the adjustment factor.")
    return h2h_adjustments

# Function to calculate average and adjusted points
def calculate_avg_points(recent_points, opponent_points):
    baseline_avg_points = np.mean(recent_points)
    avg_opponent_points = np.mean(opponent_points)
    std_dev = np.std(recent_points + opponent_points)
    return baseline_avg_points, avg_opponent_points, std_dev

# Function to predict the outcome using H2H data and normalize probabilities
def predict_outcome(team_a_score_prob, team_b_score_prob, h2h_adjustment):
    outcomes = {"Home Win": 0.0, "Away Win": 0.0, "Draw": 0.0}
    best_outcome = None
    best_probability = 0.0
    total_points_probabilities = {}

    # Calculate unnormalized probabilities for each outcome
    for score_a, prob_a in team_a_score_prob.items():
        for score_b, prob_b in team_b_score_prob.items():
            combined_prob = prob_a * prob_b  # Probabilities are fractions now
            adjustment_factor = h2h_adjustment.get((score_a, score_b), 1)
            adjusted_prob = combined_prob * adjustment_factor
            total_points = score_a + score_b

            # Aggregate total points probabilities
            if total_points not in total_points_probabilities:
                total_points_probabilities[total_points] = 0.0
            total_points_probabilities[total_points] += adjusted_prob

            # Determine outcome type
            if score_a > score_b:
                outcome_type = "Home Win"
            elif score_b > score_a:
                outcome_type = "Away Win"
            else:
                outcome_type = "Draw"

            outcomes[outcome_type] += adjusted_prob

            # Track the best outcome with the highest probability
            if adjusted_prob > best_probability:
                best_probability = adjusted_prob
                best_outcome = outcome_type

    # Normalize the probabilities so they add up to 100%
    total_outcome_prob = sum(outcomes.values())
    for outcome_type in outcomes:
        outcomes[outcome_type] = (outcomes[outcome_type] / total_outcome_prob) * 100

    # Normalize total points probabilities as well
    total_points_sum = sum(total_points_probabilities.values())
    for total_points in total_points_probabilities:
        total_points_probabilities[total_points] = (total_points_probabilities[total_points] / total_points_sum) * 100

    return best_outcome, outcomes[best_outcome], total_points_probabilities

# Main function to bring it all together
def main():
    team_a = input("Enter Team A's name: ")
    team_b = input("Enter Team B's name: ")

    # Get recent points data for both teams
    team_a_recent_points, team_a_opponent_points = get_team_data(team_a)
    team_b_recent_points, team_b_opponent_points = get_team_data(team_b)

    # Calculate average and adjusted points
    team_a_avg, team_a_opponent_avg, std_dev_a = calculate_avg_points(team_a_recent_points, team_a_opponent_points)
    team_b_avg, team_b_opponent_avg, std_dev_b = calculate_avg_points(team_b_recent_points, team_b_opponent_points)

    # Probabilities for each score line based on the average points
    team_a_score_prob = calculate_probability_above_lines(team_a_avg, team_a_recent_points, std_dev_a)
    team_b_score_prob = calculate_probability_above_lines(team_b_avg, team_b_recent_points, std_dev_b)

    # Get head-to-head adjustments
    h2h_adjustment = get_h2h_adjustments()

    # Predict final outcome and probabilities
    outcome, probability, total_points_probabilities = predict_outcome(team_a_score_prob, team_b_score_prob, h2h_adjustment)

    print(f"\nPredicted match outcome is {outcome} with an adjusted probability of {probability:.2f}%")
    print("\nProbabilities for each possible total points outcome:")
    for total_points, prob in total_points_probabilities.items():
        print(f"Total Points: {total_points}, Probability: {prob:.2f}%")

if _name_ == "_main_":
    main()