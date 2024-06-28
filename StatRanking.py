import requests
import pandas as pd

# Define the URLs for the APIs
batting_url = "https://stats-community.cricket.com.au/api/getBattingStats?grade_id=faac1044-0ab6-4ffa-875f-c3474c909a9a&options_type="
bowling_url = "https://stats-community.cricket.com.au/api/getBowlingStats?grade_id=faac1044-0ab6-4ffa-875f-c3474c909a9a&options_type="
fielding_url = "https://stats-community.cricket.com.au/api/getFieldingStats?grade_id=faac1044-0ab6-4ffa-875f-c3474c909a9a&options_type="

# Fetch the data
batting_data = requests.get(batting_url).json()
bowling_data = requests.get(bowling_url).json()
fielding_data = requests.get(fielding_url).json()

# # Extract the relevant statistics and create DataFrames
batting_stats = [{'player_id': player['Id'], 'player_name': player['Name'], 'batting_agg': player['Statistics']['BattingAggregate']} for player in batting_data]
bowling_stats = [{'player_id': player['Id'], 'player_name': player['Name'], 'bowling_Wickets': player['Statistics']['BowlingWickets']} for player in bowling_data]
fielding_stats = [{'player_id': player['Id'], 'player_name': player['Name'], 'catches': player['Statistics']['FieldingTotalCatches']} for player in fielding_data]

batting_df = pd.DataFrame(batting_stats)
bowling_df = pd.DataFrame(bowling_stats)
fielding_df = pd.DataFrame(fielding_stats)

# Merge the DataFrames on the player ID
combined_df = pd.merge(batting_df, bowling_df, on=['player_id', 'player_name'], suffixes=('_bat', '_bowl'))
combined_df = pd.merge(combined_df, fielding_df, on=['player_id', 'player_name'])

# Calculate a combined score for each player
# Adjust the weights based on their importance
combined_df['combined_score'] = (
    combined_df['batting_agg'] * 0.05 +  # Replace with the actual weight
    combined_df['bowling_Wickets'] * 1 +  # Replace with the actual weight
    combined_df['catches'] * 1           # Replace with the actual weight
)

# Rank the players based on the combined score
combined_df['rank'] = combined_df['combined_score'].rank(ascending=False)

# Sort the DataFrame by the rank
sorted_df = combined_df.sort_values(by='rank')

# Display the sorted DataFrame
print(sorted_df[['player_id', 'player_name', 'batting_agg', 'bowling_Wickets', 'catches', 'combined_score', 'rank']])

