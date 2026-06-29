# src/main.py - CLEANED UP VERSION

import argparse
import logging
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import PostgresConfig
from src.database import get_connection, init_db, drop_db
from src.load import load_csv_data, load_api_data
from src.extract_api import get_current_season

LOG_DIR = PostgresConfig.LOGS_DIR
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "ingestion.log")

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def init_database(reset=False):
    """Initialize or reset the database."""
    logger.info("=" * 60)
    logger.info("DATABASE INITIALIZATION")
    logger.info("=" * 60)
    
    conn = get_connection()
    try:
        if reset:
            logger.info("Dropping existing tables...")
            drop_db(conn)
        
        logger.info("Creating tables...")
        init_db(conn)
        logger.info("✅ Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()


def run_pipeline(args):
    """Run the full ingestion pipeline."""
    logger.info("=" * 60)
    logger.info("NBA DATA INGESTION PIPELINE STARTED")
    logger.info("=" * 60)
    
    # 1. Initialize database (if requested)
    if args.init or args.reset:
        init_database(reset=args.reset)
    
    # 2. Load CSV data (if requested)
    if args.source in ['csv', 'all']:
        logger.info("STEP 1: LOADING CSV DATA")
        logger.info("=" * 60)
        load_csv_data()
    
    # 3. Load API data (if requested)
    if args.source in ['api', 'all']:
        logger.info("STEP 2: LOADING API DATA")
        logger.info("=" * 60)
        
        season = args.season or PostgresConfig.DEFAULT_SEASON
        players = args.players if args.players else []
        teams = args.teams if args.teams else [] 
        
        load_api_data(season=season, players=players, teams=teams)
    
    logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)


def main():
    """Main entry point with argument parsing for the pipeline."""
    
    parser = argparse.ArgumentParser(
        description='NBA Data Ingestion Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main --source all --init
  python -m src.main --source csv
  python -m src.main --source api --season 2024-25
  python -m src.main --source api --players "LeBron James" "Stephen Curry"
        """
    )
    
    parser.add_argument(
        '--source',
        choices=['csv', 'api', 'all'],
        default='all',
        help='Data source to ingest'
    )
    
    parser.add_argument(
        '--season',
        type=str,
        default=None,
        help='Season to fetch (e.g., 2024-25)'
    )
    
    parser.add_argument(
        '--players',
        nargs='+',
        default=None,
        help='List of player names'
    )
    
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize database tables'
    )

    parser.add_argument(
        '--teams',
        nargs='+',
        default=None,
        help='List of team names'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset database (drops and recreates tables)'
    )
    
    args = parser.parse_args()
    
    try:
        pipeline_start = time.perf_counter()
        run_pipeline(args)
        pipeline_end = time.perf_counter()

        print(f"Pipeline Runtime: {pipeline_end - pipeline_start:.2f}s")
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()