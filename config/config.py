#config/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class PostgresConfig:
    DATA_DIR = '/mnt/c/Users/jimso/MyCode/Revature/nba_data_ingestion_pipeline/data'
    LOGS_DIR = '/mnt/c/Users/jimso/MyCode/Revature/nba_data_ingestion_pipeline/logs'

    GAMES_CSV = f"{DATA_DIR}/games_index.csv"
    PLAYER_STATS_CSV = f"{DATA_DIR}/player_boxscores.csv"
    TEAM_STATS_CSV = f"{DATA_DIR}/team_boxscores.csv"
    BETTING_CSV=f"{DATA_DIR}/game_odds.csv"

    DEFAULT_SEASON = "2024-25"
    
    def __init__(self):
        self._host = os.getenv("POSTGRES_HOST")
        self._port = os.getenv("POSTGRES_PORT")
        self._db = os.getenv("POSTGRES_DB")
        self._user = os.getenv("POSTGRES_USER")
        self._password = os.getenv("POSTGRES_PASSWORD")
    
    def __str__(self):
        return (
            f"host={self._host} port={self._port} dbname={self._db} "
            f"user={self._user} password={self._password}"
        )
    def as_dict(self):
        return {
            "host": self._host,
            "port": self._port,
            "database": self._db,
            "user": self._user,
            "password": self._password
        }
    