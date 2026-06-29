# src/extract_nba_api.py
import os
import pandas as pd
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from src.transform import merge_api_games, create_matchKey, add_matchKey, transform_api_playerLogs, transform_api_teamLogs

# Import nba_api
from nba_api.stats.endpoints import (
    LeagueGameFinder,
    PlayerGameLog,
    PlayerDashboardByYearOverYear,
    CommonAllPlayers,
    LeagueDashTeamStats,          
    TeamGameLogs,                 
    TeamDashboardByGeneralSplits, 
    LeagueLeaders             
)
from nba_api.stats.static import players, teams

load_dotenv()

logger = logging.getLogger(__name__)

#Get current season
def get_current_season():
    """Get the current NBA season string"""
    year = datetime.now().year
    # If before October, use previous season
    if datetime.now().month < 10:
        return f"{year-1}-{str(year)[-2:]}"
    return f"{year}-{str(year+1)[-2:]}"

#extraacting games from api for schema
def extract_api_games_for_stg(season=None):
    """
    Extract games from API and pivot from team-level to game-level.
    Returns records ready for stg_games insertion.
    """
    if season is None:
        season = get_current_season()
    
    logger.info(f"Fetching games for season {season}...")
    
    # Get all games for the season
    try:
        game_finder = LeagueGameFinder(
            season_nullable=season,
            league_id_nullable='00'  # NBA
        )

        # print(game_finder)
        
        df = game_finder.get_data_frames()[0]
        
        logger.info(f"Raw API returned {len(df)} rows")
        logger.info(f"Raw rows: {len(df)}")
        logger.info(df.columns.tolist())

        if df.empty:
            logger.warning(f"No games found for season {season}")
            return []
        
        merged = merge_api_games(df)
        logger.info(f"Merged rows: {len(merged)}")
        logger.info(merged.head())

        merged['season'] = season
        
        #creating new matchkey for apis
        merged['matchKey'] = merged.apply(lambda row: create_matchKey(row['gameDate'], row['homeTeam'], row['awayTeam']), axis =1)
        
        #take pd and convert it to dictionary
        records = merged.to_dict('records')
        # logger.info(f"Pivoted to {len(records)} games for stg_games")
        
        return records
    except Exception:
        logger.exception("Error extracting API games")
        raise


#finding player by id
def find_player_id(player_name: str):
    """Find player ID by name"""
    player_list = players.find_players_by_full_name(player_name)
    if player_list:
        return player_list[0]['id']
    return None


#extracting game logs for each player
def extract_player_game_logs(player_id: str, season=None):
    """
    Extract game logs for a specific player.
    Useful for player prop analysis.
    """
    if season is None:
        season = get_current_season()
    
    logger.info(f"Fetching game logs for player {player_id}...")
    try:
        player_log = PlayerGameLog(
            player_id=player_id,
            season=season
        )
    
        
        df = player_log.get_data_frames()[0]
        # logger.info(f"Found {len(df)} games for player")
        
        return df
    except Exception as e:
        return []

# def extract_player_advanced_stats(player_id: str):
#     """
#     Extract advanced metrics for a player.
#     Includes PER, TS%, Usage %, etc.
#     """
#     logger.info(f"Fetching advanced stats for player {player_id}...")
    
#     dashboard = PlayerDashboardByYearOverYear(
#         player_id=player_id
#     )
    
#     # Get all available DataFrames from every season
#     dataframes = dashboard.get_data_frames()
#     dataframes1 = dashboard.get_data_frames()[0]
#     # print(dataframes)
#     # print(dataframes1)
    
#     # The first DataFrame usually contains the overall stats
#     if dataframes:
#         df = dataframes[0]
#         logger.info(f"Found advanced stats for player")
#         return df.to_dict('records')
    
#     return []


def extract_targeted_player_data(player_names_or_ids, season=None):
    """
    Fetch game logs for specific players.
    
    Args:
        player_names_or_ids: List of player names (str) or IDs (int)
        season: Season string (e.g., '2024-25')
    """
    if season is None:
        season = get_current_season()

    all_player_logs = []
    
    # 1. Convert names to IDs if needed
    player_ids = []
    for item in player_names_or_ids:
        if isinstance(item, str):
            # It's a name, find the ID
            found = find_player_id(item)
            if found:
                player_ids.append(found)
            else:
                logger.warning(f"Player '{item}' not found")
        else:
            # It's already an ID
            player_ids.append(item)
    # print(player_ids)
    
    logger.info(f"Fetching data for {len(player_ids)} players")
    
    # 2. Fetch logs for each player
    for player_id in player_ids:
        try:
            # Get player logs for each player
            player_info = extract_player_game_logs(player_id)
            # print(player_info)
            player_name = players.find_player_by_id(player_id)
            if player_name:
            #and 'full_name' in player_info:
                player_name = player_name['full_name'] 
            # if player_info else f"ID {player_id}"
            else:
                player_name = f"ID {player_id}"
        
            
            logger.info(f"Fetching logs for {player_name}...")
            
            df = extract_player_game_logs(player_id, season)
            # print(df)
            if not df.empty and player_id == player_ids[0]:
                logger.info(f"DEBUG: Columns in player logs: {df.columns.tolist()}")
                logger.info(f"DEBUG: First row: {df.iloc[0].to_dict() if not df.empty else 'empty'}")
            
            if "Player_ID" not in df.columns:
                df["Player_ID"] = player_id
            if not df.empty:
                df['player_name'] = player_name
                all_player_logs.append(df)
            
            time.sleep(0.3)  # Rate limiting
            
        except Exception as e:
            logger.warning(f"Error fetching player {player_id}: {e}")
    
   # 3. Combine
    if all_player_logs:
        combined = pd.concat(all_player_logs, ignore_index=True)
        logger.info(f"Fetched {len(combined)} player-game records for {len(player_ids)} players")
        return combined
    else:
        logger.warning("No player data fetched")
        return pd.DataFrame()

#TEAM API DATA

def find_team_id(team_name: str):
    """Find team ID by name"""
    team_list = teams.find_teams_by_full_name(team_name)
    if team_list:
        return team_list[0]['id']
    return None

def extract_team_game_logs(team_id=None, season=None):
    """
    Extract game-level team stats from API.
    Returns transformed records ready for stg_teamStats.
    """
    if season is None:
        season = get_current_season()
    
    logger.info(f"Fetching team game logs for {season}...")
    logger.info(f"Fetching team game logs for team {team_id}...")
    try: 
        team_log = TeamGameLogs(
            team_id_nullable=str(team_id),
            season_nullable=season,
            league_id_nullable='00'
        )

        df = team_log.get_data_frames()[0]
        logger.info(f"Found {len(df)} team game records")

        return df
    except Exception as e:
        logger.error(f"Error fetching team {team_id}: {e}")

        return pd.DataFrame()

def extract_targeted_team_data(team_names_or_ids, season=None):
    """
    Fetch game logs for specific teams.
    
    Args:
        team_names_or_ids: List of team names (str) or IDs (int)
        season: Season string (e.g., '2024-25')
    """
    if season is None:
        season = get_current_season()

    all_team_logs = []
    
    # Convert names to IDs if needed
    team_ids = []
    for item in team_names_or_ids:
        if isinstance(item, str):
            found = find_team_id(item)
            if found:
                team_ids.append(found)
            else:
                logger.warning(f"Team '{item}' not found")
        else:
            team_ids.append(item)
    
    logger.info(f"Fetching data for {len(team_ids)} teams")
    
    # Fetch logs for each team
    all_teams = teams.get_teams()
    team_id_to_name = {team['id']: team['full_name'] for team in all_teams}
    for team_id in team_ids:
        try:
            # team_name = teams.find_team_by_id(team_id)
            team_name = team_id_to_name.get(team_id, f"ID {team_id}")

            # if team_name:
            #     team_name= team_name['full_name']
            # else:
            #     team_name = f"ID {team_id}"
            
            logger.info(f"Fetching logs for {team_name}...")
            df = extract_team_game_logs(team_id, season )
            # print(df.columns.tolist())
            
            if not df.empty:
                df['team_id'] = team_id
                df['team_name'] = team_name
                all_team_logs.append(df)
            
            time.sleep(0.3)
            
        except Exception as e:
            logger.warning(f"Error fetching team {team_id}: {e}")
    
    # Combine
    if all_team_logs:
        combined = pd.concat(all_team_logs, ignore_index=True)
        logger.info(f"Fetched {len(combined)} team-game records")
        return combined
    else:
        logger.warning("No team data fetched")
        return pd.DataFrame()
    


def extract_nba_api_data(season=None, include_player_stats=False, players_list=None, include_team_stats=False, teams_list=None):
    """
    Main extraction function with player stats option.
    
    Args:
        season: Season string
        include_player_stats: Whether to include player data
        players_list: List of player names or IDs (if None and include_player_stats=True, fetch all)
    """

     # ✅ ADD DEBUGGING
    logger.info(f"DEBUG: include_player_stats={include_player_stats}, players_list={players_list}")
    logger.info(f"DEBUG: include_team_stats={include_team_stats}, teams_list={teams_list}")
    

    if season is None:
        season = get_current_season()

    result = {
        'season': season,
        'games': [],
        'player_logs': [],
        'team_logs': []
    }
    
    # 1. Get games 
    extraction_start = time.perf_counter()
    games = extract_api_games_for_stg(season)
    extraction_end = time.perf_counter()
    print(f"API Extraction: {extraction_end-extraction_start:.2f}s")
    if games:
        logger.info(f"First game record: {games[0]}")
    else:
        logger.warning("No games returned from extract_api_games_for_stg()")

    result['games'] = games
    transformation_start = time.perf_counter()

    # 2. Get player stats (only if requested)
    if include_player_stats and players_list:
            # Fetch specific players game logs
        player_data = extract_targeted_player_data(players_list, season)
       
        
        # Convert to records
        if not player_data.empty:
            player_logs = player_data.to_dict('records')

            missing = sum(1 for log in player_logs if not log.get("matchKey"))
            logger.info(f"Player logs missing matchKey BEFORE add_matchKey: {missing}/{len(player_logs)}")

            
            player_logs = add_matchKey(player_logs, games)
            # logger.info(f"DEBUG: player_logs has {len(player_logs)} records after matchKey")

            missing = sum(1 for log in player_logs if not log.get("matchKey"))
            logger.info(f"Player logs missing matchKey AFTER add_matchKey: {missing}/{len(player_logs)}")


            # player_logs = [log for log in player_logs if log.get('matchKey')]
            # logger.info(f"DEBUG: player_logs has {len(player_logs)} records after filtering")
            result['player_logs'] = transform_api_playerLogs(player_logs)

            logger.info(f"Fetched {len(result['player_logs'])} player records")

        else:
            logger.warning("No player data fetched")
    else:
        if not players_list:
            logger.warning("No players specified for extraction")
        elif not include_player_stats:
            logger.info("Player stats not requested")
    
    if include_team_stats and teams_list:
        logger.info("Extracting team stats...")
        team_data = extract_targeted_team_data(teams_list, season)
        
        if not team_data.empty:
            team_logs = team_data.to_dict('records')
            team_logs = add_matchKey(team_logs, games)  # Need to create this
            team_logs = [log for log in team_logs if log.get('matchKey')]
            result['team_logs'] = transform_api_teamLogs(team_logs)

            logger.info(f"Extracted {len(result['team_logs'])} team records")
        else:
            logger.warning("No team data fetched")
    else:
        if include_team_stats and not teams_list:
            logger.warning("No teams specified for extraction")
    transformation_end = time.perf_counter()
    print(f"API Transformation/Validation Runtime: {transformation_end - transformation_start:.2f}s")



    return result




