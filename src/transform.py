import pandas as pd
import logging

logger = logging.getLogger(__name__)

nba_teams = {
        "ATL": "Atlanta Hawks",
        "BKN": "Brooklyn Nets",
        "BOS": "Boston Celtics",
        "CHA": "Charlotte Hornets",
        "CHI": "Chicago Bulls",
        "CLE": "Cleveland Cavaliers",
        "DAL": "Dallas Mavericks",
        "DEN": "Denver Nuggets",
        "DET": "Detroit Pistons",
        "GSW": "Golden State Warriors",
        "HOU": "Houston Rockets",
        "IND": "Indiana Pacers",
        "LAC": "Los Angeles Clippers",
        "LAL": "Los Angeles Lakers",
        "MEM": "Memphis Grizzlies",
        "MIA": "Miami Heat",
        "MIL": "Milwaukee Bucks",
        "MIN": "Minnesota Timberwolves",
        "NOP": "New Orleans Pelicans",
        "NYK": "New York Knicks",
        "OKC": "Oklahoma City Thunder",
        "ORL": "Orlando Magic",
        "PHI": "Philadelphia 76ers",
        "PHX": "Phoenix Suns",
        "POR": "Portland Trail Blazers",
        "SAC": "Sacramento Kings",
        "SAS": "San Antonio Spurs",
        "TOR": "Toronto Raptors",
        "UTA": "Utah Jazz",
        "WAS": "Washington Wizards"
    }


def create_matchKey(game_date, home_team, away_team):
    date = str(game_date).split('T')[0].replace('-', '')
    home = str(home_team)[:3].upper()
    away = str(away_team)[:3].upper()
    return f"{date}_{home}_{away}"

def build_gameLookup(games):
    logger.info(f"First game record: {games[0]}")
    lookup={}

    for game in games:
        game_id = game.get("gameId") or game.get("GAME_ID") or game.get("Game_ID") or game.get("game_id")
    
        if game_id is None:
            continue
        
        lookup[int(game_id)] = {
            'matchKey': game.get("matchKey"),
            "gameDate": game.get("gameDate")
        }

    first_key = next(iter(lookup))
    logger.info(lookup[first_key])
    logger.info(f"Lookup size: {len(lookup)}")
    logger.info(f"First 5 lookup keys: {list(lookup.keys())[:5]}")

    return lookup

def convert_type_toInt(df):
  
    for col in df.columns:
        if col.endswith("Id"):
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    


def clean_fill_numeric_col(df, columns):
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    

def clean_player_stats(df):
    numeric_cols = ['points', 'rebounds', 'assists', 'steals', 'blocks', 'minutes', 'turnovers']
    clean_fill_numeric_col(df, numeric_cols)

    for col in numeric_cols:
            df[col] = df[col].astype(int)
   

def clean_team_stats(df):
    numeric_cols = ['points', 'rebounds', 'assists', 'steals', 'blocks', 'minutes', 'turnovers']
    clean_fill_numeric_col(df, numeric_cols)

    for col in numeric_cols:
            df[col] = df[col].astype(int)
   

def clean_betting_lines(df):
    
    df['homeMoneyLine'] = pd.to_numeric(df['homeMoneyLine'], errors='coerce').fillna(0).astype(int)
    df['awayMoneyLine'] = pd.to_numeric(df['awayMoneyLine'], errors='coerce').fillna(0).astype(int)
    df['homeDecimalOdds'] = pd.to_numeric(df['homeDecimalOdds'], errors='coerce').fillna(0)
    df['awayDecimalOdds'] = pd.to_numeric(df['awayDecimalOdds'], errors='coerce').fillna(0)
   

    #FIX NEGATIVES
    both_neg = (df['homeMoneyLine'] < 0) & (df['awayMoneyLine'] < 0)
    if both_neg.any():
        #finding who should be underdog, lower decimal odds = fav, higher decimal odds = under
        mask_home = both_neg & (df['homeDecimalOdds'] > df['awayDecimalOdds'])
        mask_away = both_neg & (df['awayDecimalOdds'] > df['homeDecimalOdds'])

        df.loc[mask_home, 'homeMoneyLine'] = round((df.loc[mask_home, 'homeDecimalOdds']-1)*100).astype(int)
        
        df.loc[mask_away, 'awayMoneyLine'] = round((df.loc[mask_away, 'awayDecimalOdds']-1)*100).astype(int)
    

    MAX_ODDS = 2000
    MIN_ODDS = -2000

    df['homeMoneyLine']= df['homeMoneyLine'].clip(MIN_ODDS, MAX_ODDS)
    df['awayMoneyLine']= df['awayMoneyLine'].clip(MIN_ODDS, MAX_ODDS)
    df['homeDecimalOdds']= df['homeDecimalOdds'].clip(1.01, 100.0)
    df['awayDecimalOdds']= df['awayDecimalOdds'].clip(1.01, 100.0)

    

def merge_api_games(df):
    df['is_home'] = df['MATCHUP'].str.contains('vs.')
    
    # Split home and away
    home_df = df[df['is_home'] == True].copy()
    away_df = df[df['is_home'] == False].copy()
    
    # Rename columns for merging
    home_df = home_df.rename(columns={
        'GAME_ID': 'gameId',
        'GAME_DATE': 'gameDate',
        'TEAM_NAME': 'homeTeam',
        'PTS': 'homeScore'
    })
    
    away_df = away_df.rename(columns={
        'GAME_ID': 'gameId',
        'TEAM_NAME': 'awayTeam',
        'PTS': 'awayScore'
    })
    
    # # Merge on gameId
    merged = pd.merge(
        home_df[['gameId', 'gameDate', 'homeTeam', 'homeScore']],
        away_df[['gameId', 'awayTeam', 'awayScore']],
        on='gameId',
        how='inner'
    )

    merged = merged.drop_duplicates(subset=['gameId'])
    # # Add season
    merged['season'] = df['SEASON_ID'].iloc[0] if 'SEASON_ID' in df.columns else None
    # Convert gameId to integer (remove leading zeros)
    merged['gameId'] = merged['gameId'].astype(int)
   
    
    return merged

def add_matchKey(logs, games):
    if not logs or not games:
        return logs

    game_lookup = build_gameLookup(games)
    logger.info(f"First player log: {logs[0]}")
    for log in logs:
        game_id = (
            log.get("gameId")
            or log.get("GAME_ID")
            or log.get("Game_ID")
        )

        if game_id is None:
            continue

        # logger.info(f"Looking for game_id: {game_id}")
        # logger.info(f"Lookup contains key? {int(game_id) in game_lookup}")
        game = game_lookup.get(int(game_id))

        if not game:
            logger.warning(f"No game found for game_id={game_id}")
        else:
            log["matchKey"] = game["matchKey"]

            if not log.get("gameDate"):
                log["gameDate"] = game["gameDate"]

    return logs


def transform_api_playerLogs(playerLogs):
    if not playerLogs:
        return []
    
    if isinstance(playerLogs, list):
        df = pd.DataFrame(playerLogs)
    else:
        df = playerLogs

    
    logger.info(f"DEBUG: transform_api_playerLogs - columns: {df.columns.tolist()}")
    #mapping api schema to database schema
    column_mapping = {
        'Player_ID': 'playerId',
        'GAME_ID': 'gameId',
        'game_id': 'gameId',
        'GAME_DATE': 'gameDate',
        'Player_Name': 'playerName',
        'player_name': 'playerName',
        'PLAYER_NAME': 'playerName',
        'PTS': 'points',
        'AST': 'assists',
        'REB': 'rebounds',
        'BLK': 'blocks',
        'STL': 'steals',
        'MIN': 'minutes',
        'TOV': 'turnovers'
    }
        
    logger.info(f"DEBUG: Is 'Game_ID' in columns? {'Game_ID' in df.columns}")


    df = df.rename(columns={k:v for k,v in column_mapping.items() if k in df.columns})
    df = df.loc[:, ~df.columns.duplicated()]
    if 'gameId' in df.columns:
        logger.info(f"DEBUG: gameId values (first 5): {df['gameId'].head(5).tolist()}")
        logger.info(f"DEBUG: gameId dtype: {df['gameId'].dtype}")
    else:
        logger.warning("DEBUG: 'gameId' NOT FOUND after rename!")
        # ✅ Try to manually rename
        if 'Game_ID' in df.columns:
            df['gameId'] = df['Game_ID']
            logger.info("DEBUG: Manually created gameId from Game_ID")

     # ✅ DEBUG: Check if gameId exists
    logger.info(f"DEBUG: After rename - columns: {df.columns.tolist()}")
    logger.info(f"DEBUG: gameId values: {df['gameId'].head(5).tolist() if 'gameId' in df.columns else 'NOT FOUND'}")

    #converting gameId to int
    # print(df.columns.tolist())

    # print(df.columns[df.columns.duplicated()])
    convert_type_toInt(df)

    #filling in missing columns
    player_cols = ['gameId', 'matchKey', 'gameDate', 'playerId', 'playerName', 'team', 'points', 'assists', 'rebounds', 'steals', 'blocks', 'turnovers', 'minutes']

    for col in player_cols:
        if col not in df.columns:
            if col in ['points', 'assists', 'rebounds', 'steals', 'blocks', 'turnovers', 'minutes']:
                df[col] = 0
            elif col == 'team':
                if 'MATCHUP' in df.columns:
                    df["team"] = df["MATCHUP"].str.split().str[0].map(nba_teams)
                else:
                    df['team'] = 'Unknown'
            else:
                df[col] = None

    clean_player_stats(df)

    logger.info(df[['gameId','playerId','matchKey']].head(10))
    logger.info(df['matchKey'].isna().sum())
    logger.info(len(df))    
    #Removing rows
    df = df[df['gameId'].notna() & df['playerId'].notna()]
    df = df[df['matchKey'].notna()]

    #Removing duplicates
    df = df.drop_duplicates(subset=['gameId', 'playerId'])
    df = df.drop_duplicates(subset=['matchKey', 'playerId'])

    records = df[player_cols].to_dict('records')

    return records

def transform_api_teamLogs(teamLogs):
    """
    Transform API team game logs to match stg_teamStats schema.
    
    Args:
        teamLogs: DataFrame from TeamGameLogs API
    
    Returns:
        List of dicts ready for stg_teamStats insertion
    """
    if not teamLogs:
        return []
    
    if isinstance(teamLogs, list):
        df = pd.DataFrame(teamLogs)
    else:
        df = teamLogs.copy()
    
    # Map API columns to database schema
    column_mapping = {
        'TEAM_ID': 'teamId',
        'team_id': 'teamId',
        'Team_Id': "teamId",
        'Game_ID': 'gameId', 
        'GAME_ID': 'gameId',
        'game_id': 'gameId',
        'game_date': 'gameDate',
        'GAME_DATE': 'gameDate',
        'TEAM_NAME': 'teamName',
        'Team_Name': 'teamName',
        'team_name': 'teamName',
        'PTS': 'points',
        'AST': 'assists',
        'REB': 'rebounds',
        'BLK': 'blocks',
        'STL': 'steals',
        'MIN': 'minutes',
        'TOV': 'turnovers',
        
       
    }

    logger.info(f"DEBUG: Is 'Game_ID' in columns? {'Game_ID' in df.columns}")

    
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    df = df.loc[:, ~df.columns.duplicated()]
    # print(df.columns.tolist())
    # print(df.columns[df.columns.duplicated()])
    convert_type_toInt(df)


   
    # Fill missing columns
    team_cols = ['gameId', 'teamId', 'teamName', 'gameDate', 'matchKey', 'points', 'assists', 'rebounds', 'steals', 'blocks', 'turnovers', 'minutes']
    
    for col in team_cols:
        if col not in df.columns:
            if col in ['points', 'assists', 'rebounds', 'steals', 'blocks', 'turnovers', 'minutes']:
                df[col] = 0
            else:
                df[col] = None
    
    clean_team_stats(df)

    # Remove rows with missing key data
    df = df[df['gameId'].notna() & df['teamId'].notna()]
    
    if 'matchKey' in df.columns:
        df = df[df['matchKey'].notna()]
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['gameId', 'teamId'])
    df = df.drop_duplicates(subset=['matchKey', 'teamId'])
    
    # Return records
  
    records = df[team_cols].to_dict('records')
    
    return records