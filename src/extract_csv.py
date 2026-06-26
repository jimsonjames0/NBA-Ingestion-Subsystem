import pandas as pd
import logging
from src.database import get_connection, insert_stg_games, insert_stg_playerStats, insert_stg_teamStats, insert_stg_bettingLines
from src.transform import create_matchKey, clean_fill_numeric_col, clean_player_stats, clean_team_stats, clean_betting_lines
from config.config import PostgresConfig
logging.basicConfig(
    filename= '/mnt/c/Users/jimso/MyCode/Revature/nba_data_ingestion_pipeline/logs/ingestion.log',
    level=logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

def extract_games(csv_path: str):
    logger.info(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    logger.info(f"Read {len(df)} row from CSV")
    """  gameId INTEGER PRIMARY KEY, 
                gameDate DATE,
                season INTEGER, 
                homeTeam VARCHAR(50),
                awayTeam VARCHAR(50),
                homeScore INTEGER,
                awayScore INTEGER,
                totalScore INTEGER
    """
    games_df = df[['game_id', 'game_date', 'season_year', 'team_name_home', 'team_name_away', 'pts_home', 'pts_away']].copy()
    games_df.columns = ['gameId', 'gameDate', 'season', 'homeTeam', 'awayTeam', 'homeScore', 'awayScore']

    games_df['gameDate'] = pd.to_datetime(games_df['gameDate']).dt.date
    games_df['matchKey'] = games_df.apply(
        lambda row: create_matchKey(row['gameDate'], row['homeTeam'], row['awayTeam']),
        axis=1
    )

    records= games_df.to_dict('records')
    logger.info(f"Prepared {len(records)} games for insertion")

    return records

def extract_player_stats(csv_path: str):
    logger.info(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    logger.info(f"Read {len(df)} row from CSV")


    #getting required columns from games_csv to create matchKey for players tables
    games_df = pd.read_csv(PostgresConfig.GAMES_CSV)
    games_lookup = games_df[['game_id', 'game_date', 'team_name_home', 'team_name_away']].copy()
       #cleaning gameDate
    games_lookup['game_date'] = pd.to_datetime(games_lookup['game_date']).dt.date
    #creating matchkey
    games_lookup['matchKey']= games_lookup.apply(
        lambda row: create_matchKey(row['game_date'], row['team_name_home'], row['team_name_away']),
        axis=1
    )

    #mapping gameId to matchKey and gameDate
    game_id_to_matchKey = dict(zip(games_lookup['game_id'], games_lookup['matchKey']))
    game_id_to_gameDate = dict(zip(games_lookup['game_id'], games_lookup['game_date']))
    valid_gameIds = set(games_lookup['game_id'])

    playerstats_df = df[['game_id', 'player_id', 'player_name', 'team_name', 'pts', 'reb', 'ast', 'stl', 'blk', 'min','tov']].copy()
    playerstats_df.columns = ['gameId', 'playerId', 'playerName', 'team', 'points', 'rebounds', 'assists', 'steals', 'blocks', 'minutes', 'turnovers']


    playerstats_df = playerstats_df[playerstats_df['gameId'].isin(valid_gameIds)]
    
    #error checking numeric columns, converting to int
    # numeric_cols= ['points', 'rebounds', 'assists', 'steals', 'blocks', 'minutes', 'turnovers']
    # for col in numeric_cols:
    #     playerstats_df[col] = pd.to_numeric(playerstats_df[col], errors='coerce').fillna(0)

    # playerstats_df['points'] = playerstats_df['points'].astype(int)
    # playerstats_df['rebounds'] = playerstats_df['rebounds'].astype(int)
    # playerstats_df['assists'] = playerstats_df['assists'].astype(int)
    # playerstats_df['steals'] = playerstats_df['steals'].astype(int)
    # playerstats_df['blocks'] = playerstats_df['blocks'].astype(int)
    # playerstats_df['turnovers'] = playerstats_df['turnovers'].astype(int)
    clean_player_stats(playerstats_df)


    playerstats_df['matchKey'] = playerstats_df['gameId'].map(game_id_to_matchKey)
    playerstats_df['gameDate'] = playerstats_df['gameId'].map(game_id_to_gameDate)

    #dropping all matchKeys that are na
    playerstats_df = playerstats_df[playerstats_df['matchKey'].notna()]

    records= playerstats_df.to_dict('records')
    logger.info(f"Prepared {len(records)} playerStats for insertion")

    return records

def extract_team_stats(csv_path: str):
    logger.info(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    logger.info(f"Read {len(df)} row from CSV")

    games_df = pd.read_csv(PostgresConfig.GAMES_CSV)
    games_lookup = games_df[['game_id', 'game_date', 'team_name_home', 'team_name_away']].copy()
    #Cleaning game_date to create matchKey
    games_lookup['game_date'] = pd.to_datetime(games_lookup['game_date']).dt.date
    games_lookup['matchKey'] = games_lookup.apply(
        lambda row: create_matchKey(row['game_date'], row['team_name_home'], row['team_name_away']),
        axis=1
    )

    game_id_to_matchKey = dict(zip(games_lookup['game_id'], games_lookup['matchKey']))
    game_id_to_gameDate = dict(zip(games_lookup['game_id'], games_lookup['game_date']))
    valid_gameIds = set(games_lookup['game_id'])

    #extracting team stats
    teamstats_df = df[['game_id', 'team_id', 'team_name', 'pts', 'reb', 'ast', 'stl', 'blk', 'min','tov']].copy()
    teamstats_df.columns = ['gameId', 'teamId', 'teamName', 'points', 'rebounds', 'assists', 'steals', 'blocks', 'minutes', 'turnovers']

    
    teamstats_df = teamstats_df[teamstats_df['gameId'].isin(valid_gameIds)]
   

    # numeric_cols= ['points', 'rebounds', 'assists', 'steals', 'blocks', 'minutes', 'turnovers']
    # for col in numeric_cols:
    #     teamstats_df[col] = pd.to_numeric(teamstats_df[col], errors='coerce').fillna(0)

    # teamstats_df['points'] = teamstats_df['points'].astype(int)
    # teamstats_df['rebounds'] = teamstats_df['rebounds'].astype(int)
    # teamstats_df['assists'] = teamstats_df['assists'].astype(int)
    # teamstats_df['steals'] = teamstats_df['steals'].astype(int)
    # teamstats_df['blocks'] = teamstats_df['blocks'].astype(int)
    # teamstats_df['turnovers'] = teamstats_df['turnovers'].astype(int)

    clean_team_stats(teamstats_df)

    teamstats_df['matchKey'] = teamstats_df['gameId'].map(game_id_to_matchKey)
    teamstats_df['gameDate'] = teamstats_df['gameId'].map(game_id_to_gameDate)

    teamstats_df = teamstats_df[teamstats_df['matchKey'].notna()]

    records= teamstats_df.to_dict('records')
    logger.info(f"Prepared {len(records)} teamStats for insertion")

    return records

def extract_betting_lines(csv_path: str):
    logger.info(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    logger.info(f"Read {len(df)} row from CSV")

    #creating matchKeys
    games_df = pd.read_csv(PostgresConfig.GAMES_CSV)
    games_lookup = games_df[['game_id', 'game_date', 'team_name_home', 'team_name_away']].copy()
    games_lookup['matchKey'] = games_lookup.apply(
        lambda row: create_matchKey(row['game_date'], row['team_name_home'], row['team_name_away']),
        axis=1
    )

    #mapping of gameIds to matchKeys
    gameId_to_matchKey = dict(zip(games_lookup['game_id'], games_lookup['matchKey']))
    #valid set of matchKeys
    valid_matchKeys = set(games_lookup['matchKey'])
    valid_gameIds = set(games_lookup['game_id'])



    #filtering by gameIds
    df = df[df['game_id'].isin(valid_gameIds)]

    df = df.groupby('game_id').agg({
        'game_date': 'first',
        'decimal_home': 'mean',
        'decimal_away': 'mean',
        'moneyline_home': 'mean',
        'moneyline_away': 'mean'
        }).reset_index()
    
    bettinglines_df = df[['game_id', 'game_date', 'moneyline_home', 'moneyline_away', 'decimal_home', 'decimal_away']].copy()
    bettinglines_df.columns = ['gameId', 'gameDate', 'homeMoneyLine', 'awayMoneyLine', 'homeDecimalOdds', 'awayDecimalOdds']

    # bettinglines_df['homeMoneyLine'] = pd.to_numeric(bettinglines_df['homeMoneyLine'], errors='coerce').fillna(0).astype(int)
    # bettinglines_df['awayMoneyLine'] = pd.to_numeric(bettinglines_df['awayMoneyLine'], errors='coerce').fillna(0).astype(int)
    # bettinglines_df['homeDecimalOdds'] = pd.to_numeric(bettinglines_df['homeDecimalOdds'], errors='coerce').fillna(0)
    # bettinglines_df['awayDecimalOdds'] = pd.to_numeric(bettinglines_df['awayDecimalOdds'], errors='coerce').fillna(0)
   

    # #FIX NEGATIVES
    # both_neg = (bettinglines_df['homeMoneyLine'] < 0) & (bettinglines_df['awayMoneyLine'] < 0)
    # if both_neg.any():
    #     #finding who should be underdog, lower decimal odds = fav, higher decimal odds = under
    #     mask_home = both_neg & (bettinglines_df['homeDecimalOdds'] > bettinglines_df['awayDecimalOdds'])
    #     mask_away = both_neg & (bettinglines_df['awayDecimalOdds'] > bettinglines_df['homeDecimalOdds'])

    #     bettinglines_df.loc[mask_home, 'homeMoneyLine'] = round((bettinglines_df.loc[mask_home, 'homeDecimalOdds']-1)*100).astype(int)
        
    #     bettinglines_df.loc[mask_away, 'awayMoneyLine'] = round((bettinglines_df.loc[mask_away, 'awayDecimalOdds']-1)*100).astype(int)
    # #CLEAN VALUES

    # MAX_ODDS = 2000
    # MIN_ODDS = -2000

    # bettinglines_df['homeMoneyLine']= bettinglines_df['homeMoneyLine'].clip(MIN_ODDS, MAX_ODDS)
    # bettinglines_df['awayMoneyLine']= bettinglines_df['awayMoneyLine'].clip(MIN_ODDS, MAX_ODDS)

    # bettinglines_df['homeDecimalOdds']= bettinglines_df['homeDecimalOdds'].clip(1.01, 100.0)
    # bettinglines_df['awayDecimalOdds']= bettinglines_df['awayDecimalOdds'].clip(1.01, 100.0)
    clean_betting_lines(bettinglines_df)

    bettinglines_df['matchKey'] = bettinglines_df['gameId'].map(gameId_to_matchKey)
    bettinglines_df = bettinglines_df[bettinglines_df['matchKey'].notna()]

    records= bettinglines_df.to_dict('records')
    logger.info(f"Prepared {len(records)} bettingLines for insertion")

    return records

# if __name__ == '__main__':
#     g_games_path = '/mnt/c/Users/jimso/MyCode/Revature/nba_data_ingestion_pipeline/data/games_index.csv'
#     playerstats_path = '/mnt/c/Users/jimso/MyCode/Revature/nba_data_ingestion_pipeline/data/player_boxscores.csv'
#     teamstats_path = '/mnt/c/Users/jimso/MyCode/Revature/nba_data_ingestion_pipeline/data/team_boxscores.csv'
#     betlines_path = '/mnt/c/Users/jimso/MyCode/Revature/nba_data_ingestion_pipeline/data/game_odds.csv'
#     game_records = extract_games(g_games_path)

#     player_records= extract_player_stats(playerstats_path)

#     team_records = extract_team_stats(teamstats_path)
#     # print(game_records[:10])

#     bet_records = extract_betting_lines(betlines_path, g_games_path)

#     conn = get_connection()
#     insert_stg_games(conn, game_records)
#     insert_stg_playerStats(conn, player_records)  # ← Same connection
#     insert_stg_teamStats(conn, team_records)
#     insert_stg_bettingLines(conn, bet_records)
#     conn.close()

   



