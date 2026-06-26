#src/database.py
import psycopg2, os
from psycopg2.extras import RealDictCursor

from config.config import PostgresConfig
from dotenv import load_dotenv
load_dotenv()

# print("Host:", os.getenv("POSTGRES_HOST"))
# print("Port:", os.getenv("POSTGRES_PORT"))
# print("DB:", os.getenv("POSTGRES_DB"))
# print("User:", os.getenv("POSTGRES_USER"))
# print("Password length:", len(os.getenv("POSTGRES_PASSWORD", "")))  # Don't print actual password

def get_connection(config: PostgresConfig = None):
    config = config or PostgresConfig()
    return psycopg2.connect(**config.as_dict())

# def test_connection():
#     try:
#         conn = get_connection()
#         print("Successfully connected!")
#         conn.close()
#     except Exception as e:
#         print(f"Connection Failed: {e}")

def init_db(connection):
    with connection.cursor() as cursor:

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stg_games(
                gameId BIGINT PRIMARY KEY, 
                matchKey VARCHAR(50) UNIQUE,
                gameDate DATE,
                season VARCHAR(50), 
                homeTeam VARCHAR(50),
                awayTeam VARCHAR(50),
                homeScore INTEGER,
                awayScore INTEGER,
                totalScore INTEGER GENERATED ALWAYS AS (homeScore + awayScore) STORED,
                ingestionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stg_bettingLines(
                gameId BIGINT PRIMARY KEY REFERENCES stg_games(gameId), 
                matchKey VARCHAR(50) UNIQUE REFERENCES stg_games(matchKey),
                gameDate DATE,
                homeMoneyLine INTEGER,
                awayMoneyLine INTEGER,
                homeDecimalOdds DECIMAL(4,2),
                awayDecimalOdds DECIMAL(4,2),
                spread DECIMAL(4,1),
                overUnder DECIMAL(4,1), 
                ingestionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stg_playerStats(
                playerStatId BIGSERIAL PRIMARY KEY, 
                matchKey VARCHAR(50) REFERENCES stg_games(matchKey),
                gameId BIGINT REFERENCES stg_games(gameId),
                gameDate DATE,
                playerId BIGINT, 
                playerName VARCHAR(50),
                team VARCHAR(50),
                points INTEGER,
                rebounds INTEGER,
                assists INTEGER,
                steals INTEGER,
                blocks INTEGER,
                minutes INTEGER,
                turnovers INTEGER,
                ingestionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(gameId, playerId),
                UNIQUE(matchKey, playerId)
                )
                """
            )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stg_teamStats(
                teamStatId BIGSERIAL PRIMARY KEY, 
                matchKey VARCHAR(50) REFERENCES stg_games(matchKey),
                gameId BIGINT REFERENCES stg_games(gameId),
                gameDate DATE,
                teamId BIGINT, 
                teamName VARCHAR(50),
                points INTEGER,
                rebounds INTEGER,
                assists INTEGER,
                steals INTEGER,
                blocks INTEGER,
                minutes INTEGER,
                turnovers INTEGER,
                ingestionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(gameId, teamId),
                UNIQUE(matchKey, teamId)
                )
                """
            )
        # cursor.execute(
        #     """
        #     CREATE TABLE IF NOT EXISTS stg_rejects(
        #         rejectId BIGSERIAL PRIMARY KEY, 
        #         sourceName VARCHAR(50) NOT NULL,
        #         gameId BIGINT REFERENCES stg_games(gameId),
        #         gameDate DATE,
        #         teamId BIGINT, 
        #         teamName VARCHAR(50),
        #         points INTEGER,
        #         rebounds INTEGER,
        #         assists INTEGER,
        #         steals INTEGER,
        #         blocks INTEGER,
        #         minutes INTEGER,
        #         turnovers INTEGER,
        #         ingestionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        #         UNIQUE(gameId, teamId),
        #         UNIQUE(matchKey, teamId)
        #         )
        #         """
        #     )
        connection.commit()


def drop_db(connection):
    with connection.cursor() as cursor:
        # Drop in reverse order of dependencies
        cursor.execute("DROP TABLE IF EXISTS stg_playerStats CASCADE")
        cursor.execute("DROP TABLE IF EXISTS stg_teamStats CASCADE")
        cursor.execute("DROP TABLE IF EXISTS stg_bettingLines CASCADE")
        cursor.execute("DROP TABLE IF EXISTS stg_games CASCADE")
        connection.commit()


def insert_stg_games(connection, rows):
    """
            CREATE TABLE IF NOT EXISTS stg_games(
                gameId BIGINT PRIMARY KEY, 
                matchKey VARCHAR(50) UNIQUE,
                gameDate DATE,
                season VARCHAR(50), 
                homeTeam VARCHAR(50),
                awayTeam VARCHAR(50),
                homeScore INTEGER,
                awayScore INTEGER,
                totalScore INTEGER GENERATED ALWAYS AS (homeScore + awayScore) STORED,
                ingestionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
    """
    query = """
            INSERT INTO stg_games (
                gameId, matchKey, gameDate, season, homeTeam, awayTeam, homeScore, awayScore
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (matchKey) DO NOTHING
            """

    with connection.cursor() as cursor:
            cursor.executemany(
                query, 
                [
                    (
                        row["gameId"],
                        row["matchKey"],
                        row["gameDate"],
                        row["season"],
                        row["homeTeam"],
                        row["awayTeam"],
                        row["homeScore"],
                        row["awayScore"],
                        
                    )
                    for row in rows
                ],
            )
            connection.commit()

            print(f"Successfully loaded in data")

def insert_stg_playerStats(connection, rows):
    with connection.cursor() as cursor:
        cursor.execute("SELECT gameId FROM stg_games")
        valid_game_ids = {row[0] for row in cursor.fetchall()}
        
        filtered_rows = [row for row in rows if row['gameId'] in valid_game_ids]

    query = """
            INSERT INTO stg_playerStats (
            matchKey, gameId, gameDate, playerId, playerName, team, points, rebounds, assists, steals, blocks, minutes, turnovers)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (matchKey, playerId) DO NOTHING
            """

    with connection.cursor() as cursor:
        cursor.executemany(
                query, 
                [
                    (
                        row["matchKey"],
                        row["gameId"],
                        row["gameDate"],
                        row["playerId"],
                        row["playerName"],
                        row["team"],
                        row.get("points",0),
                        row.get("rebounds",0),
                        row.get("assists",0),
                        row.get("steals",0),
                        row.get("blocks",0),
                        row.get("minutes",0),
                        row.get("turnovers",0),
                        
                    )
                    for row in filtered_rows
                ],
            )
        connection.commit()

def insert_stg_teamStats(connection, rows):
    with connection.cursor() as cursor:
        cursor.execute("SELECT gameId FROM stg_games")
        valid_game_ids = {row[0] for row in cursor.fetchall()}
        
        filtered_rows = [row for row in rows if row['gameId'] in valid_game_ids]


    query = """
            INSERT INTO stg_teamStats (
            matchKey, gameId, gameDate, teamId, teamName, points, rebounds, assists, steals, blocks, minutes, turnovers)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (matchKey, teamId) DO NOTHING

        """

    with connection.cursor() as cursor:
        cursor.executemany(
                query, 
                [
                    (
                        row["matchKey"],
                        row["gameId"],
                        row["gameDate"],
                        row["teamId"],
                        row["teamName"],
                        row.get("points",0),
                        row.get("rebounds",0),
                        row.get("assists",0),
                        row.get("steals",0),
                        row.get("blocks",0),
                        row.get("minutes",0),
                        row.get("turnovers",0),
                        
                    )
                    for row in filtered_rows
                ],
            )
        connection.commit()

def insert_stg_bettingLines(connection, rows):
    """
            CREATE TABLE IF NOT EXISTS stg_bettingLines(
                gameId BIGINT PRIMARY KEY REFERENCES stg_games(gameId), 
                matchKey VARCHAR(50) UNIQUE REFERENCES stg_games(matchKey),
                gameDate DATE,
                homeMoneyLine INTEGER,
                awayMoneyLine INTEGER,
                homeDecimalOdds DECIMAL(4,2),
                awayDecimalOdds DECIMAL(4,2),
                spread DECIMAL(4,1),
                overUnder DECIMAL(4,1), 
                ingestionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT matchKey FROM stg_games")
        existing_games = {row[0] for row in cursor.fetchall()}

        filtered_rows = [row for row in rows if row['matchKey'] in existing_games]
    
    query = """
            INSERT INTO stg_bettingLines (
            gameId, matchKey, gameDate, homeMoneyLine, awayMoneyLine, homeDecimalOdds, awayDecimalOdds)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (matchKey) DO NOTHING
        """

    with connection.cursor() as cursor:
        cursor.executemany(
                query, 
                [
                    (
                        row["gameId"],
                        row["matchKey"],
                        row["gameDate"],
                        row["homeMoneyLine"],
                        row["awayMoneyLine"],
                        row["homeDecimalOdds"],
                        row["awayDecimalOdds"],
                    )
                    for row in filtered_rows
                ],
            )
        connection.commit()  
           

if __name__ == "__main__":
    
    conn = get_connection()
    drop_db(conn)
    init_db(conn)
    conn.close()
