import logging    
import pandas as pd
from config.config import PostgresConfig
from src.database import get_connection, insert_stg_games, insert_stg_playerStats, insert_stg_teamStats, insert_stg_bettingLines
from src.extract_csv import extract_games, extract_player_stats, extract_team_stats, extract_betting_lines
from src.extract_api import extract_nba_api_data
from src.transform import create_matchKey, clean_fill_numeric_col, clean_player_stats, clean_team_stats, clean_betting_lines
import time
logger = logging.getLogger(__name__)

def load_csv_data():
    logger.info("Loading CSV Data")

    conn = get_connection()

    try: 
        extraction_start = time.perf_counter()
        game_records = extract_games(PostgresConfig.GAMES_CSV)
        player_records = extract_player_stats(PostgresConfig.PLAYER_STATS_CSV)
        team_records = extract_team_stats(PostgresConfig.TEAM_STATS_CSV)
        betting_records = extract_betting_lines(PostgresConfig.BETTING_CSV)
        extraction_end = time.perf_counter()
        print(f"CSV Extraction: {extraction_end-extraction_start:.2f}s")

        game_df = pd.DataFrame(game_records)
        game_records = game_df.to_dict('records')

        transformation_start = time.perf_counter()
        player_df = pd.DataFrame(player_records)
        clean_player_stats(player_df)
        player_records = player_df.to_dict('records')
        team_df = pd.DataFrame(team_records)
        clean_team_stats(team_df)
        team_records = team_df.to_dict('records')
        betting_df = pd.DataFrame(betting_records)
        clean_betting_lines(betting_df)
        betting_records = betting_df.to_dict('records')

        transformation_end = time.perf_counter()
        print(f"CSV Transformation and Validation Time: {transformation_end-transformation_start:.2f}s")

        insertion_start = time.perf_counter()
        insert_stg_games(conn, game_records)
        insert_stg_playerStats(conn, player_records)
        insert_stg_teamStats(conn, team_records)
        insert_stg_bettingLines(conn, betting_records)
        insertion_end = time.perf_counter()
        print(f"CSV Insertion Time:  {insertion_end - insertion_start:.2f}s")

    except Exception as e:
        logger.error(f"Error loading CSV Data")
        raise
    finally:
        conn.close()

def load_api_data(season=None, players=None, teams=None):
    logger.info("Loading API Data")
    logger.info(f"load_api_data called with: season={season}, players={players}, teams={teams}")

    conn = get_connection()
    try:

         
        extraction_start = time.perf_counter()
        data = extract_nba_api_data(
            season=season,
            include_player_stats=True if players else False,
            players_list=players,
            include_team_stats=True if teams else False,
            teams_list=teams
        )

        logger.info(f"Extracted: {len(data.get('games', []))} games, "
                f"{len(data.get('player_logs', []))} player logs, "
                f"{len(data.get('team_logs', []))} team logs")
        insertion_start =  time.perf_counter()
        
        if data['games']:
            insert_stg_games(conn, data['games'])
            logger.info(f"✅ Loaded {len(data['games'])} API games")
        
        if data.get('player_logs'):
            insert_stg_playerStats(conn, data['player_logs'])
            logger.info(f"✅ Loaded {len(data['player_logs'])} player records")
        else:
            logger.warning("No player logs to insert")

        
        if data.get('team_logs'):
            insert_stg_teamStats(conn, data['team_logs'])
            logger.info(f"✅ Loaded {len(data['team_logs'])} team records")
        else:
            logger.warning("No team logs to insert")

    except Exception as e:
        logger.error(f"Error loading API Data {e}")
        raise
    finally:
        insertion_end = time.perf_counter()
        print(f"API Insertion Time: {insertion_end-insertion_start:.2f}s")
        conn.close()


            