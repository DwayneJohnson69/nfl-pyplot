import pandas as pd
from scrape import scrape_player_page
from scrape import scrape_team_page
import numpy as np

#update csvs from metata given a range of years
def player_team_data_to_csvs(years):
    categories = ['passing',  'rushing', 'receiving', 'scrimmage', 'defense',  'kicking', 'returns', 'scoring']
    team_table_ids = ['AFC', 'NFC', 'team_stats', 'passing', 'rushing', 'returns', 'kicking', 'team_scoring', 'team_conversions', 'drives']
    def_table_ids = ['team_stats', 'advanced_defense', 'passing', 'rushing', 'returns', 'kicking', 'team_scoring', 'team_conversions', 'drives']

    player_df_dict = {}
    for cat in categories:
        player_df_dict[cat] = pd.DataFrame()

    team_df_dict = {}
    for table_id in team_table_ids:
        team_df_dict[table_id] = pd.DataFrame()

    def_df_dict = {}
    for table_id in def_table_ids:
        def_df_dict[table_id] = pd.DataFrame()

    for year in years:
        print(year, '...')
        for cat in categories:
            print(cat, '...')
            df = scrape_player_page(year, cat)
            df['Year'] = year
            df['Player'] = df['Player'].str.strip('*+')
            player_df_dict[cat] = player_df_dict[cat].append(df)

        print('team data...')
        temp_team_df_dict, temp_def_df_dict = scrape_team_page(year)

        for table_id in team_table_ids:
            temp_team_df_dict[table_id]['Year'] = year
            team_df_dict[table_id] = team_df_dict[table_id].append(temp_team_df_dict[table_id])
        for table_id in def_table_ids:
            temp_def_df_dict[table_id]['Year'] = year
            def_df_dict[table_id] = def_df_dict[table_id].append(temp_def_df_dict[table_id])
        
    #clean dataframes 
    for cat in categories:  
        player_df_dict[cat].columns = player_df_dict[cat].columns.str.replace('%', '_perc')
        player_df_dict[cat]['Pos'] = player_df_dict[cat]['Pos'].str.upper().fillna(np.nan).str.lstrip('/').str.rstrip('/')
        for col in player_df_dict[cat].columns:
            try:
                if player_df_dict[cat][col].dtypes == 'object':
                    player_df_dict[cat][col] = player_df_dict[cat][col].str.rstrip('%')
            except Exception:
                pass

    for category in team_table_ids:
        team_df_dict[category].columns = team_df_dict[category].columns.str.replace('%', '_perc')
        for col in team_df_dict[category].columns:
            try: 
                if team_df_dict[category][col].dtypes == 'object':
                    team_df_dict[category][col] = team_df_dict[category][col].str.rstrip('%')
            except Exception:
                pass

    for category in def_table_ids:
        def_df_dict[category].columns = def_df_dict[category].columns.str.replace('%', '_perc')
        for col in def_df_dict[category].columns:
            try: 
                if def_df_dict[category][col].dtypes == 'object':
                    def_df_dict[category][col] = def_df_dict[category][col].str.rstrip('%')
            except Exception:
                pass
                
    #merge team dataframes 
    temp_def_df_dict = def_df_dict
    for table_id in def_table_ids:
        if table_id not in ['advanced_defense']:
            temp_def_df_dict[table_id] = temp_def_df_dict[table_id].set_index(['Tm', 'Year'])
            for col in temp_def_df_dict[table_id].columns:
                temp_def_df_dict[table_id] = temp_def_df_dict[table_id].rename(columns={col : 'opp_{}'.format(col)})

    merged_table_ids = ['team_stats', 'passing', 'rushing', 'returns', 'kicking', 'team_scoring', 'team_conversions', 'drives']
    merged_df_dict = {}
    temp_team_df_dict = team_df_dict
    for table_id in merged_table_ids:
        temp_team_df_dict[table_id] = temp_team_df_dict[table_id].set_index(['Tm', 'Year'])
        merged_df_dict[table_id] = pd.merge(temp_team_df_dict[table_id], temp_def_df_dict[table_id], left_index = True, right_index = True)
        merged_df_dict[table_id] = merged_df_dict[table_id].reset_index()
        
    #Save csvs
    try: 
        for category, df in player_df_dict.items():
            df = df[df['Player'].notna()]
            df.to_csv(r'data/players/{}.csv'.format(category))
            print('Saved {} as .csv'.format(category))
    except:
        print('Unable to save player {} as a CSV'.format(category))
    
    team_file_names = {'AFC': 'AFC', 'NFC' : 'NFC', 'team_stats' : 'team_stats', 'passing' : 'team_passing', 'rushing' : 'team_rushing', \
                'returns' : 'team_returns', 'kicking' : 'team_kicking', 'team_scoring' : 'team_scoring', 'team_conversions' : 'team_conversions', \
                'drives' : 'team_drives'}
    try:
        for table_id in team_table_ids:
            team_df_dict[table_id].to_csv(r'data/teams/{}.csv'.format(team_file_names[table_id]))
            print('Saved {} as .csv'.format(table_id))
    except:
        print('Unable to save team {} as a CSV'.format(table_id))

    def_file_names = {'team_stats': 'opp_team_stats', 'advanced_defense': 'opp_advanced_defense', \
        'passing': 'opp_passing', 'rushing' : 'opp_rushing', 'returns' : 'opp_returns', \
        'kicking' : 'opp_kicking', 'team_scoring' : 'opp_team_scoring', 'team_conversions': 'opp_team_conversions', \
        'drives' : 'opp_drives'}

    for table_id in def_table_ids:
        try:
            def_df_dict[table_id].to_csv(r'data/teams/{}.csv'.format(def_file_names[table_id]))
            print('Saved oppenent {} as .csv'.format(table_id))
        except: 
            print('Unable to save opponent {} as a CSV'.format(table_id))

    merged_file_names = {'team_stats': 'merged_team_stats', \
        'passing': 'merged_passing', 'rushing' : 'merged_rushing', 'returns' : 'merged_returns', \
        'kicking' : 'merged_kicking', 'team_scoring' : 'merged_team_scoring', 'team_conversions': 'merged_team_conversions', \
        'drives' : 'merged_drives'}

    for table_id in merged_table_ids:
        try:
            merged_df_dict[table_id].to_csv(r'data/teams/{}.csv'.format(merged_file_names[table_id]))
            print('Saved merged {} as csv'.format(table_id))
        except Exception:
            print('Unable to save merged {} as a CSV'.format(table_id))

if __name__ == '__main__':
    #scrapes player and team stats for a range of years as the input 
    player_team_data_to_csvs(range(2006, 2022))
