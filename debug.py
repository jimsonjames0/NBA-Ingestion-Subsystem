# debug.py
import psycopg2
from src.database import get_connection

def check_table_quality(conn, table_name):
    """Check data quality for a specific table"""
    print(f"\n{'='*60}")
    print(f"📊 CHECKING: {table_name}")
    print(f"{'='*60}")
    
    cursor = conn.cursor()
    
    # 1. Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    print(f"📈 Total rows: {row_count:,}")
    
    # 2. Get column info
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print(f"\n📋 Columns:")
    for col_name, col_type in columns:
        print(f"   - {col_name}: {col_type}")
    
    # 3. Check for NULLs in key columns
    cursor.execute(f"""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN gameid IS NULL THEN 1 END) as null_gameid
        FROM {table_name}
    """)
    result = cursor.fetchone()
    print(f"\n🔍 NULL check:")
    print(f"   - Null gameId: {result[1]} ({(result[1]/result[0]*100):.2f}%)")
    
    # 4. Get sample data (first 5 rows)
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    sample = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    
    print(f"\n📝 Sample data (first 5 rows):")
    print(f"   Columns: {', '.join(col_names)}")
    for i, row in enumerate(sample, 1):
        # Truncate long values for display
        display_row = []
        for val in row:
            if isinstance(val, str) and len(val) > 50:
                val = val[:50] + "..."
            display_row.append(val)
        print(f"   Row {i}: {tuple(display_row)}")
    
    # 5. Get min/max for numeric columns (avoiding overflow)
    numeric_cols = []
    for col_name, col_type in columns:
        if 'int' in col_type.lower() or 'decimal' in col_type.lower() or 'numeric' in col_type.lower():
            numeric_cols.append(col_name)
    
    if numeric_cols:
        print(f"\n📊 Numeric column stats:")
        for col in numeric_cols[:5]:  # Limit to first 5 numeric cols
            try:
                # Use BIGINT for large numbers
                if col in ['teamid', 'playerid']:
                    cursor.execute(f"""
                        SELECT 
                            MIN({col})::bigint as min_val,
                            MAX({col})::bigint as max_val,
                            COUNT(CASE WHEN {col} IS NULL THEN 1 END) as null_count
                        FROM {table_name}
                        WHERE {col} IS NOT NULL
                    """)
                    stats = cursor.fetchone()
                    print(f"   - {col}:")
                    print(f"       Min: {stats[0]}")
                    print(f"       Max: {stats[1]}")
                    print(f"       Null: {stats[2]}")
                else:
                    cursor.execute(f"""
                        SELECT 
                            MIN({col}) as min_val,
                            MAX({col}) as max_val,
                            AVG({col})::numeric(10,2) as avg_val,
                            COUNT(CASE WHEN {col} IS NULL THEN 1 END) as null_count
                        FROM {table_name}
                        WHERE {col} IS NOT NULL
                    """)
                    stats = cursor.fetchone()
                    print(f"   - {col}:")
                    print(f"       Min: {stats[0]}")
                    print(f"       Max: {stats[1]}")
                    print(f"       Avg: {stats[2]}")
                    print(f"       Null: {stats[3]}")
            except Exception as e:
                print(f"   - {col}: Could not compute stats ({e})")
    
    # 6. Check for duplicates in primary key
    try:
        first_col = col_names[0]
        cursor.execute(f"""
            SELECT COUNT(*) - COUNT(DISTINCT {first_col}) as duplicates
            FROM {table_name}
        """)
        dup_count = cursor.fetchone()[0]
        if dup_count > 0:
            print(f"\n⚠️ Duplicates found: {dup_count:,} duplicate values in {first_col}")
        else:
            print(f"\n✅ No duplicates found in {first_col}")
    except Exception as e:
        print(f"\n⚠️ Could not check duplicates: {e}")

    cursor.close()

def check_moneyline_data(conn):
    """Special check for betting lines (moneyline validation)"""
    print(f"\n{'='*60}")
    print(f"🎯 SPECIAL CHECK: Moneyline Validation")
    print(f"{'='*60}")
    
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'stg_bettinglines'
        )
    """)
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        print("⚠️ stg_bettinglines table doesn't exist yet")
        return
    
    # Check for invalid moneyline pairs
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN homemoneyline < 0 AND awaymoneyline < 0 THEN 1 END) as both_negative,
            COUNT(CASE WHEN homemoneyline > 0 AND awaymoneyline > 0 THEN 1 END) as both_positive,
            COUNT(CASE WHEN homemoneyline = 0 AND awaymoneyline = 0 THEN 1 END) as both_zero,
            COUNT(CASE WHEN homemoneyline = 0 OR awaymoneyline = 0 THEN 1 END) as one_zero
        FROM stg_bettinglines
        WHERE homemoneyline IS NOT NULL AND awaymoneyline IS NOT NULL
    """)
    result = cursor.fetchone()
    
    print(f"\n📊 Moneyline Distribution:")
    print(f"   - Total rows: {result[0]:,}")
    print(f"   - Both negative (both favorites): {result[1]:,} ⚠️")
    print(f"   - Both positive (both underdogs): {result[2]:,} ⚠️")
    print(f"   - Both zero: {result[3]:,}")
    print(f"   - One zero: {result[4]:,}")
    
    # Show sample of problematic rows
    cursor.execute("""
        SELECT gameid, homemoneyline, awaymoneyline, homedecimalodds, awaydecimalodds
        FROM stg_bettinglines
        WHERE (homemoneyline < 0 AND awaymoneyline < 0)
           OR (homemoneyline > 0 AND awaymoneyline > 0)
        LIMIT 10
    """)
    problems = cursor.fetchall()
    if problems:
        print(f"\n⚠️ Sample of problematic moneyline pairs:")
        for row in problems:
            print(f"   Game {row[0]}: Home={row[1]}, Away={row[2]}, DecHome={row[3]}, DecAway={row[4]}")
    
    cursor.close()

def check_player_stats(conn):
    """Special check for player stats"""
    print(f"\n{'='*60}")
    print(f"🏀 SPECIAL CHECK: Player Stats Validation")
    print(f"{'='*60}")
    
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'stg_playerstats'
        )
    """)
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        print("⚠️ stg_playerstats table doesn't exist yet")
        return
    
    # Check for extreme values
    cursor.execute("""
        SELECT 
            MIN(points) as min_pts,
            MAX(points) as max_pts,
            AVG(points)::numeric(10,2) as avg_pts,
            COUNT(CASE WHEN points > 80 THEN 1 END) as over_80,
            COUNT(CASE WHEN minutes > 60 THEN 1 END) as over_60_min
        FROM stg_playerstats
    """)
    result = cursor.fetchone()
    
    print(f"\n📊 Player Stats Distribution:")
    print(f"   - Points - Min: {result[0]}, Max: {result[1]}, Avg: {result[2]}")
    print(f"   - Players with 80+ points: {result[3]:,}")
    print(f"   - Players with 60+ minutes: {result[4]:,}")
    
    # Check for players with 0 minutes but points > 0 (impossible)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM stg_playerstats 
        WHERE minutes = 0 AND points > 0
    """)
    impossible = cursor.fetchone()[0]
    if impossible > 0:
        print(f"\n⚠️ {impossible:,} players have points but 0 minutes (check data)")
    
    # Check for reasonable range
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN points < 0 THEN 1 END) as negative_pts,
            COUNT(CASE WHEN rebounds < 0 THEN 1 END) as negative_reb,
            COUNT(CASE WHEN assists < 0 THEN 1 END) as negative_ast,
            COUNT(CASE WHEN minutes < 0 THEN 1 END) as negative_min
        FROM stg_playerstats
    """)
    negatives = cursor.fetchone()
    if sum(negatives) > 0:
        print(f"\n⚠️ Negative values found:")
        print(f"   - Negative points: {negatives[0]:,}")
        print(f"   - Negative rebounds: {negatives[1]:,}")
        print(f"   - Negative assists: {negatives[2]:,}")
        print(f"   - Negative minutes: {negatives[3]:,}")
    
    cursor.close()

def check_team_stats(conn):
    """Special check for team stats"""
    print(f"\n{'='*60}")
    print(f"🏀 SPECIAL CHECK: Team Stats Validation")
    print(f"{'='*60}")
    
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'stg_teamstats'
        )
    """)
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        print("⚠️ stg_teamstats table doesn't exist yet")
        return
    
    cursor.execute("""
        SELECT 
            MIN(points) as min_pts,
            MAX(points) as max_pts,
            AVG(points)::numeric(10,2) as avg_pts,
            COUNT(CASE WHEN points > 200 THEN 1 END) as over_200,
            COUNT(CASE WHEN points < 0 THEN 1 END) as negative_pts
        FROM stg_teamstats
    """)
    result = cursor.fetchone()
    
    print(f"\n📊 Team Stats Distribution:")
    print(f"   - Points - Min: {result[0]}, Max: {result[1]}, Avg: {result[2]}")
    print(f"   - Teams with 200+ points: {result[3]:,} (should be 0 for NBA)")
    print(f"   - Teams with negative points: {result[4]:,}")
    
    cursor.close()

def check_game_data(conn):
    """Special check for game data"""
    print(f"\n{'='*60}")
    print(f"🏀 SPECIAL CHECK: Game Data Validation")
    print(f"{'='*60}")
    
    cursor = conn.cursor()
    
    # Check for invalid scores
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN homescore < 0 OR awayscore < 0 THEN 1 END) as negative_scores,
            COUNT(CASE WHEN homescore > 200 OR awayscore > 200 THEN 1 END) as high_scores,
            MIN(homescore) as min_home,
            MAX(homescore) as max_home,
            AVG(homescore)::numeric(10,2) as avg_home,
            MIN(awayscore) as min_away,
            MAX(awayscore) as max_away,
            AVG(awayscore)::numeric(10,2) as avg_away
        FROM stg_games
    """)
    result = cursor.fetchone()
    
    print(f"\n📊 Game Scores:")
    print(f"   - Negative scores: {result[0]:,}")
    print(f"   - Scores > 200: {result[1]:,}")
    print(f"   - Home - Min: {result[2]}, Max: {result[3]}, Avg: {result[4]}")
    print(f"   - Away - Min: {result[5]}, Max: {result[6]}, Avg: {result[7]}")
    
    # Check totalScore matches homeScore + awayScore
    cursor.execute("""
        SELECT COUNT(*) 
        FROM stg_games 
        WHERE totalscore != homescore + awayscore
    """)
    mismatch = cursor.fetchone()[0]
    if mismatch > 0:
        print(f"\n⚠️ {mismatch:,} games have incorrect totalScore (should equal home+away)")
    else:
        print(f"\n✅ TotalScore correctly generated from home+away")
    
    # Check season format
    cursor.execute("""
        SELECT DISTINCT season 
        FROM stg_games 
        ORDER BY season 
        LIMIT 10
    """)
    seasons = cursor.fetchall()
    print(f"\n📊 Seasons in database:")
    for season in seasons:
        print(f"   - {season[0]}")
    
    cursor.close()

def run_full_check():
    """Run all data quality checks"""
    conn = get_connection()
    
    print("=" * 60)
    print("🔍 DATA QUALITY CHECK - FULL REPORT")
    print("=" * 60)
    
    # Check each table
    check_table_quality(conn, "stg_games")
    check_table_quality(conn, "stg_playerstats")
    check_table_quality(conn, "stg_teamstats")
    check_table_quality(conn, "stg_bettinglines")
    
    # Run special checks
    check_game_data(conn)
    check_player_stats(conn)
    check_team_stats(conn)
    check_moneyline_data(conn)
    
    conn.close()
    
    print(f"\n{'='*60}")
    print("✅ Data Quality Check Complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    run_full_check()