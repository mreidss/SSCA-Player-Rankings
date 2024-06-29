import requests
import pandas as pd

# Define the list of grades with their IDs
grades = {
    '2022-2023': {
        'A1': 'f3a5cd22-3e0f-4015-a83f-524041c02604',
        'A2': '45c5bdc7-7522-4b4f-b1fe-3cf6b0388fdc',
        'B1': '36d25d27-6f0e-46c7-b08b-32674e6d5072',
        'B2': '2d115353-0146-483e-b582-1366b6369f41',
        'B3': '5563b108-f19c-4a2f-9a0a-930ec645e11b',
        'B4': '4a3e16d1-ce1d-4632-b9e5-b198cd95f2bc',
        'C1': 'ff9cd850-ae40-46b2-83f7-5123127804cc'
    },
    '2023-2024': {
        'A1': 'faac1044-0ab6-4ffa-875f-c3474c909a9a',
        'A2': '3dc5d900-292f-4c1a-8122-f315fa66edb7',
        'B1': 'eb7777d1-2a81-47ad-8859-3aec15022bb9',
        'B2': '67117794-a5f8-4767-b86b-9e9801a55269',
        'B3': 'a56c4725-d12c-4455-a559-f0b9d20adf1b',
        'B4': 'e334c797-d7ef-4f59-abf1-aa879772c8ab',
        'C1': '7fafa153-8e28-43ce-bd24-272bf9b0a26a'
    }
}
# Initialize empty lists to hold the stats
all_batting_stats = []
all_bowling_stats = []
all_fielding_stats = []

# Loop through each year and grade to fetch the stats
for year, year_grades in grades.items():
    for grade_name, grade_id in year_grades.items():
        # Define the URLs for the APIs
        batting_url = f"https://stats-community.cricket.com.au/api/getBattingStats?grade_id={grade_id}&options_type=false"
        bowling_url = f"https://stats-community.cricket.com.au/api/getBowlingStats?grade_id={grade_id}&options_type=false"
        fielding_url = f"https://stats-community.cricket.com.au/api/getFieldingStats?grade_id={grade_id}&options_type=false"

        # Fetch the data
        batting_data = requests.get(batting_url).json()
        bowling_data = requests.get(bowling_url).json()
        fielding_data = requests.get(fielding_url).json()

        # Extract the relevant statistics and create DataFrames
        batting_stats = [{'year': year, 'player_id': player['Id'], 'player_name': player['Name'], 
                          'PlayerClub': player['Organisation']['Name'], 
                          'Grade': grade_name,
                          'BattingAggregate': player['Statistics']['BattingAggregate'], 
                          'BattingNotOuts': player['Statistics']['BattingNotOuts'], 
                          'Batting50s': player['Statistics']['Batting50s'], 
                          'Batting100s': player['Statistics']['Batting100s']} for player in batting_data]
        
        bowling_stats = [{'year': year, 'player_id': player['Id'], 'player_name': player['Name'], 
                          'Grade': grade_name,
                          'BowlingWickets': player['Statistics']['BowlingWickets'], 
                          'BowlingMaidens': player['Statistics']['BowlingMaidens'], 
                          'Bowling5WIs': player['Statistics']['Bowling5WIs']} for player in bowling_data]
        
        fielding_stats = [{'year': year, 'player_id': player['Id'], 'player_name': player['Name'], 
                           'Grade': grade_name,
                           'FieldingTotalCatches': player['Statistics']['FieldingTotalCatches'], 
                           'FieldingRunOuts': player['Statistics']['FieldingRunOuts'], 
                           'FieldingStumpings': player['Statistics']['FieldingStumpings']} for player in fielding_data]

        # Append the stats to the corresponding lists
        all_batting_stats.extend(batting_stats)
        all_bowling_stats.extend(bowling_stats)
        all_fielding_stats.extend(fielding_stats)


batting_df = pd.DataFrame(all_batting_stats)
bowling_df = pd.DataFrame(all_bowling_stats)
fielding_df = pd.DataFrame(all_fielding_stats)

batting_df = batting_df.groupby(['player_id', 'player_name', 'year', 'Grade']).sum().reset_index()  
bowling_df = bowling_df.groupby(['player_id', 'player_name', 'year', 'Grade']).sum().reset_index()  
fielding_df = fielding_df.groupby(['player_id', 'player_name', 'year', 'Grade']).sum().reset_index()  

# Merge the DataFrames on the player ID
combined_df = pd.merge(batting_df, bowling_df, on=['player_id', 'player_name', 'year', 'Grade'], suffixes=('_bat', '_bowl'))
combined_df = pd.merge(combined_df, fielding_df, on=['player_id', 'player_name', 'year', 'Grade'])





# Calculate a combined score for each player
# Adjust the weights based on their importance
weights = {
    'BattingAggregate': 0.05,
    'BattingNotOuts': 1,
    'Batting50s': 1,
    'Batting100s': 2,
    'BowlingWickets': 1,
    'BowlingMaidens': 0.25,
    'Bowling5WIs': 2,
    'FieldingTotalCatches': 1,
    'FieldingRunOuts': 1,
    'FieldingStumpings': 1
}

# Define the weights for each grade
grade_weights = {
    'A1': 1.0,
    'A2': 0.9,
    'B1': 0.8,
    'B2': 0.7,
    'B3': 0.6,
    'B4': 0.55,
    'C1': 0.5
}

# Add a new column to store the grade weight
combined_df['GradeWeight'] = combined_df['Grade'].map(grade_weights)

# Calculate the combined score with grade weighting
combined_df['combined_score'] = (
    combined_df['BattingAggregate'] * weights['BattingAggregate'] * combined_df['GradeWeight'] +
    combined_df['BattingNotOuts'] * weights['BattingNotOuts'] * combined_df['GradeWeight'] +
    combined_df['Batting50s'] * weights['Batting50s'] * combined_df['GradeWeight'] +
    combined_df['Batting100s'] * weights['Batting100s'] * combined_df['GradeWeight'] +
    combined_df['BowlingWickets'] * weights['BowlingWickets'] * combined_df['GradeWeight'] +
    combined_df['BowlingMaidens'] * weights['BowlingMaidens'] * combined_df['GradeWeight'] +
    combined_df['Bowling5WIs'] * weights['Bowling5WIs'] * combined_df['GradeWeight'] +
    combined_df['FieldingTotalCatches'] * weights['FieldingTotalCatches'] * combined_df['GradeWeight'] +
    combined_df['FieldingRunOuts'] * weights['FieldingRunOuts'] * combined_df['GradeWeight'] +
    combined_df['FieldingStumpings'] * weights['FieldingStumpings'] * combined_df['GradeWeight']
)


#print(combined_df['BattingAggregate'].dtype)
# print(bowling_df[bowling_df['player_name'] == 'Gill, Justin'])

# Aggregate the statistics for players appearing in multiple grades
#aggregated_df = combined_df.groupby(['player_id', 'player_name', 'PlayerClub']).sum().reset_index()
aggregated_df = combined_df.groupby(['player_id', 'player_name', 'PlayerClub', 'year']).sum().reset_index()


# aggregated_df = combined_df.groupby(['player_id', 'player_name']).agg({
#     **{col: 'um' for col in combined_df.columns if col != 'Grade'},
#     'Grade': lambda x: ', '.join(x.astype(str))
# }).reset_index()

# aggregated_df['combined_score'] = (
#     aggregated_df['BattingAggregate'] * weights['BattingAggregate'] +
#     aggregated_df['BattingNotOuts'] * weights['BattingNotOuts'] +
#     aggregated_df['Batting50s'] * weights['Batting50s'] +
#     aggregated_df['Batting100s'] * weights['Batting100s'] +
#     aggregated_df['BowlingWickets'] * weights['BowlingWickets'] +
#     aggregated_df['BowlingMaidens'] * weights['BowlingMaidens'] +
#     aggregated_df['Bowling5WIs'] * weights['Bowling5WIs'] +
#     aggregated_df['FieldingTotalCatches'] * weights['FieldingTotalCatches'] +
#     aggregated_df['FieldingRunOuts'] * weights['FieldingRunOuts'] +
#     aggregated_df['FieldingStumpings'] * weights['FieldingStumpings']
# )

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
aggregated_df['rank'] = aggregated_df['combined_score'].rank(ascending=False)

# Sort the DataFrame by the rank
sorted_df = aggregated_df.sort_values(by='rank')

# tell panda to print all rows
pd.set_option('display.max_rows', None)

#print(combined_df)
# Display the sorted DataFrame
print(sorted_df[['year', 'player_name', 'PlayerClub', 'Grade', 'BattingAggregate', 'BattingNotOuts', 'Batting50s', 'Batting100s', 'BowlingWickets', 'BowlingMaidens', 'Bowling5WIs', 'FieldingTotalCatches', 'FieldingStumpings', 'combined_score', 'rank']])








######### Working well but need to come up with a solution for grade weighting when stats are scored in muliple grades.













# # Define the URLs for the APIs
# batting_url = "https://stats-community.cricket.com.au/api/getBattingStats?grade_id=faac1044-0ab6-4ffa-875f-c3474c909a9a&options_type=false"
# bowling_url = "https://stats-community.cricket.com.au/api/getBowlingStats?grade_id=faac1044-0ab6-4ffa-875f-c3474c909a9a&options_type=false"
# fielding_url = "https://stats-community.cricket.com.au/api/getFieldingStats?grade_id=faac1044-0ab6-4ffa-875f-c3474c909a9a&options_type=false"

# # Fetch the data
# batting_data = requests.get(batting_url).json()
# bowling_data = requests.get(bowling_url).json()
# fielding_data = requests.get(fielding_url).json()

# # # Extract the relevant statistics and create DataFrames
# batting_stats = [{'player_id': player['Id'], 'player_name': player['Name'], 
#                   'BattingAggregate': player['Statistics']['BattingAggregate'], 
#                   'PlayerClub': player['Organisation']['Name'], 
#                   'BattingNotOuts': player['Statistics']['BattingNotOuts'], 
#                   'Batting50s': player['Statistics']['Batting50s'], 
#                   'Batting100s': player['Statistics']['Batting100s']} for player in batting_data]
# bowling_stats = [{'player_id': player['Id'], 'player_name': player['Name'], 
#                   'BowlingWickets': player['Statistics']['BowlingWickets'], 
#                   'BowlingMaidens': player['Statistics']['BowlingMaidens'], 
#                   'Bowling5WIs': player['Statistics']['Bowling5WIs']} for player in bowling_data]
# fielding_stats = [{'player_id': player['Id'], 'player_name': player['Name'], 
#                    'FieldingTotalCatches': player['Statistics']['FieldingTotalCatches'], 
#                    'FieldingRunOuts': player['Statistics']['FieldingRunOuts'], 
#                    'FieldingStumpings': player['Statistics']['FieldingStumpings']} for player in fielding_data]