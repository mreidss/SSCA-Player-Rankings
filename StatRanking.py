import requests
import pandas as pd

# Define the URLs for the APIs
batting_url = "https://stats-community.cricket.com.au/api/getBattingStats?grade_id=faac1044-0ab6-4ffa-875f-c3474c909a9a&options_type=false"
bowling_url = "https://stats-community.cricket.com.au/api/getBowlingStats?grade_id=faac1044-0ab6-4ffa-875f-c3474c909a9a&options_type=false"
fielding_url = "https://stats-community.cricket.com.au/api/getFieldingStats?grade_id=faac1044-0ab6-4ffa-875f-c3474c909a9a&options_type=false"

# Fetch the data
batting_data = requests.get(batting_url).json()
bowling_data = requests.get(bowling_url).json()
fielding_data = requests.get(fielding_url).json()

# # Extract the relevant statistics and create DataFrames
batting_stats = [{'player_id': player['Id'], 'player_name': player['Name'], 
                  'BattingAggregate': player['Statistics']['BattingAggregate'], 
                  'PlayerClub': player['Organisation']['Name'], 
                  'BattingNotOuts': player['Statistics']['BattingNotOuts'], 
                  'Batting50s': player['Statistics']['Batting50s'], 
                  'Batting100s': player['Statistics']['Batting100s']} for player in batting_data]
bowling_stats = [{'player_id': player['Id'], 'player_name': player['Name'], 
                  'BowlingWickets': player['Statistics']['BowlingWickets'], 
                  'BowlingMaidens': player['Statistics']['BowlingMaidens'], 
                  'Bowling5WIs': player['Statistics']['Bowling5WIs']} for player in bowling_data]
fielding_stats = [{'player_id': player['Id'], 'player_name': player['Name'], 
                   'FieldingTotalCatches': player['Statistics']['FieldingTotalCatches'], 
                   'FieldingRunOuts': player['Statistics']['FieldingRunOuts'], 
                   'FieldingStumpings': player['Statistics']['FieldingStumpings']} for player in fielding_data]

batting_df = pd.DataFrame(batting_stats)
bowling_df = pd.DataFrame(bowling_stats)
fielding_df = pd.DataFrame(fielding_stats)

# Merge the DataFrames on the player ID
combined_df = pd.merge(batting_df, bowling_df, on=['player_id', 'player_name'], suffixes=('_bat', '_bowl'))
combined_df = pd.merge(combined_df, fielding_df, on=['player_id', 'player_name'])

# Calculate a combined score for each player
# Adjust the weights based on their importance
combined_df['combined_score'] = (
    combined_df['BattingAggregate'] * 0.05 +    # Batting Agg
    combined_df['BattingNotOuts'] * 1 +      # Not Outs
    combined_df['Batting50s'] * 1 +          # 50's
    combined_df['Batting100s'] * 2 +         # 100's
    combined_df['BowlingWickets'] * 1 +        # Bowling Wickets
    combined_df['BowlingMaidens'] * 0.25 +         # Maidens
    combined_df['Bowling5WIs'] * 2 +            # 5 Wicket Halls
    combined_df['FieldingTotalCatches'] * 1 +   # FielderCatches
    combined_df['FieldingRunOuts'] * 1 +        # Runouts 
    combined_df['FieldingStumpings'] * 1        # Stumpings
)

# Batting Aggregate: 0.05
# Not outs: 1
# 50's: 1
# 100's: 2
# Wickets: 1
# Maidens: 0.5
# 5 wicket halls: 2
# Catches: 1
# WK Catches: 1
# Runouts 
# Stumpings: 1

# Rank the players based on the combined score
combined_df['rank'] = combined_df['combined_score'].rank(ascending=False)

# Sort the DataFrame by the rank
sorted_df = combined_df.sort_values(by='rank')

# tell panda to print all rows
pd.set_option('display.max_rows', None)
# Display the sorted DataFrame
print(sorted_df[['player_id', 'player_name', 'PlayerClub', 'BattingAggregate', 'BattingNotOuts', 'Batting50s', 'Batting100s', 'BowlingWickets', 'BowlingMaidens', 'Bowling5WIs', 'FieldingTotalCatches', 'FieldingStumpings', 'combined_score', 'rank']])

