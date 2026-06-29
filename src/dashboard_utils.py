# # src/dashboard_utils.py
# """
# Dashboard Utilities - All SQL queries and data fetching
# """
# import streamlit as st
# import pandas as pd
# from src.database import get_connection


# @st.cache_data(ttl=300)
# def get_table_counts():
#     """Get row counts for all tables"""
#     conn = get_connection()
#     tables = ['stg_games', 'stg_playerStats', 'stg_teamStats', 'stg_bettingLines']
#     results = {}
    
#     for table in tables:
#         try:
#             query = f"SELECT COUNT(*) FROM {table}"
#             cursor = conn.cursor()
#             cursor.execute(query)
#             results[table] = cursor.fetchone()[0]
#         except Exception as e:
#             print(f"Error counting {table}: {e}")
#             results[table] = 0
    
#     conn.close()
#     return results

# @st.cache_data(ttl=300)
# def get_table_schemas():
#     """Get column info for all tables"""
#     conn = get_connection()
#     cursor = conn.cursor()
    
#     tables = ['stg_games', 'stg_playerStats', 'stg_teamStats', 'stg_bettingLines']
#     schemas = {}
    
#     for table in tables:
#         try:
#             cursor.execute(f"""
#                 SELECT 
#                     column_name, 
#                     data_type,
#                     is_nullable
#                 FROM information_schema.columns 
#                 WHERE table_name = '{table}'
#                 AND table_schema = 'public'
#                 ORDER BY ordinal_position
#             """)
#             rows = cursor.fetchall()
            
#             schemas[table] = {
#                 'columns': rows,
#                 'row_count': 0
#             }
            
#         except Exception as e:
#             print(f"Error getting schema for {table}: {e}")
#             schemas[table] = {'columns': [], 'row_count': 0}
    
#     conn.close()
#     return schemas

# @st.cache_data(ttl=300)
# def get_data_quality_metrics():
#     """Calculate data quality metrics"""
#     conn = get_connection()
#     metrics = {}
    
#     try:
#         # Missing home scores
#         query = "SELECT COUNT(*) FROM stg_games WHERE homeScore IS NULL"
#         metrics['missing_home_score'] = pd.read_sql(query, conn).iloc[0,0]
#     except Exception:
#         metrics['missing_home_score'] = 0
    
#     try:
#         # Missing away scores
#         query = "SELECT COUNT(*) FROM stg_games WHERE awayScore IS NULL"
#         metrics['missing_away_score'] = pd.read_sql(query, conn).iloc[0,0]
#     except Exception:
#         metrics['missing_away_score'] = 0
    
#     try:
#         # Players with 0 minutes
#         query = "SELECT COUNT(*) FROM stg_playerStats WHERE minutes = 0 AND points > 0"
#         metrics['players_0_min'] = pd.read_sql(query, conn).iloc[0,0]
#     except Exception:
#         metrics['players_0_min'] = 0
    
#     try:
#         # Foreign key matches (playerStats)
#         query = """
#             SELECT COUNT(*) 
#             FROM stg_playerStats p
#             LEFT JOIN stg_games g ON p.gameId = g.gameId
#             WHERE g.gameId IS NULL
#         """
#         metrics['orphan_player_stats'] = pd.read_sql(query, conn).iloc[0,0]
#     except Exception:
#         metrics['orphan_player_stats'] = 0
    
#     try:
#         # Foreign key matches (teamStats)
#         query = """
#             SELECT COUNT(*) 
#             FROM stg_teamStats t
#             LEFT JOIN stg_games g ON t.gameId = g.gameId
#             WHERE g.gameId IS NULL
#         """
#         metrics['orphan_team_stats'] = pd.read_sql(query, conn).iloc[0,0]
#     except Exception:
#         metrics['orphan_team_stats'] = 0
    
#     conn.close()
#     return metrics


# @st.cache_data(ttl=300)
# def get_season_trends():
#     """Get scoring trends by season"""
#     conn = get_connection()
#     try:
#         query = """
#             SELECT 
#                 season,
#                 COUNT(*) as games,
#                 ROUND(AVG(homeScore), 1) as avg_home_score,
#                 ROUND(AVG(awayScore), 1) as avg_away_score,
#                 ROUND(AVG(totalScore), 1) as avg_total
#             FROM stg_games
#             WHERE season IS NOT NULL
#             GROUP BY season
#             ORDER BY season
#         """
#         df = pd.read_sql(query, conn)
#     except Exception as e:
#         print(f"Error getting season trends: {e}")
#         df = pd.DataFrame()
#     conn.close()
#     return df


# @st.cache_data(ttl=300)
# def get_top_teams(limit=10):
#     """Get top scoring teams"""
#     conn = get_connection()
#     try:
#         query = f"""
#             SELECT 
#                 homeTeam as team,
#                 COUNT(*) as games,
#                 ROUND(AVG(homeScore), 1) as avg_points
#             FROM stg_games
#             WHERE homeTeam IS NOT NULL
#             GROUP BY homeTeam
#             ORDER BY avg_points DESC
#             LIMIT {limit}
#         """
#         df = pd.read_sql(query, conn)
#     except Exception as e:
#         print(f"Error getting top teams: {e}")
#         df = pd.DataFrame()
#     conn.close()
#     return df


# @st.cache_data(ttl=300)
# def get_table_data(table_name, limit=100):
#     """Get raw table data for explorer"""
#     conn = get_connection()
#     try:
#         query = f"SELECT * FROM {table_name} LIMIT {limit}"
#         df = pd.read_sql(query, conn)
#     except Exception as e:
#         print(f"Error getting table data for {table_name}: {e}")
#         df = pd.DataFrame()
#     conn.close()
#     return df


# @st.cache_data(ttl=300)
# def get_player_points_distribution():
#     """Get distribution of player points"""
#     conn = get_connection()
#     try:
#         query = """
#             SELECT 
#                 CASE 
#                     WHEN points BETWEEN 0 AND 9 THEN '0-9'
#                     WHEN points BETWEEN 10 AND 19 THEN '10-19'
#                     WHEN points BETWEEN 20 AND 29 THEN '20-29'
#                     WHEN points BETWEEN 30 AND 39 THEN '30-39'
#                     WHEN points >= 40 THEN '40+'
#                     ELSE 'Unknown'
#                 END as point_range,
#                 COUNT(*) as count
#             FROM stg_playerStats
#             WHERE points IS NOT NULL
#             GROUP BY point_range
#             ORDER BY point_range
#         """
#         df = pd.read_sql(query, conn)
#     except Exception as e:
#         print(f"Error getting player points distribution: {e}")
#         df = pd.DataFrame()
#     conn.close()
#     return df


# @st.cache_data(ttl=300)
# def get_pipeline_summary():
#     """Get overall pipeline summary"""
#     counts = get_table_counts()
#     metrics = get_data_quality_metrics()
    
#     total_rows = sum(counts.values())
#     total_issues = (
#         metrics.get('missing_home_score', 0) +
#         metrics.get('missing_away_score', 0) +
#         metrics.get('orphan_player_stats', 0) +
#         metrics.get('orphan_team_stats', 0)+
#         metrics.get('players_0_min', 0)
#     )
    
#     if total_rows > 0:
#         quality_score = round((1 - (total_issues / total_rows)) * 100, 2)
#     else:
#         quality_score = 0.0

#     return {
#         'total_rows': total_rows,
#         'quality_score': quality_score,
#         'issues': total_issues,
#         'issue_breakdown': metrics
#     }


# def get_tables_with_counts():
#     """Get list of tables with their counts"""
#     counts = get_table_counts()
#     return [{'name': name.replace('stg_', ''), 'count': count} for name, count in counts.items() if count > 0]

# src/dashboard_utils.py
"""
Dashboard Utilities - All SQL queries and data fetching
"""
import streamlit as st
import pandas as pd
from src.database import get_connection

import subprocess
from pathlib import Path


@st.cache_data(ttl=300)
def get_table_counts():
    """Get row counts for all tables"""
    conn = get_connection()
    tables = ['stg_games', 'stg_playerStats', 'stg_teamStats', 'stg_bettingLines']
    results = {}
    
    for table in tables:
        try:
            query = f"SELECT COUNT(*) FROM {table}"
            cursor = conn.cursor()
            cursor.execute(query)
            results[table] = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting {table}: {e}")
            results[table] = 0
    
    conn.close()
    return results


@st.cache_data(ttl=300)
def get_table_schemas():
    """Get column info for all tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    tables = ['stg_games', 'stg_playerStats', 'stg_teamStats', 'stg_bettingLines']
    schemas = {}
    
    for table in tables:
        try:
            cursor.execute(f"""
                SELECT 
                    column_name, 
                    data_type,
                    is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            rows = cursor.fetchall()
            
            schemas[table] = {
                'columns': rows,
                'row_count': 0
            }
            
        except Exception as e:
            print(f"Error getting schema for {table}: {e}")
            schemas[table] = {'columns': [], 'row_count': 0}
    
    conn.close()
    return schemas


@st.cache_data(ttl=300)
def get_data_quality_metrics():
    """Calculate data quality metrics"""
    conn = get_connection()
    metrics = {}
    
    try:
        query = "SELECT COUNT(*) FROM stg_games WHERE homeScore IS NULL"
        metrics['missing_home_score'] = pd.read_sql(query, conn).iloc[0,0]
    except Exception:
        metrics['missing_home_score'] = 0
    
    try:
        query = "SELECT COUNT(*) FROM stg_games WHERE awayScore IS NULL"
        metrics['missing_away_score'] = pd.read_sql(query, conn).iloc[0,0]
    except Exception:
        metrics['missing_away_score'] = 0
    
    try:
        query = "SELECT COUNT(*) FROM stg_playerStats WHERE minutes = 0 AND points > 0"
        metrics['players_0_min'] = pd.read_sql(query, conn).iloc[0,0]
    except Exception:
        metrics['players_0_min'] = 0
    
    try:
        query = """
            SELECT COUNT(*) 
            FROM stg_playerStats p
            LEFT JOIN stg_games g ON p.gameId = g.gameId
            WHERE g.gameId IS NULL
        """
        metrics['orphan_player_stats'] = pd.read_sql(query, conn).iloc[0,0]
    except Exception:
        metrics['orphan_player_stats'] = 0
    
    try:
        query = """
            SELECT COUNT(*) 
            FROM stg_teamStats t
            LEFT JOIN stg_games g ON t.gameId = g.gameId
            WHERE g.gameId IS NULL
        """
        metrics['orphan_team_stats'] = pd.read_sql(query, conn).iloc[0,0]
    except Exception:
        metrics['orphan_team_stats'] = 0
    
    conn.close()
    return metrics


@st.cache_data(ttl=300)
def get_season_trends():
    """Get scoring trends by season"""
    conn = get_connection()
    try:
        query = """
            SELECT 
                season,
                COUNT(*) as games,
                ROUND(AVG(homeScore), 1) as avg_home_score,
                ROUND(AVG(awayScore), 1) as avg_away_score,
                ROUND(AVG(totalScore), 1) as avg_total
            FROM stg_games
            WHERE season IS NOT NULL
            GROUP BY season
            ORDER BY season
        """
        df = pd.read_sql(query, conn)
    except Exception as e:
        print(f"Error getting season trends: {e}")
        df = pd.DataFrame()
    conn.close()
    return df


@st.cache_data(ttl=300)
def get_top_teams(limit=10):
    """Get top scoring teams"""
    conn = get_connection()
    try:
        query = f"""
            SELECT 
                homeTeam as team,
                COUNT(*) as games,
                ROUND(AVG(homeScore), 1) as avg_points
            FROM stg_games
            WHERE homeTeam IS NOT NULL
            GROUP BY homeTeam
            ORDER BY avg_points DESC
            LIMIT {limit}
        """
        df = pd.read_sql(query, conn)
    except Exception as e:
        print(f"Error getting top teams: {e}")
        df = pd.DataFrame()
    conn.close()
    return df


@st.cache_data(ttl=300)
def get_table_data(table_name, limit=100):
    """Get raw table data for explorer"""
    conn = get_connection()
    try:
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql(query, conn)
    except Exception as e:
        print(f"Error getting table data for {table_name}: {e}")
        df = pd.DataFrame()
    conn.close()
    return df


@st.cache_data(ttl=300)
def get_player_points_distribution():
    """Get distribution of player points"""
    conn = get_connection()
    try:
        query = """
            SELECT 
                CASE 
                    WHEN points BETWEEN 0 AND 9 THEN '0-9'
                    WHEN points BETWEEN 10 AND 19 THEN '10-19'
                    WHEN points BETWEEN 20 AND 29 THEN '20-29'
                    WHEN points BETWEEN 30 AND 39 THEN '30-39'
                    WHEN points >= 40 THEN '40+'
                    ELSE 'Unknown'
                END as point_range,
                COUNT(*) as count
            FROM stg_playerStats
            WHERE points IS NOT NULL
            GROUP BY point_range
            ORDER BY point_range
        """
        df = pd.read_sql(query, conn)
    except Exception as e:
        print(f"Error getting player points distribution: {e}")
        df = pd.DataFrame()
    conn.close()
    return df


@st.cache_data(ttl=300)
def get_pipeline_summary():
    """Get overall pipeline summary with accurate quality score"""
    counts = get_table_counts()
    metrics = get_data_quality_metrics()
    
    total_rows = sum(counts.values())
    
    # Include ALL issues in the total
    total_issues = (
        metrics.get('missing_home_score', 0) +
        metrics.get('missing_away_score', 0) +
        metrics.get('orphan_player_stats', 0) +
        metrics.get('orphan_team_stats', 0) +
        metrics.get('players_0_min', 0)
    )
    
    # Calculate quality score
    if total_rows > 0:
        quality_score = round((1 - (total_issues / total_rows)) * 100, 2)
    else:
        quality_score = 0.0
    
    return {
        'total_rows': total_rows,
        'quality_score': quality_score,
        'issues': total_issues,
        'issue_breakdown': metrics
    }


def get_tables_with_counts():
    """Get list of tables with their counts"""
    counts = get_table_counts()
    return [{'name': name.replace('stg_', ''), 'count': count} for name, count in counts.items() if count > 0]


def get_log_file_path():
    """Get the path to the ingestion log file"""
    from config.config import PostgresConfig
    log_path = Path(PostgresConfig.LOGS_DIR) / "ingestion.log"
    return log_path

def load_logs_tail(limit=100):
    """
    Load logs using tail -n to get most recent entries
    This is much more efficient than reading the entire file
    """
    log_path = get_log_file_path()
    
    if not log_path.exists():
        return pd.DataFrame(), "Log file not found"
    
    try:
        # Use subprocess to run tail -n for efficiency
        result = subprocess.run(
            ['tail', '-n', str(limit), str(log_path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return pd.DataFrame(), f"Error reading log file: {result.stderr}"
        
        lines = result.stdout.splitlines()
        
        parsed = []
        for line in lines:
            parsed_line = parse_log_line(line)
            if parsed_line:
                parsed.append(parsed_line)
        
        if not parsed:
            return pd.DataFrame(), "No parsed log entries found"
        
        df = pd.DataFrame(parsed)
        return df, None
        
    except Exception as e:
        return pd.DataFrame(), f"Error reading log file: {e}"

def load_logs_fallback(limit=100):
    """
    Fallback method using Python file reading
    Used if subprocess fails
    """
    log_path = get_log_file_path()
    
    if not log_path.exists():
        return pd.DataFrame(), "Log file not found"
    
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
        
        # Get last N lines
        lines_to_load = lines[-limit:] if limit else lines
        
        parsed = []
        for line in lines_to_load:
            parsed_line = parse_log_line(line)
            if parsed_line:
                parsed.append(parsed_line)
        
        if not parsed:
            return pd.DataFrame(), "No parsed log entries found"
        
        df = pd.DataFrame(parsed)
        return df, None
        
    except Exception as e:
        return pd.DataFrame(), f"Error reading log file: {e}"

def load_logs(limit=100):
    """
    Load logs - tries tail first, falls back to Python reading
    """
    # Try tail first (more efficient)
    df, error = load_logs_tail(limit)
    
    # If tail fails, use fallback
    if error and "not found" not in error:
        df, error = load_logs_fallback(limit)
    
    return df, error


