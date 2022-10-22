from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

"""Fantasy player statistics from pro-football-reference aka PFR
https://www.pro-football-reference.com/"""

def scrape_player_page(year, category):
    url = 'https://www.pro-football-reference.com/years/{}/{}.htm'.format(year, category)

    headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'}
    req = requests.get(url, headers = headers)

    soup = BeautifulSoup(req.content, 'html.parser')
    table = soup.find_all('table')[0]

    dataframe = []
    cols = []

    if category in ['rushing', 'kicking', 'scrimmage', 'defense', 'returns']:
        head = table.find('thead').find_all('tr')[1]
    if category in ['passing', 'receiving', 'scoring']:
        head = table.find('thead').find_all('tr')[0]
    
    for col in head.find_all('th'):
        col = (col.text).rstrip('\n')
        cols.append(col)

    for row in table.find('tbody').find_all('tr'):
        datas = row.find_all('td')
        datas = [ele.text.strip() for ele in datas]
        dataframe.append([data for data in datas])

    return pd.DataFrame(dataframe, columns = cols[1:])

def scrape_team_page(year, header = True):
    url = 'https://www.pro-football-reference.com/years/{}/index.htm'.format(year)
    def_url = 'https://www.pro-football-reference.com/years/{}/opp.htm'.format(year)
    headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'}
    res = requests.get(url, headers = headers)
    def_res = requests.get(def_url, headers = headers)
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", res.text), 'html.parser')
    def_soup = BeautifulSoup(comm.sub("", def_res.text), 'html.parser')

    team_table_ids = ['AFC', 'NFC', 'team_stats', 'passing', 'rushing', 'returns', 'kicking', 'team_scoring', 'team_conversions', 'drives']
    def_table_ids = ['team_stats', 'advanced_defense', 'passing', 'rushing', 'returns', 'kicking', 'team_scoring', 'team_conversions', 'drives']

    team_df_dict = {}
    for table_id in team_table_ids:
        team_df_dict[table_id] = pd.DataFrame()
    def_df_dict = {}
    for table_id in def_df_dict:
        def_df_dict[table_id] = pd.DataFrame()

    for table_id in team_table_ids:
        print('offensive ', table_id, '...')
        tables = soup.findAll('table', id = table_id)
        data_rows = tables[0].findAll('tr')
        game_data = [[td.getText() for td in data_rows[i].findAll(['th','td'])]
            for i in range(len(data_rows))]

        team_df_dict[table_id] = pd.DataFrame(game_data)

        if table_id in ['drives', 'team_conversions', 'kicking', 'returns', 'team_stats']:
            team_df_dict[table_id].columns = team_df_dict[table_id].iloc[1,:]
            team_df_dict[table_id] = team_df_dict[table_id][2:]
        else:
            team_df_dict[table_id].columns = team_df_dict[table_id].iloc[0,:]
            team_df_dict[table_id] = team_df_dict[table_id][1:]        
        
        team_df_dict[table_id]['Year'] = year
        
        team_df_dict[table_id] = team_df_dict[table_id].set_index('Tm')
        try: 
            for unwanted_name in ['League Total', 'Avg Team', 'Avg Tm/G']:
                team_df_dict[table_id] = team_df_dict[table_id].drop(unwanted_name, axis = 0)
        except Exception:
            pass
        
        if table_id in ['AFC', 'NFC']:
            for unwanted_name in [' {} East'.format(table_id), ' {} West'.format(table_id), ' {} North'.format(table_id), ' {} South'.format(table_id)]:
                    team_df_dict[table_id] = team_df_dict[table_id].drop(unwanted_name, axis = 0)

        team_df_dict[table_id] = team_df_dict[table_id].reset_index()
        
    for table_id in def_table_ids:
        print('defensive ', table_id, '...')
        if year < 2018 and table_id in ['advanced_defense']:
            game_data = pd.DataFrame()
        else:
            tables = def_soup.findAll('table', id = table_id)
            data_rows = tables[0].findAll('tr')
            game_data = [[td.getText() for td in data_rows[i].findAll(['th','td'])]
                for i in range(len(data_rows))]

        def_df_dict[table_id] = pd.DataFrame(game_data)

        if table_id in ['team_stats', 'returns','kicking', 'team_conversions', 'drives', ]:
            def_df_dict[table_id].columns = def_df_dict[table_id].iloc[1,:]
            def_df_dict[table_id] = def_df_dict[table_id][2:]
        elif table_id in ['advanced_defense', 'passing', 'rushing', 'team_scoring']:
            if year < 2018 and table_id in ['advanced_defense']:
                pass
            else: 
                def_df_dict[table_id].columns = def_df_dict[table_id].iloc[0,:]
                def_df_dict[table_id] = def_df_dict[table_id][1:]

        if year < 2018 and table_id in ['advanced_defense']:
                pass
        else: 
            def_df_dict[table_id] = def_df_dict[table_id].set_index('Tm')
            try: 
                for unwanted_name in ['League Total', 'Avg Team', 'Avg Tm/G']:
                    def_df_dict[table_id] = def_df_dict[table_id].drop(unwanted_name, axis = 0)
            except Exception:
                pass

            def_df_dict[table_id] = def_df_dict[table_id].reset_index()
   
    return team_df_dict, def_df_dict

def scrape_team_DVOA(year):
    eff_url = 'https://www.footballoutsiders.com/stats/nfl/team-efficiency/{}'.format(year)
    off_url = 'https://www.footballoutsiders.com/stats/nfl/team-offense/{}'.format(year)
    def_url = 'https://www.footballoutsiders.com/stats/nfl/team-defense/{}'.format(year)
    headers = {
        'authority': 'www.footballoutsiders.com',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.footballoutsiders.com/',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '__stripe_mid=744923fb-ff1f-40a8-a532-478ce0dd382ff1a4cf; __stripe_sid=e93e5df6-af32-4f38-a37d-e8c6180da33e1e0c83; SSESS6e74c02779aec58cd6cdef0fc4a0b09b=n3QPfAPcqzvbLZokvaIwJC8Jnt77ERtU7ZpNZC%2CkVJC%2CP1KP; activityCheck=1',
    }
    urls = [eff_url, off_url, def_url]
    file_names = ['DVOA_team', 'DVOA_off', 'DVOA_def']
    for url, file_name in zip(urls, file_names):
        req = requests.get(url, headers = headers)
        soup = BeautifulSoup(req.content, 'html5lib')
        table = soup.findAll('table')[0]
        data_rows = table.findAll('tr')
        game_data = [[td.get_text() for td in data_rows[i].findAll(['th','td'])]
            for i in range(len(data_rows))]
        df = pd.DataFrame(game_data)
        print(df)
        temp_cols = df.iloc[0]
        """
        if file_name in ['DVOA_off']:
            cols_drop = [1,4,6,8,10,12,14,16,18,20]
        elif file_name in ['DVOA_def']:
            cols_drop = [1,4,6,8,10,12,14,16,18,20]
        elif file_name in ['DVOA_team']:
            cols_drop = [1,3,5,7,9,11,13,15,17,19,23]

        print(df)
        df = df.drop(columns = cols_drop,)# axis = 1, inplace = True)
        print(df)
        df.columns = temp_cols
        df = df.drop(0, axis = 0)
        df['Team'] = df['Team'].str.rstrip('\n')
        df['Year'] = year
        print(df)
        """
        #df.to_csv(r'data/DVOA/{}.csv'.format(file_name))
