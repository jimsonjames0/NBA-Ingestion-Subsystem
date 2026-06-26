# src/dashboard_utils.py
"""
Dashboard Utilities - All SQL queries and data fetching
"""
import streamlit as st
import pandas as pd
from src.database import get_connection


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
        # Missing home scores
        query = "SELECT COUNT(*) FROM stg_games WHERE homeScore IS NULL"
        metrics['missing_home_score'] = pd.read_sql(query, conn).iloc[0,0]
    except Exception:
        metrics['missing_home_score'] = 0
    
    try:
        # Missing away scores
        query = "SELECT COUNT(*) FROM stg_games WHERE awayScore IS NULL"
        metrics['missing_away_score'] = pd.read_sql(query, conn).iloc[0,0]
    except Exception:
        metrics['missing_away_score'] = 0
    
    try:
        # Players with 0 minutes
        query = "SELECT COUNT(*) FROM stg_playerStats WHERE minutes = 0 AND points > 0"
        metrics['players_0_min'] = pd.read_sql(query, conn).iloc[0,0]
    except Exception:
        metrics['players_0_min'] = 0
    
    try:
        # Foreign key matches (playerStats)
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
        # Foreign key matches (teamStats)
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
    """Get overall pipeline summary"""
    counts = get_table_counts()
    metrics = get_data_quality_metrics()
    
    total_rows = sum(counts.values())
    total_issues = (
        metrics.get('missing_home_score', 0) +
        metrics.get('missing_away_score', 0) +
        metrics.get('orphan_player_stats', 0) +
        metrics.get('orphan_team_stats', 0)+
        metrics.get('players_0_min', 0)
    )
    
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