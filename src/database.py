#src/database.py
import psycopg2, os
from psycopg2.extras import RealDictCursor
import json
import json
from datetime import date, datetime


from config.config import PostgresConfig
from dotenv import load_dotenv
load_dotenv()

# print("Host:", os.getenv("POSTGRES_HOST"))
# print("Port:", os.getenv("POSTGRES_PORT"))
# print("DB:", os.getenv("POSTGRES_DB"))
# print("User:", os.getenv("POSTGRES_USER"))
# print("Password length:", len(os.getenv("POSTGRES_PASSWORD", "")))  # Don't print actual password

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles date and datetime objects."""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):  # For pandas Series/DataFrame
            return obj.to_dict()
        return super().default(obj)
    

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
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stg_rejects(
                rejectId BIGSERIAL PRIMARY KEY, 
                sourceName VARCHAR(50) NOT NULL,
                entityType VARCHAR(50) NOT NULL,
                matchKey VARCHAR(50),
                gameId BIGINT,
                playerId BIGINT,
                teamId BIGINT,
                reason VARCHAR(100) NOT NULL,
                rawPayload JSONB NOT NULL,
                rejectedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            )
            
        
        # Create indexes for faster queries
        cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rejects_source 
                ON stg_rejects(sourceName)
            """
            )
        cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rejects_entity 
                ON stg_rejects(entityType)
            """
            )
        cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rejects_rejected_at 
                ON stg_rejects(rejectedAt)
            """ 
            )
        cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rejects_match_key 
                ON stg_rejects(matchKey)
            """
            )
        connection.commit()


def drop_db(connection):
    with connection.cursor() as cursor:
        # Drop in reverse order of dependencies
        cursor.execute("DROP TABLE IF EXISTS stg_playerStats CASCADE")
        cursor.execute("DROP TABLE IF EXISTS stg_teamStats CASCADE")
        cursor.execute("DROP TABLE IF EXISTS stg_bettingLines CASCADE")
        cursor.execute("DROP TABLE IF EXISTS stg_games CASCADE")
        connection.commit()


def insert_reject(connection, source_name, entity_type, raw_record, reason,
                  match_key=None, game_id=None, player_id=None, team_id=None):
    """
    Insert a rejected record into stg_rejects table.
    """
    # Convert raw_record to JSON with custom encoder
    if isinstance(raw_record, dict):
        try:
            payload = json.dumps(raw_record, cls=CustomJSONEncoder)
        except TypeError:
            # If still fails, convert to string
            payload = str(raw_record)
    else:
        payload = str(raw_record)
    
    query = """
        INSERT INTO stg_rejects (
            sourceName, entityType, matchKey, gameId, playerId, teamId, reason, rawPayload
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                source_name,
                entity_type,
                match_key,
                game_id,
                player_id,
                team_id,
                reason,
                payload
            )
        )
        connection.commit()


def insert_stg_games(connection, rows):
    """Insert games, rejecting duplicates"""
    
    # Check for existing matchKeys
    with connection.cursor() as cursor:
        cursor.execute("SELECT matchKey FROM stg_games")
        existing_matchKeys = {row[0] for row in cursor.fetchall()}
    
    valid_rows = []
    rejected_rows = []
    
    for row in rows:
        if row.get('matchKey') not in existing_matchKeys:
            valid_rows.append(row)
        else:
            rejected_rows.append(row)
    
    # Insert rejected rows into stg_rejects
    if rejected_rows:
        print(f"⚠️ Rejecting {len(rejected_rows)} duplicate games")
        for row in rejected_rows:
            insert_reject(
                connection,
                source_name='csv_games',
                entity_type='game',
                raw_record=row,
                reason=f"Duplicate matchKey: {row.get('matchKey')}",
                match_key=row.get('matchKey'),
                game_id=row.get('gameId')
            )
    
    if not valid_rows:
        print("No valid games to insert")
        return

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
    """Insert player stats, rejecting invalid gameIds"""
    
    # Get valid game IDs
    with connection.cursor() as cursor:
        cursor.execute("SELECT gameId FROM stg_games")
        valid_game_ids = {row[0] for row in cursor.fetchall()}
    
    valid_rows = []
    rejected_rows = []
    
    for row in rows:
        if row.get('gameId') in valid_game_ids:
            valid_rows.append(row)
        else:
            rejected_rows.append(row)
    
    # Insert rejected rows into stg_rejects
    if rejected_rows:
        print(f"⚠️ Rejecting {len(rejected_rows)} player stats with invalid gameId")
        for row in rejected_rows:
            insert_reject(
                connection,
                source_name='csv_player_stats',
                entity_type='player_stats',
                raw_record=row,
                reason=f"gameId {row.get('gameId')} not found in stg_games",
                game_id=row.get('gameId'),
                player_id=row.get('playerId')
            )
    
    if not valid_rows:
        print("No valid player stats to insert")
        return
    
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
    
    valid_rows = []
    rejected_rows = []
    
    for row in rows:
        if row.get('gameId') in valid_game_ids:
            valid_rows.append(row)
        else:
            rejected_rows.append(row)
    
    # Insert rejected rows into stg_rejects
    if rejected_rows:
        print(f"⚠️ Rejecting {len(rejected_rows)} team stats with invalid gameId")
        for row in rejected_rows:
            insert_reject(
                connection,
                source_name='csv_team_stats',
                entity_type='team_stats',
                raw_record=row,
                reason=f"gameId {row.get('gameId')} not found in stg_games",
                game_id=row.get('gameId'),
                team_id=row.get('teamId')
            )
    
    if not valid_rows:
        print("No valid team stats to insert")
        return

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

    with connection.cursor() as cursor:
        cursor.execute("SELECT matchKey FROM stg_games")
        existing_matchKeys = {row[0] for row in cursor.fetchall()}
    
    valid_rows = []
    rejected_rows = []
    
    for row in rows:
        if row.get('matchKey') in existing_matchKeys:
            valid_rows.append(row)
        else:
            rejected_rows.append(row)
    
    # Insert rejected rows into stg_rejects
    if rejected_rows:
        print(f"⚠️ Rejecting {len(rejected_rows)} betting lines with invalid matchKey")
        for row in rejected_rows:
            insert_reject(
                connection,
                source_name='csv_betting_lines',
                entity_type='betting_line',
                raw_record=row,
                reason=f"matchKey {row.get('matchKey')} not found in stg_games",
                match_key=row.get('matchKey'),
                game_id=row.get('gameId')
            )
    
    if not valid_rows:
        print("No valid betting lines to insert")
        return

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
