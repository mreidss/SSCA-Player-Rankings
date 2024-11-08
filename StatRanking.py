import requests
import pandas as pd
import numpy as np
import re

# Define the list of grades with their IDs
grades = {
    '2022-2023': {
        '1st': 'a24041d3-782a-45aa-bd30-967b7fc514b7',
        '2nd': 'bdcf8810-24fb-4e2b-b80a-ca227506502d',
        '3rd': 'e03d64ea-c735-4fcb-8975-43ec4f530d76',
        '4th': 'df93397a-ca39-4b22-9cfb-44b6d8a23602',
        '5th': '60043cd8-0205-4a88-8b4e-3998bc226238',
        'GreenShield': '32bcb9f2-48dd-4b56-92ff-630b08250d9d',
        'A1': 'f3a5cd22-3e0f-4015-a83f-524041c02604',
        'A2': '45c5bdc7-7522-4b4f-b1fe-3cf6b0388fdc',
        'B1': '36d25d27-6f0e-46c7-b08b-32674e6d5072',
        'B2': '2d115353-0146-483e-b582-1366b6369f41',
        'B3': '5563b108-f19c-4a2f-9a0a-930ec645e11b',
        'B4': '4a3e16d1-ce1d-4632-b9e5-b198cd95f2bc',
        'C1': 'ff9cd850-ae40-46b2-83f7-5123127804cc',
        '16A': '68dda557-1bd1-4e70-9351-7068cfa208a1',
        '16B': '2f705d44-c11e-449b-8250-944c47de8406'
    },
    '2023-2024': {
        '1st': '44e7ea73-36b0-4782-9380-71460944cb60',
        '2nd': '43fbb17f-df24-4459-bb62-b685ca536acc',
        '3rd': '847b49b7-ec93-4f11-bead-484a579615f8',
        '4th': '128c0d3f-2fe2-40fe-9202-5b4564fe44a9',
        '5th': '6609fb3e-ee3f-42a5-b1f3-a647432e5e3a',
        'GreenShield': 'c86175dd-8cd0-4e7b-969e-0c90a61427ce',
        'MetroCup': 'bc0a5589-88cc-459b-b8dd-60b32e0dcf5b',
        'A1': 'faac1044-0ab6-4ffa-875f-c3474c909a9a',
        'A2': '3dc5d900-292f-4c1a-8122-f315fa66edb7',
        'B1': 'eb7777d1-2a81-47ad-8859-3aec15022bb9',
        'B2': '67117794-a5f8-4767-b86b-9e9801a55269',
        'B3': 'a56c4725-d12c-4455-a559-f0b9d20adf1b',
        'B4': 'e334c797-d7ef-4f59-abf1-aa879772c8ab',
        'B5': '14d12ef7-57db-4fcc-be09-7a8158d66df1',
        'C1': '7fafa153-8e28-43ce-bd24-272bf9b0a26a',
        '16A': '0e45acf1-98a1-4df8-9780-e469a4adbb70',
        '16B': 'cbc93f76-2279-4437-a9c3-d1bdac72f593'
    }
}

# Define the weights for each grade
grade_weights = {
    '1st': 1.3,
    '2nd': 1.25,
    '3rd': 1.2,
    '4th': 1.15,
    '5th': 1.05,
    'GreenShield': 1.0,
    'MetroCup': 1.0,
    'A1': 1.0,
    'A2': 0.95,
    'B1': 0.85,
    'B2': 0.8,
    'B3': 0.75,
    'B4': 0.7,
    'B5': 0.65,
    'C1': 0.6,
    '16A': 0.85,
    '16B': 0.8
}

# Calculate a combined score for each player
# Adjust the weights based on their importance
weights = {
    'BattingAggregate': 0.1,
    #'BattingNotOuts': 0.5,
    #'Batting50s': 1,
    #'Batting100s': 1,
    'BowlingWickets': 1,
    #'BowlingMaidens': 0.5,
    #'Bowling5WIs': 2,
    'FieldingTotalCatches': 0.5,
    'FieldingRunOuts': 0.5,
    'FieldingStumpings': 1
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

# batting_df['PlayerClub'] = batting_df.groupby(['player_id', 'year'])['PlayerClub'].transform(lambda x: ','.join(x))
# batting_df['PlayerClub'] = batting_df.groupby(['player_id', 'year'])['PlayerClub'].transform(lambda x: x.iloc[0])
#batting_df['PlayerClub'] = batting_df.groupby(['player_id', 'year'])['PlayerClub'].transform(lambda x: next(iter(set(x))))


# Merge the DataFrames on the player ID
combined_df = pd.merge(batting_df, bowling_df, on=['player_id', 'player_name', 'year', 'Grade'], suffixes=('_bat', '_bowl'))
combined_df = pd.merge(combined_df, fielding_df, on=['player_id', 'player_name', 'year', 'Grade'])








###### Old weights
# Calculate a combined score for each player
# Adjust the weights based on their importance
# weights = {
#     'BattingAggregate': 0.1,
#     'BattingNotOuts': 0.5,
#     'Batting50s': 1,
#     'Batting100s': 1,
#     'BowlingWickets': 1,
#     'BowlingMaidens': 0.5,
#     'Bowling5WIs': 2,
#     'FieldingTotalCatches': 1,
#     'FieldingRunOuts': 1,
#     'FieldingStumpings': 1
# }

# # Define the weights for each grade
# grade_weights = {
#     'A1': 1.0,
#     'A2': 0.9,
#     'B1': 0.8,
#     'B2': 0.7,
#     'B3': 0.6,
#     'B4': 0.55,
#     'C1': 0.5
# }







# Add a new column to store the grade weight
combined_df['GradeWeight'] = combined_df['Grade'].map(grade_weights)

#print(combined_df)



# Calculate the combined score with grade weighting
combined_df['combined_score'] = (
    combined_df['BattingAggregate'] * weights['BattingAggregate'] * combined_df['GradeWeight'] +
    # combined_df['BattingNotOuts'] * weights['BattingNotOuts'] * combined_df['GradeWeight'] +
    # combined_df['Batting50s'] * weights['Batting50s'] * combined_df['GradeWeight'] +
    # combined_df['Batting100s'] * weights['Batting100s'] * combined_df['GradeWeight'] +
    combined_df['BowlingWickets'] * weights['BowlingWickets'] * combined_df['GradeWeight'] +
    # combined_df['BowlingMaidens'] * weights['BowlingMaidens'] * combined_df['GradeWeight'] +
    # combined_df['Bowling5WIs'] * weights['Bowling5WIs'] * combined_df['GradeWeight'] +
    combined_df['FieldingTotalCatches'] * weights['FieldingTotalCatches'] * combined_df['GradeWeight'] +
    combined_df['FieldingRunOuts'] * weights['FieldingRunOuts'] * combined_df['GradeWeight'] +
    combined_df['FieldingStumpings'] * weights['FieldingStumpings'] * combined_df['GradeWeight']
)


print(combined_df)

# # # Aggregate the statistics for players appearing in multiple grades
# # aggregated_df = combined_df.groupby(['year', 'player_id', 'player_name', 'PlayerClub']).agg({
# #     'Grade': lambda x: ', '.join(x),
# #     'combined_score': 'sum'
# # }).reset_index()

#Aggregate the statistics for players appearing in multiple grades and multiple clubs
# # aggregated_df = combined_df.groupby(['year', 'player_id', 'player_name']).agg({
# #     'PlayerClub': lambda x: ', '.join(x),
# #     'Grade': lambda x: ', '.join(x),
# #     'combined_score': 'sum'
# # }).reset_index()

# Aggregate the statistics for players appearing in multiple grades and multiple clubs and don't repeat the clubs or grades if there are multiple
aggregated_df = combined_df.groupby(['year', 'player_id', 'player_name']).agg({
    'PlayerClub': lambda x: ', '.join(sorted(set(x))), 
    'Grade': lambda x: ', '.join(sorted(set(x))), 
    'combined_score': 'sum'
}).reset_index()


print(aggregated_df)

# Rename the columns
aggregated_df.columns = ['year', 'player_id', 'player_name', 'PlayerClub', 'Grades', 'combined_score']


print(aggregated_df)

# Aggregate the statistics for players appearing in multiple grades
#aggregated_df = combined_df.groupby(['year', 'player_id', 'player_name']).sum().reset_index()











# Rank the players based on the combined score for each year
aggregated_df['rank'] = aggregated_df.groupby('year')['combined_score'].rank(ascending=False)





# tell panda to print all rows
#pd.set_option('display.max_rows', None)





# # Print all data for each player with seperated grade stats year 2022-2023 (e.g., 2022-2023)
def PrintPlayerRankSeperateGrades(year):

    # Only show stats for the specified year
    yearly_stats_df = combined_df[combined_df['year'] == year]

    # Print the resulting DataFrame
    print(yearly_stats_df[['year', 'player_name', 'PlayerClub', 'Grade', 'BattingAggregate', 'BattingNotOuts', 'Batting50s', 'Batting100s', 'BowlingWickets', 'BowlingMaidens', 'Bowling5WIs', 'FieldingTotalCatches', 'FieldingRunOuts', 'FieldingStumpings', 'combined_score']])

    # Export the resulting DataFrame to an Excel file
    yearly_stats_df[['year', 'player_name', 'PlayerClub', 'Grade', 'BattingAggregate', 'BattingNotOuts', 'Batting50s', 'Batting100s', 'BowlingWickets', 'BowlingMaidens', 'Bowling5WIs', 'FieldingTotalCatches', 'FieldingRunOuts', 'FieldingStumpings', 'combined_score']].to_excel(f'PlayerStats_{year}.xlsx', index=False)


    # ##### Print Ranks over both years
def PrintCombinedRankOverAllYears():
    # # # Pivot the data to create a column for each year
    pivoted_df = aggregated_df.pivot_table(index=['player_id', 'player_name', 'PlayerClub'],
                                            columns='year',
                                            values='combined_score',
                                            aggfunc=lambda x: ','.join(aggregated_df.loc[x.index, 'Grades']) + ' ' + str(round(x.values[0], 2)))

    # Reset the index and rename the columns
    pivoted_df = pivoted_df.reset_index()
    pivoted_df.columns = ['player_id', 'player_name', 'PlayerClub', '2022-2023', '2023-2024']

    # Fill NaN values with an empty string
    pivoted_df = pivoted_df.fillna('')

    # Add a rank column based on the average combined score
    pivoted_df['average_combined_score'] = pivoted_df[['2022-2023', '2023-2024']].apply(lambda x: np.mean([float(y.split(' ')[1]) for y in x if y]), axis=1)
    pivoted_df['rank'] = pivoted_df['average_combined_score'].rank(ascending=False).astype(int)

    # Sort the DataFrame by the 'rank' column
    #####pivoted_df = pivoted_df.sort_values(by='rank',ascending=False)
    pivoted_df = pivoted_df.sort_values(by='rank')

    # Export the result to an Excel file
    pivoted_df[['rank', 'player_name', 'PlayerClub', '2022-2023', '2023-2024', 'average_combined_score']].to_excel('player_ranks.xlsx', index=False)

    # Print the result
    print(pivoted_df[['rank', 'player_name', 'PlayerClub', '2022-2023', '2023-2024', 'average_combined_score']])


    ### Print top 50
    # # # # # # top_50 = pivoted_df.nlargest(50, 'average_combined_score')
    # # # # # # print(top_50[['rank', 'player_name', 'PlayerClub', '2022-2023', '2023-2024', 'average_combined_score']])

    # Display the sorted DataFrame
    ###############print(pivoted_df[['rank', 'player_name', 'PlayerClub', '2022-2023', '2023-2024', 'average_combined_score']])
    #print(pivoted_df[['rank', 'player_id', 'player_name', 'PlayerClub', '2022-2023', '2023-2024', 'average_combined_score']])



def PrintCombinedRankOverAllYearsFormated():
    # Pivot the data to create a column for each year
    pivoted_df = aggregated_df.pivot_table(index=['player_id', 'player_name', 'PlayerClub'],
                                            columns='year',
                                            values=['combined_score', 'Grades'],
                                            aggfunc={'combined_score': 'mean', 'Grades': lambda x: ', '.join(x)})

    # Reset the index and rename the columns
    pivoted_df = pivoted_df.reset_index()
    pivoted_df.columns = ['player_id', 'player_name', 'PlayerClub', '2022-2023_score', '2022-2023_grade', '2023-2024_score', '2023-2024_grade']

    # Fill NaN values with an empty string
    pivoted_df = pivoted_df.fillna('')

    # make the scores numeric so they can be calculated as an average
    pivoted_df['2022-2023_score'] = pd.to_numeric(pivoted_df['2022-2023_score'], errors='coerce')
    pivoted_df['2023-2024_score'] = pd.to_numeric(pivoted_df['2023-2024_score'], errors='coerce')

    # Add a rank column based on the average combined score
    pivoted_df['average_combined_score'] = pivoted_df[['2022-2023_score', '2023-2024_score']].mean(axis=1)
    pivoted_df['average_combined_score'] = pivoted_df['average_combined_score'].fillna(0)
    pivoted_df['rank'] = pivoted_df['average_combined_score'].rank(ascending=False).astype(int)

    # Sort the DataFrame by the 'rank' column
    pivoted_df = pivoted_df.sort_values(by='rank')

    # Create a new column that combines the score and grade for each year
    # pivoted_df['2022-2023'] = pivoted_df.apply(lambda row: f"{row['2022-2023_grade']} {row['2022-2023_score']:.2f}", axis=1)
    # pivoted_df['2023-2024'] = pivoted_df.apply(lambda row: f"{row['2023-2024_grade']} {row['2023-2024_score']:.2f}", axis=1)

    # Export the result to an Excel file
    pivoted_df[['player_id', 'rank', 'player_name', 'PlayerClub', '2022-2023_score', '2022-2023_grade', '2023-2024_score', '2023-2024_grade', 'average_combined_score']].to_excel('player_ranks.xlsx', index=False)

    # Print the result
    print(pivoted_df[['rank', 'player_name', 'PlayerClub', '2022-2023_score', '2022-2023_grade', '2023-2024_score', '2023-2024_grade', 'average_combined_score']])


# Print player stats and ranks for one year with split grades
#PrintPlayerRankSeperateGrades('2022-2023')
#PrintPlayerRankSeperateGrades('2023-2024')

# Print player stats and ranks combined to find a list of top players SSCA
#PrintCombinedRankOverAllYears()

#PrintCombinedRankOverAllYearsFormated()



# a more formated print function
def print_combined_years(aggregated_df):
    # Pivot the DataFrame to have separate columns for each year
    pivoted_df = aggregated_df.pivot(index=['player_id', 'player_name', 'PlayerClub'], columns='year', values=['Grades', 'combined_score'])
    
    # Flatten the column MultiIndex
    pivoted_df.columns = [f"{year}_{col}" for col, year in pivoted_df.columns]
    
    # Reset the index to include player_id, player_name, and PlayerClub as columns
    pivoted_df = pivoted_df.reset_index()
    
    # Print the resulting DataFrame
    print(pivoted_df)

    # Write the DataFrame to an Excel file
    pivoted_df.to_excel('player_ranks_Formated.xlsx', index=False)


print_combined_years(aggregated_df)



# TODO -- Fix the club names combining because it is creating more than one row in the pivot table
# TODO -- Investigate McMahon, Liam as he is printing twice with the same id and stats for the same yearss




###### Print All player stats for both years with combined grade stats


###### Variable holding all users stats seperated by year
# sorted_SeperatedYears_df = aggregated_df.sort_values(by=['year', 'rank'], ascending=False)
# # Print all users and stats and rankings sperated by year
# print(sorted_SeperatedYears_df[['year', 'player_name', 'PlayerClub', 'Grade', 'BattingAggregate', 'BattingNotOuts', 'Batting50s', 'Batting100s', 'BowlingWickets', 'BowlingMaidens', 'Bowling5WIs', 'FieldingTotalCatches', 'FieldingStumpings', 'combined_score', 'rank']])



















##### Tom Croucher -- email -- tomcroucher49@gmail.com -- Got the address from Michael Mooney




































# # Calculate the combined score with grade weighting
# combined_df['combined_score'] = (
#     combined_df['BattingAggregate'] * weights['BattingAggregate'] * combined_df['GradeWeight'] +
#     combined_df['BattingNotOuts'] * weights['BattingNotOuts'] * combined_df['GradeWeight'] +
#     combined_df['Batting50s'] * weights['Batting50s'] * combined_df['GradeWeight'] +
#     combined_df['Batting100s'] * weights['Batting100s'] * combined_df['GradeWeight'] +
#     combined_df['BowlingWickets'] * weights['BowlingWickets'] * combined_df['GradeWeight'] +
#     combined_df['BowlingMaidens'] * weights['BowlingMaidens'] * combined_df['GradeWeight'] +
#     combined_df['Bowling5WIs'] * weights['Bowling5WIs'] * combined_df['GradeWeight'] +
#     combined_df['FieldingTotalCatches'] * weights['FieldingTotalCatches'] * combined_df['GradeWeight'] +
#     combined_df['FieldingRunOuts'] * weights['FieldingRunOuts'] * combined_df['GradeWeight'] +
#     combined_df['FieldingStumpings'] * weights['FieldingStumpings'] * combined_df['GradeWeight']
# )









# # # # # # Group by player_id and year, and calculate the mean combined score
# # # # # average_scores_df = aggregated_df.groupby(['player_id', 'player_name', 'PlayerClub'])['combined_score'].mean().reset_index()

# # # # # # Sort the DataFrame by the average combined score in descending order
# # # # # average_scores_df = average_scores_df.sort_values(by='combined_score', ascending=False)

# # # # # # Add a rank column based on the average combined score
# # # # # average_scores_df['rank'] = average_scores_df['combined_score'].rank(ascending=False).astype(int)

# # # # # # Display the sorted DataFrame
# # # # # print(average_scores_df[['rank', 'player_name', 'PlayerClub', 'combined_score', 'Grade']])







