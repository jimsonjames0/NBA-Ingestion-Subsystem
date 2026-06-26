# src/test_extract.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from config.config import PostgresConfig
from src.extract_csv import extract_games, extract_player_stats, extract_team_stats, extract_betting_lines
from src.database import get_connection, insert_stg_games, insert_stg_playerStats, insert_stg_teamStats, insert_stg_bettingLines

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_games():
    """Test games extraction and insertion"""
    logger.info("="*60)
    logger.info("TEST 1: GAMES")
    logger.info("="*60)
    
    try:
        logger.info("Extracting games...")
        games = extract_games(PostgresConfig.GAMES_CSV)
        logger.info(f"✅ Extracted {len(games)} games")
        
        if games:
            logger.info(f"Sample game: {games[0]}")
        
        logger.info("Inserting games into database...")
        conn = get_connection()
        insert_stg_games(conn, games)
        conn.close()
        logger.info("✅ Games test PASSED!")
        return True
    except Exception as e:
        logger.error(f"❌ Games test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_player_stats():
    """Test player stats extraction and insertion"""
    logger.info("="*60)
    logger.info("TEST 2: PLAYER STATS")
    logger.info("="*60)
    
    try:
        logger.info("Extracting player stats...")
        players = extract_player_stats(PostgresConfig.PLAYER_STATS_CSV)
        logger.info(f"✅ Extracted {len(players)} player stats")
        
        if players:
            logger.info(f"Sample player stat: {players[0]}")
        
        logger.info("Inserting player stats into database...")
        conn = get_connection()
        insert_stg_playerStats(conn, players)
        conn.close()
        logger.info("✅ Player stats test PASSED!")
        return True
    except Exception as e:
        logger.error(f"❌ Player stats test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_team_stats():
    """Test team stats extraction and insertion"""
    logger.info("="*60)
    logger.info("TEST 3: TEAM STATS")
    logger.info("="*60)
    
    try:
        logger.info("Extracting team stats...")
        teams = extract_team_stats(PostgresConfig.TEAM_STATS_CSV)
        logger.info(f"✅ Extracted {len(teams)} team stats")
        
        if teams:
            logger.info(f"Sample team stat: {teams[0]}")
        
        logger.info("Inserting team stats into database...")
        conn = get_connection()
        insert_stg_teamStats(conn, teams)
        conn.close()
        logger.info("✅ Team stats test PASSED!")
        return True
    except Exception as e:
        logger.error(f"❌ Team stats test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_betting_lines():
    """Test betting lines extraction and insertion"""
    logger.info("="*60)
    logger.info("TEST 4: BETTING LINES")
    logger.info("="*60)
    
    try:
        logger.info("Extracting betting lines...")
        bets = extract_betting_lines(PostgresConfig.BETTING_CSV)
        logger.info(f"✅ Extracted {len(bets)} betting lines")
        
        if bets:
            logger.info(f"Sample bet: {bets[0]}")
        
        logger.info("Inserting betting lines into database...")
        conn = get_connection()
        insert_stg_bettingLines(conn, bets)
        conn.close()
        logger.info("✅ Betting lines test PASSED!")
        return True
    except Exception as e:
        logger.error(f"❌ Betting lines test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🔍 TESTING CSV EXTRACTION ONE BY ONE\n")
    
    # Run each test individually
    tests = [
        ("GAMES", test_games),
        ("PLAYER STATS", test_player_stats),
        ("TEAM STATS", test_team_stats),
        ("BETTING LINES", test_betting_lines),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        print("\n" + "-"*60 + "\n")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")