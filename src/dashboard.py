# # src/dashboard.py
# """
# NBA Data Ingestion Dashboard - Main Entry Point
# """
# import streamlit as st
# import pandas as pd
# from datetime import datetime
# import os
# import sys

# # Add project root to path
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from src.dashboard_utils import *
# from src.database import get_connection

# # ──────────────────────────────────────────────────────────────
# # PAGE CONFIG
# # ──────────────────────────────────────────────────────────────

# st.set_page_config(
#     page_title="NBA Data Ingestion Dashboard",
#     page_icon="🏀",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ──────────────────────────────────────────────────────────────
# # CUSTOM CSS
# # ──────────────────────────────────────────────────────────────

# st.markdown("""
# <style>
#     .metric-card {
#         background-color: #262730;
#         padding: 20px;
#         border-radius: 10px;
#         border: 1px solid #333;
#     }
#     .metric-value {
#         font-size: 2.5rem;
#         font-weight: bold;
#         color: #1f77b4;
#     }
#     .metric-label {
#         font-size: 0.9rem;
#         color: #888;
#     }
#     .status-success {
#         color: #00cc66;
#         font-weight: bold;
#     }
#     .status-failed {
#         color: #ff4444;
#         font-weight: bold;
#     }
#     .pipeline-flow {
#         text-align: center;
#         font-size: 1.1rem;
#         padding: 20px;
#     }
#     .flow-arrow {
#         color: #1f77b4;
#         font-size: 1.5rem;
#     }
#     .sidebar .sidebar-content {
#         background-color: #0e1117;
#     }
#     .stSelectbox label, .stMultiSelect label {
#         color: #fafafa !important;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ──────────────────────────────────────────────────────────────
# # SIDEBAR
# # ──────────────────────────────────────────────────────────────

# with st.sidebar:
#     st.markdown("## 🏀 NBA Pipeline")
#     st.markdown("---")
    
#     # Refresh button
#     if st.button("🔄 Refresh Data"):
#         st.cache_data.clear()
#         st.rerun()
    
#     st.markdown("---")
#     st.markdown("### 📊 Quick Stats")
    
#     # Show live counts in sidebar
#     try:
#         counts = get_table_counts()
#         for table, count in counts.items():
#             st.metric(table.replace('stg_', ''), f"{count:,}")
#     except Exception:
#         st.warning("Connect to database to see stats")
    
#     st.markdown("---")
#     st.markdown("### 🏗️ Architecture")
#     st.markdown("""
#     - **Extract**: NBA API + CSV
#     - **Transform**: Pandas
#     - **Load**: PostgreSQL
#     - **Visualize**: Streamlit
#     """)
    
#     st.markdown("---")
#     st.markdown("### 📅 Last Updated")
#     st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# # ──────────────────────────────────────────────────────────────
# # MAIN CONTENT
# # ──────────────────────────────────────────────────────────────

# st.title("🏀 NBA Data Ingestion Pipeline")
# st.caption("ETL Pipeline Monitoring Dashboard")

# # ──────────────────────────────────────────────────────────────
# # NAVIGATION
# # ──────────────────────────────────────────────────────────────

# # Create navigation tabs
# tabs = st.tabs([
#     "🏠 Overview",
#     "📊 Database Metrics",
#     "📋 Data Quality",
#     "🏀 NBA Analytics",
#     "🗃️ Data Explorer",
#     "ℹ️ About"
# ])

# # ──────────────────────────────────────────────────────────────
# # TAB 1: OVERVIEW
# # ──────────────────────────────────────────────────────────────

# with tabs[0]:
#     st.markdown("### Pipeline Status")
    
#     try:
#         counts = get_table_counts()
#         summary = get_pipeline_summary()
        
#         # Status row
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <div class="metric-value">{counts.get('stg_games', 0):,}</div>
#                 <div class="metric-label">🏀 Games</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <div class="metric-value">{counts.get('stg_playerStats', 0):,}</div>
#                 <div class="metric-label">👤 Players</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <div class="metric-value">{counts.get('stg_teamStats', 0):,}</div>
#                 <div class="metric-label">🏆 Teams</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col4:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <div class="metric-value">{counts.get('stg_bettingLines', 0):,}</div>
#                 <div class="metric-label">📈 Betting Lines</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         st.markdown("---")
        
#         # ETL Flow
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             st.markdown("### 🔄 ETL Pipeline Flow")
#             st.markdown("""
#             <div class="pipeline-flow">
#                 <span style="color:#1f77b4;">NBA API</span><br>
#                 <span class="flow-arrow">⬇️</span><br>
#                 <span style="color:#ff7f0e;">Extract</span><br>
#                 <span class="flow-arrow">⬇️</span><br>
#                 <span style="color:#2ca02c;">Transform</span><br>
#                 <span class="flow-arrow">⬇️</span><br>
#                 <span style="color:#d62728;">Validation</span><br>
#                 <span class="flow-arrow">⬇️</span><br>
#                 <span style="color:#9467bd;">Deduplication</span><br>
#                 <span class="flow-arrow">⬇️</span><br>
#                 <span style="color:#1f77b4;">PostgreSQL</span>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             st.markdown("### 📊 Summary")
#             st.metric("Total Rows", f"{summary['total_rows']:,}")
#             st.metric("Data Quality Score", f"{summary['quality_score']}%")
#             st.metric("Issues Found", f"{summary['issues']:,}")
            
#             # Status indicator
#             if summary['issues'] == 0:
#                 st.markdown('🟢 **Status: SUCCESS**')
#             else:
#                 st.markdown('🟡 **Status: WARNING**')
        
#     except Exception as e:
#         st.error(f"Error loading dashboard: {e}")
#         st.info("Make sure your database is running and has data loaded.")

# # ──────────────────────────────────────────────────────────────
# # TAB 2: DATABASE METRICS
# # ──────────────────────────────────────────────────────────────
# # In dashboard.py - TAB 2: DATABASE METRICS

# with tabs[1]:
#     st.markdown("### 📊 Database Metrics")
    
#     try:
#         counts = get_table_counts()
        
#         # Show metric cards
#         st.markdown("#### 📈 Table Row Counts")
#         cols = st.columns(4)
#         for i, (table, count) in enumerate(counts.items()):
#             with cols[i % 4]:
#                 st.metric(
#                     table.replace('stg_', ''),
#                     f"{count:,}",
#                     delta="✅" if count > 0 else "⚠️ Empty"
#                 )
        
#         st.markdown("---")
        
#         # ──────────────────────────────────────────────────────────────
#         # TABLE DETAILS - WITH SCHEMA FOR EACH TABLE
#         # ──────────────────────────────────────────────────────────────
        
#         st.markdown("### 📋 Table Details with Schema")
#         st.caption("Each table shows: Sample data (first 5 rows) + Column Types")
        
#         # Get all table schemas
#         schemas = get_table_schemas()
        
#         for table, count in counts.items():
#             if count > 0:
#                 expander_label = f"📁 {table} ({count:,} rows)"
#             else:
#                 expander_label = f"📁 {table} (⚠️ EMPTY)"
            
#             with st.expander(expander_label):
#                 # ── Get sample data ──
#                 df_sample = get_table_data(table, 5)
                
#                 # ── Show sample data ──
#                 st.markdown("**📊 Sample Data (first 5 rows)**")
#                 if not df_sample.empty:
#                     st.dataframe(df_sample, use_container_width=True)
#                 else:
#                     st.caption("No sample data available")
                
#                 st.markdown("---")
                
#                 # ── SHOW COLUMN INFORMATION ──
#                 st.markdown("**📋 Column Information**")
                
#                 if table in schemas and schemas[table]:
#                     # Get column info
#                     col_data = schemas[table]
                    
#                     # Create schema DataFrame
#                     schema_df = pd.DataFrame([
#                         {'Column': col[0], 'Data Type': col[1], 'Nullable': col[2] if len(col) > 2 else 'YES'}
#                         for col in col_data['columns']
#                     ])
                    
#                     # Add sample null counts
#                     if not df_sample.empty:
#                         null_counts = df_sample.isnull().sum().values
#                         schema_df['Null in Sample'] = null_counts
                    
#                     st.dataframe(schema_df, use_container_width=True)
#                 else:
#                     st.warning("No column information available")
                
#                 # ── Show column count ──
#                 st.caption(f"📊 {len(schema_df)} columns total")
    
#     except Exception as e:
#         st.error(f"Error loading database metrics: {e}")
#         import traceback
#         with st.expander("Show error details"):
#             st.code(traceback.format_exc())

# # ──────────────────────────────────────────────────────────────
# # TAB 3: DATA QUALITY
# # ──────────────────────────────────────────────────────────────

# # In dashboard.py - TAB 3: DATA QUALITY

# with tabs[2]:
#     st.markdown("### 📋 Data Quality Dashboard")
    
#     try:
#         metrics = get_data_quality_metrics()
#         summary = get_pipeline_summary()
        
#         # ── Show metrics cards ──
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             is_ok = metrics['missing_home_score'] == 0
#             st.metric(
#                 "Missing Home Scores",
#                 f"{metrics['missing_home_score']:,}",
#                 delta="✅ OK" if is_ok else "⚠️ ISSUE"
#             )
        
#         with col2:
#             is_ok = metrics['missing_away_score'] == 0
#             st.metric(
#                 "Missing Away Scores",
#                 f"{metrics['missing_away_score']:,}",
#                 delta="✅ OK" if is_ok else "⚠️ ISSUE"
#             )
        
#         with col3:
#             # ✅ Show the 0 minutes issue prominently
#             is_ok = metrics['players_0_min'] == 0
#             st.metric(
#                 "Players with 0 Min",
#                 f"{metrics['players_0_min']:,}",
#                 delta="⚠️ ISSUE" if not is_ok else "✅ OK",
#                 delta_color="off" if not is_ok else "normal"
#             )
        
#         with col4:
#             total_orphans = metrics['orphan_player_stats'] + metrics['orphan_team_stats']
#             is_ok = total_orphans == 0
#             st.metric(
#                 "Orphan Records",
#                 f"{total_orphans:,}",
#                 delta="✅ OK" if is_ok else "⚠️ ISSUE"
#             )
        
#         st.markdown("---")
        
#         # ── Data Quality Score ──
#         st.markdown(f"""
#         ### 📊 Data Quality Score: {summary['quality_score']}%
#         """)
        
#         # Progress bar with color based on score
#         score = summary['quality_score']
#         if score >= 99:
#             color = "green"
#         elif score >= 95:
#             color = "yellow"
#         else:
#             color = "red"
        
#         st.progress(score / 100)
        
#         # Show what's affecting the score
#         st.caption(f"Based on {summary['total_rows']:,} total rows and {summary['issues']:,} issues found.")
        
#         # ── Show issue breakdown ──
#         st.markdown("### 🔍 Issue Breakdown")
        
#         issues_df = pd.DataFrame([
#             {'Issue': 'Missing Home Scores', 'Count': metrics['missing_home_score']},
#             {'Issue': 'Missing Away Scores', 'Count': metrics['missing_away_score']},
#             {'Issue': 'Players with 0 Minutes', 'Count': metrics['players_0_min']},
#             {'Issue': 'Orphan Player Stats', 'Count': metrics['orphan_player_stats']},
#             {'Issue': 'Orphan Team Stats', 'Count': metrics['orphan_team_stats']}
#         ])
        
#         # Only show issues with count > 0
#         issues_df = issues_df[issues_df['Count'] > 0]
        
#         if not issues_df.empty:
#             st.dataframe(issues_df, use_container_width=True)
            
#             # Visualize issues
#             import plotly.express as px
#             fig = px.bar(
#                 issues_df,
#                 x='Issue',
#                 y='Count',
#                 title='Data Quality Issues',
#                 color='Count',
#                 color_continuous_scale='Reds',
#                 text='Count'
#             )
#             fig.update_traces(textposition='outside')
#             fig.update_layout(height=300)
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.success("🎉 No data quality issues found!")
        
#         # ── Show the 0 minutes players as a warning ──
#         if metrics['players_0_min'] > 0:
#             with st.expander(f"⚠️ {metrics['players_0_min']} Players with 0 Minutes but Positive Points"):
#                 st.warning("""
#                 These players have recorded points but 0 minutes played.
#                 This typically indicates:
#                 - Data entry errors
#                 - Players who played less than 1 minute
#                 - Garbage time stats without minute tracking
#                 """)
                
#                 # Show sample of these players
#                 conn = get_connection()
#                 query = """
#                     SELECT playerName, team, points, minutes
#                     FROM stg_playerStats
#                     WHERE minutes = 0 AND points > 0
#                     LIMIT 10
#                 """
#                 df_sample = pd.read_sql(query, conn)
#                 conn.close()
                
#                 if not df_sample.empty:
#                     st.dataframe(df_sample, use_container_width=True)
#                     st.caption("Showing first 10 of {metrics['players_0_min']} records")
        
#     except Exception as e:
#         st.error(f"Error loading data quality metrics: {e}")
# # ──────────────────────────────────────────────────────────────
# # TAB 4: NBA ANALYTICS
# # ──────────────────────────────────────────────────────────────

# with tabs[3]:
#     st.markdown("### 🏀 NBA Analytics")
    
#     try:
#         # Season Trends
#         st.markdown("#### 📈 Scoring Trends by Season")
#         season_df = get_season_trends()
        
#         if not season_df.empty:
#             import plotly.express as px
            
#             fig = px.line(
#                 season_df,
#                 x='season',
#                 y=['avg_home_score', 'avg_away_score', 'avg_total'],
#                 title='Average Points by Season',
#                 labels={'value': 'Average Points', 'season': 'Season'},
#                 markers=True
#             )
#             fig.update_layout(height=400)
#             st.plotly_chart(fig, use_container_width=True)
        
#         # Top Teams
#         st.markdown("#### 🏆 Top Scoring Teams")
#         teams_df = get_top_teams(10)
        
#         if not teams_df.empty:
#             fig = px.bar(
#                 teams_df,
#                 x='team',
#                 y='avg_points',
#                 title='Top 10 Teams by Average Points',
#                 color='avg_points',
#                 color_continuous_scale='blues',
#                 text='avg_points'
#             )
#             fig.update_traces(textposition='outside')
#             fig.update_layout(height=400)
#             st.plotly_chart(fig, use_container_width=True)
        
#         # Player Points Distribution
#         st.markdown("#### 📊 Player Points Distribution")
#         points_df = get_player_points_distribution()
        
#         if not points_df.empty:
#             fig = px.bar(
#                 points_df,
#                 x='point_range',
#                 y='count',
#                 title='Distribution of Player Points',
#                 color='point_range',
#                 text='count'
#             )
#             fig.update_traces(textposition='outside')
#             fig.update_layout(height=400)
#             st.plotly_chart(fig, use_container_width=True)
        
#     except Exception as e:
#         st.error(f"Error loading NBA analytics: {e}")

# # ──────────────────────────────────────────────────────────────
# # TAB 5: DATA EXPLORER
# # ──────────────────────────────────────────────────────────────

# with tabs[4]:
#     st.markdown("### 🗃️ Data Explorer")
    
#     try:
#         table_options = {
#             'stg_games': '🏀 Games',
#             'stg_playerStats': '👤 Player Stats',
#             'stg_teamStats': '🏆 Team Stats',
#             'stg_bettingLines': '📈 Betting Lines'
#         }
        
#         selected_table = st.selectbox(
#             "Select Table",
#             options=list(table_options.keys()),
#             format_func=lambda x: table_options[x]
#         )
        
#         # Limit slider
#         limit = st.slider("Rows to display", 10, 500, 100, step=10)
        
#         if selected_table:
#             df = get_table_data(selected_table, limit)
#             st.dataframe(df, use_container_width=True)
            
#             st.caption(f"Showing {len(df)} of {get_table_counts().get(selected_table, 0):,} rows")
            
#             # Column info
#             with st.expander("📋 Column Info"):
#                 col_info = pd.DataFrame({
#                     'Column': df.columns,
#                     'Type': df.dtypes.astype(str),
#                     'Null Count': df.isnull().sum().values,
#                     'Unique Values': df.nunique().values
#                 })
#                 st.dataframe(col_info, use_container_width=True)
        
#     except Exception as e:
#         st.error(f"Error loading data explorer: {e}")

# # ──────────────────────────────────────────────────────────────
# # TAB 6: ABOUT
# # ──────────────────────────────────────────────────────────────

# with tabs[5]:
#     st.markdown("### ℹ️ About This Project")
    
#     st.markdown("""
#     ## 🏀 NBA Data Ingestion Pipeline
    
#     ### 📌 Overview
#     This project demonstrates a complete ETL pipeline for NBA data, 
#     ingesting from both CSV files and the NBA Stats API into PostgreSQL.
    
#     ### 🛠️ Technologies Used
#     - **Python**: Core ETL logic
#     - **Pandas**: Data transformation and cleaning
#     - **PostgreSQL**: Data storage
#     - **NBA API**: Live data source
#     - **Streamlit**: Dashboard visualization
#     - **Plotly**: Interactive charts
    
#     ### 🔄 Pipeline Features
#     - ✅ Extract from CSV and API sources
#     - ✅ Data validation and cleaning
#     - ✅ Deduplication using matchKey
#     - ✅ PostgreSQL staging tables
#     - ✅ Data quality monitoring
#     - ✅ Interactive dashboard
    
#     ### 📊 Data Model
#     - **stg_games**: Game-level data (scores, teams, dates)
#     - **stg_playerStats**: Player performance statistics
#     - **stg_teamStats**: Team performance statistics
#     - **stg_bettingLines**: Betting odds and lines
    
#     ### 🎯 Purpose
#     This project was built as a data engineering portfolio piece 
#     to demonstrate:
#     1. Building production-ready ETL pipelines
#     2. Working with multiple data sources
#     3. Data quality monitoring
#     4. Creating data dashboards
#     5. Using modern data stack tools
#     """)
    
#     st.divider()
    
#     col1, col2 = st.columns(2)
#     with col1:
#         st.markdown("**🔗 Source Code**")
#         st.code("https://github.com/yourusername/nba_data_ingestion_pipeline")
    
#     with col2:
#         st.markdown("**📅 Last Updated**")
#         st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# # ──────────────────────────────────────────────────────────────
# # FOOTER
# # ──────────────────────────────────────────────────────────────

# st.divider()
# st.caption("🏀 NBA Data Ingestion Pipeline · Built with Streamlit")
# src/dashboard.py
"""
NBA Data Ingestion Dashboard - Main Entry Point
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys
import re
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dashboard_utils import *
from src.database import get_connection

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="NBA Data Ingestion Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #888;
    }
    .status-success {
        color: #00cc66;
        font-weight: bold;
    }
    .status-failed {
        color: #ff4444;
        font-weight: bold;
    }
    .log-info {
        color: #1f77b4;
    }
    .log-warning {
        color: #ffa500;
    }
    .log-error {
        color: #ff4444;
        font-weight: bold;
    }
    .pipeline-flow {
        text-align: center;
        font-size: 1.1rem;
        padding: 20px;
    }
    .flow-arrow {
        color: #1f77b4;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# LOG VIEWER FUNCTIONS
# ──────────────────────────────────────────────────────────────

def get_log_file_path():
    """Get the path to the ingestion log file"""
    from config.config import PostgresConfig
    log_path = Path(PostgresConfig.LOGS_DIR) / "ingestion.log"
    return log_path

def parse_log_line(line):
    """Parse a single log line into components"""
    pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.+)$'
    match = re.match(pattern, line.strip())
    if match:
        timestamp, level, message = match.groups()
        return {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'raw': line.strip()
        }
    return None

def load_logs(limit=1000):
    """Load and parse log file"""
    log_path = get_log_file_path()
    
    if not log_path.exists():
        return pd.DataFrame(), "Log file not found"
    
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
        
        parsed = []
        for line in lines[-limit:]:
            parsed_line = parse_log_line(line)
            if parsed_line:
                parsed.append(parsed_line)
        
        if not parsed:
            return pd.DataFrame(), "No parsed log entries found"
        
        df = pd.DataFrame(parsed)
        return df, None
    except Exception as e:
        return pd.DataFrame(), f"Error reading log file: {e}"

def get_log_summary(df):
    """Get summary statistics from log data"""
    if df.empty:
        return {}
    
    summary = {
        'total': len(df),
        'info': len(df[df['level'] == 'INFO']),
        'warning': len(df[df['level'] == 'WARNING']),
        'error': len(df[df['level'] == 'ERROR']),
        'success': len(df[df['message'].str.contains('PIPELINE COMPLETED SUCCESSFULLY', case=False)]),
        'start_time': df['timestamp'].iloc[-1] if not df.empty else None,
        'end_time': df['timestamp'].iloc[0] if not df.empty else None,
    }
    return summary

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🏀 NBA Pipeline")
    st.markdown("---")
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    try:
        counts = get_table_counts()
        for table, count in counts.items():
            st.metric(table.replace('stg_', ''), f"{count:,}")
    except Exception:
        st.warning("Connect to database to see stats")
    
    st.markdown("---")
    st.markdown("### 🏗️ Architecture")
    st.markdown("""
    - **Extract**: NBA API + CSV
    - **Transform**: Pandas
    - **Load**: PostgreSQL
    - **Visualize**: Streamlit
    """)
    
    st.markdown("---")
    st.markdown("### 📅 Last Updated")
    st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ──────────────────────────────────────────────────────────────
# MAIN CONTENT
# ──────────────────────────────────────────────────────────────

st.title("🏀 NBA Data Ingestion Pipeline")
st.caption("ETL Pipeline Monitoring Dashboard")

# ──────────────────────────────────────────────────────────────
# NAVIGATION
# ──────────────────────────────────────────────────────────────

tabs = st.tabs([
    "🏠 Overview",
    "📊 Database Metrics",
    "📋 Data Quality",
    "🏀 NBA Analytics",
    "📝 Pipeline Logs",
    "🗃️ Data Explorer",
    "ℹ️ About"
])

# ──────────────────────────────────────────────────────────────
# TAB 1: OVERVIEW
# ──────────────────────────────────────────────────────────────

with tabs[0]:
    st.markdown("### Pipeline Status")
    
    try:
        counts = get_table_counts()
        summary = get_pipeline_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{counts.get('stg_games', 0):,}</div>
                <div class="metric-label">🏀 Games</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{counts.get('stg_playerStats', 0):,}</div>
                <div class="metric-label">👤 Players</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{counts.get('stg_teamStats', 0):,}</div>
                <div class="metric-label">🏆 Teams</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{counts.get('stg_bettingLines', 0):,}</div>
                <div class="metric-label">📈 Betting Lines</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🔄 ETL Pipeline Flow")
            st.markdown("""
            <div class="pipeline-flow">
                <span style="color:#1f77b4;">NBA API</span><br>
                <span class="flow-arrow">⬇️</span><br>
                <span style="color:#ff7f0e;">Extract</span><br>
                <span class="flow-arrow">⬇️</span><br>
                <span style="color:#2ca02c;">Transform</span><br>
                <span class="flow-arrow">⬇️</span><br>
                <span style="color:#d62728;">Validation</span><br>
                <span class="flow-arrow">⬇️</span><br>
                <span style="color:#9467bd;">Deduplication</span><br>
                <span class="flow-arrow">⬇️</span><br>
                <span style="color:#1f77b4;">PostgreSQL</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📊 Summary")
            st.metric("Total Rows", f"{summary['total_rows']:,}")
            st.metric("Data Quality Score", f"{summary['quality_score']}%")
            st.metric("Issues Found", f"{summary['issues']:,}")
            
            if summary['issues'] == 0:
                st.markdown('🟢 **Status: SUCCESS**')
            else:
                st.markdown('🟡 **Status: WARNING**')
        
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        st.info("Make sure your database is running and has data loaded.")

# ──────────────────────────────────────────────────────────────
# TAB 2: DATABASE METRICS
# ──────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────
# TAB 2: DATABASE METRICS (UPDATED - No Table Details)
# ──────────────────────────────────────────────────────────────

with tabs[1]:
    st.markdown("### 📊 Database Metrics")
    st.caption("Overview of all staging tables and their row counts")
    
    try:
        counts = get_table_counts()
        
        # ── Metric Cards ──
        st.markdown("#### 📈 Table Row Counts")
        cols = st.columns(4)
        
        # Define icons for each table
        table_icons = {
            'stg_games': '🏀',
            'stg_playerStats': '👤',
            'stg_teamStats': '🏆',
            'stg_bettingLines': '📈'
        }
        
        for i, (table, count) in enumerate(counts.items()):
            with cols[i % 4]:
                icon = table_icons.get(table, '📊')
                st.metric(
                    f"{icon} {table.replace('stg_', '')}",
                    f"{count:,}",
                    delta="✅" if count > 0 else "⚠️ Empty"
                )
        
        st.markdown("---")
        
        # ── Bar Chart ──
        if any(counts.values()):
            import plotly.express as px
            
            df_bar = pd.DataFrame([
                {
                    'Table': table.replace('stg_', ''), 
                    'Count': count,
                    'Icon': table_icons.get(table, '📊')
                }
                for table, count in counts.items() if count > 0
            ])
            
            if not df_bar.empty:
                fig = px.bar(
                    df_bar,
                    x='Table',
                    y='Count',
                    title='Table Row Counts',
                    color='Table',
                    color_discrete_sequence=px.colors.qualitative.Set1,
                    text='Count',
                    height=400
                )
                fig.update_traces(
                    textposition='outside',
                    texttemplate='%{text:,.0f}'
                )
                fig.update_layout(
                    xaxis_title="Table",
                    yaxis_title="Row Count",
                    showlegend=False,
                    font=dict(size=14)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # ── Summary Table ──
                st.markdown("#### 📋 Table Summary")
                
                # Calculate total rows
                total_rows = sum(counts.values())
                
                summary_df = pd.DataFrame([
                    {
                        'Table': table.replace('stg_', ''),
                        'Rows': f"{count:,}",
                        'Percentage': f"{(count / total_rows * 100):.1f}%" if total_rows > 0 else "0%"
                    }
                    for table, count in counts.items() if count > 0
                ])
                
                st.dataframe(
                    summary_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'Table': 'Table Name',
                        'Rows': 'Row Count',
                        'Percentage': 'Percentage of Total'
                    }
                )
                
                # ── Total Row Count ──
                st.caption(f"📊 **Total Rows Across All Tables: {total_rows:,}**")
                
        else:
            st.warning("⚠️ No data found in any tables. Run the ingestion pipeline to load data.")
            st.code("python3 -m src.main --source all --init")
    
    except Exception as e:
        st.error(f"Error loading database metrics: {e}")
        import traceback
        with st.expander("Show error details"):
            st.code(traceback.format_exc())

# ──────────────────────────────────────────────────────────────
# TAB 3: DATA QUALITY
# ──────────────────────────────────────────────────────────────

with tabs[2]:
    st.markdown("### 📋 Data Quality Dashboard")
    
    try:
        metrics = get_data_quality_metrics()
        summary = get_pipeline_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            is_ok = metrics['missing_home_score'] == 0
            st.metric(
                "Missing Home Scores",
                f"{metrics['missing_home_score']:,}",
                delta="✅ OK" if is_ok else "⚠️ ISSUE"
            )
        
        with col2:
            is_ok = metrics['missing_away_score'] == 0
            st.metric(
                "Missing Away Scores",
                f"{metrics['missing_away_score']:,}",
                delta="✅ OK" if is_ok else "⚠️ ISSUE"
            )
        
        with col3:
            is_ok = metrics['players_0_min'] == 0
            st.metric(
                "Players with 0 Min",
                f"{metrics['players_0_min']:,}",
                delta="⚠️ ISSUE" if not is_ok else "✅ OK",
                delta_color="off" if not is_ok else "normal"
            )
        
        with col4:
            total_orphans = metrics['orphan_player_stats'] + metrics['orphan_team_stats']
            is_ok = total_orphans == 0
            st.metric(
                "Orphan Records",
                f"{total_orphans:,}",
                delta="✅ OK" if is_ok else "⚠️ ISSUE"
            )
        
        st.markdown("---")
        
        st.markdown(f"""
        ### 📊 Data Quality Score: {summary['quality_score']}%
        """)
        
        st.progress(summary['quality_score'] / 100)
        st.caption(f"Based on {summary['total_rows']:,} total rows and {summary['issues']:,} issues found.")
        
        st.markdown("### 🔍 Issue Breakdown")
        
        issues_df = pd.DataFrame([
            {'Issue': 'Missing Home Scores', 'Count': metrics['missing_home_score']},
            {'Issue': 'Missing Away Scores', 'Count': metrics['missing_away_score']},
            {'Issue': 'Players with 0 Minutes', 'Count': metrics['players_0_min']},
            {'Issue': 'Orphan Player Stats', 'Count': metrics['orphan_player_stats']},
            {'Issue': 'Orphan Team Stats', 'Count': metrics['orphan_team_stats']}
        ])
        
        issues_df = issues_df[issues_df['Count'] > 0]
        
        if not issues_df.empty:
            st.dataframe(issues_df, use_container_width=True)
            
            fig = px.bar(
                issues_df,
                x='Issue',
                y='Count',
                title='Data Quality Issues',
                color='Count',
                color_continuous_scale='Reds',
                text='Count'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("🎉 No data quality issues found!")
        
        if metrics['players_0_min'] > 0:
            with st.expander(f"⚠️ {metrics['players_0_min']} Players with 0 Minutes but Positive Points"):
                st.warning("""
                These players have recorded points but 0 minutes played.
                This typically indicates data entry errors or players who played less than 1 minute.
                """)
                
                conn = get_connection()
                query = """
                    SELECT playerName, team, points, minutes
                    FROM stg_playerStats
                    WHERE minutes = 0 AND points > 0
                    LIMIT 10
                """
                df_sample = pd.read_sql(query, conn)
                conn.close()
                
                if not df_sample.empty:
                    st.dataframe(df_sample, use_container_width=True)
                    st.caption(f"Showing first 10 of {metrics['players_0_min']} records")
        
    except Exception as e:
        st.error(f"Error loading data quality metrics: {e}")

# ──────────────────────────────────────────────────────────────
# TAB 4: NBA ANALYTICS
# ──────────────────────────────────────────────────────────────

with tabs[3]:
    st.markdown("### 🏀 NBA Analytics")
    
    try:
        st.markdown("#### 📈 Scoring Trends by Season")
        season_df = get_season_trends()
        
        if not season_df.empty:
            fig = px.line(
                season_df,
                x='season',
                y=['avg_home_score', 'avg_away_score', 'avg_total'],
                title='Average Points by Season',
                labels={'value': 'Average Points', 'season': 'Season'},
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### 🏆 Top Scoring Teams")
        teams_df = get_top_teams(10)
        
        if not teams_df.empty:
            fig = px.bar(
                teams_df,
                x='team',
                y='avg_points',
                title='Top 10 Teams by Average Points',
                color='avg_points',
                color_continuous_scale='blues',
                text='avg_points'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### 📊 Player Points Distribution")
        points_df = get_player_points_distribution()
        
        if not points_df.empty:
            fig = px.bar(
                points_df,
                x='point_range',
                y='count',
                title='Distribution of Player Points',
                color='point_range',
                text='count'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading NBA analytics: {e}")

# ──────────────────────────────────────────────────────────────
# TAB 5: PIPELINE LOGS
# ──────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────
# TAB 5: PIPELINE LOGS (UPDATED)
# ──────────────────────────────────────────────────────────────

with tabs[4]:
    st.markdown("### 📝 Pipeline Execution Logs")
    st.caption("Real-time log viewer showing the most recent pipeline activity")
    
    # ── Controls ──
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        log_limit = st.selectbox(
            "Number of lines to display",
            options=[10, 25, 50, 100, 250, 500, 1000],
            index=3,  # Default to 100
            help="Select how many recent log lines to display"
        )
    
    with col2:
        log_filter = st.multiselect(
            "Filter by level",
            options=['INFO', 'WARNING', 'ERROR'],
            default=['INFO', 'WARNING', 'ERROR'],
            help="Filter logs by severity level"
        )
    
    with col3:
        # Auto-refresh option
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=False, help="Refresh every 5 seconds")
    
    with col4:
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Auto-refresh logic
    if auto_refresh:
        st.caption("🔄 Auto-refreshing every 5 seconds...")
        import time
        time.sleep(5)
        st.rerun()
    
    st.markdown("---")
    
    # ── Show log file location ──
    log_path = get_log_file_path()
    st.caption(f"📁 Log file: `{log_path}`")
    
    # ── Load Logs ──
    df, error = load_logs(limit=log_limit)
    
    if error:
        st.error(f"Error loading logs: {error}")
        st.info("Make sure the ingestion pipeline has been run and logs exist.")
        st.code("python3 -m src.main --source all --init")
        
    elif df.empty:
        st.warning("No log entries found. Run the pipeline to generate logs.")
        st.code("python3 -m src.main --source all --init")
        
    else:
        # ── Summary Metrics ──
        summary = get_log_summary(df)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📊 Total Lines", summary['total'])
        with col2:
            st.metric("ℹ️ INFO", summary['info'])
        with col3:
            st.metric("⚠️ WARNINGS", summary['warning'])
        with col4:
            st.metric("❌ ERRORS", summary['error'])
        with col5:
            st.metric("✅ SUCCESS", summary['success'])
        
        st.markdown("---")
        
        # ── Filter and Display Logs ──
        filtered_df = df[df['level'].isin(log_filter)]
        
        if filtered_df.empty:
            st.info("No logs match the selected filters.")
            
        else:
            # ✅ SHOW MOST RECENT FIRST (NEWEST AT TOP)
            filtered_df = filtered_df.iloc[::-1]
            
            # ── Display Logs with Color Coding ──
            for _, row in filtered_df.iterrows():
                level = row['level']
                message = row['message']
                timestamp = row['timestamp']
                
                # Color based on level
                if level == 'INFO':
                    color = '#1f77b4'  # Blue
                elif level == 'WARNING':
                    color = '#ffa500'  # Orange
                elif level == 'ERROR':
                    color = '#ff4444'  # Red
                else:
                    color = '#ffffff'  # White
                
                # Icons for important messages
                if 'PIPELINE COMPLETED SUCCESSFULLY' in message:
                    icon = "✅ "
                elif 'Error' in message or 'ERROR' in message or 'FAILED' in message:
                    icon = "❌ "
                elif 'WARNING' in message:
                    icon = "⚠️ "
                elif 'Starting' in message or 'STARTED' in message:
                    icon = "🚀 "
                elif 'Loaded' in message or 'loaded' in message:
                    icon = "📦 "
                else:
                    icon = ""
                
                st.markdown(
                    f"<span style='color:{color}; font-family: monospace; font-size: 13px;'>"
                    f"{timestamp} - {level} - {icon}{message}"
                    f"</span>",
                    unsafe_allow_html=True
                )
            
            st.caption(f"Showing **{len(filtered_df)}** of **{len(df)}** most recent log entries")
            
            # ── Download Logs ──
            st.markdown("---")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Get full logs for download
                full_df, _ = load_logs_tail(limit=5000)
                if not full_df.empty:
                    st.download_button(
                        label="📥 Download Logs (last 5000 lines)",
                        data="\n".join(full_df['raw'].tolist()),
                        file_name=f"ingestion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            with col2:
                # Show log file info
                if log_path.exists():
                    file_size = log_path.stat().st_size / 1024
                    st.caption(f"📊 Log file size: {file_size:.1f} KB")
            
            # ── Pipeline Timeline ──
            st.markdown("---")
            st.markdown("### 📅 Pipeline Timeline")
            
            # Find start and end messages (from the full log, not filtered)
            full_df, _ = load_logs_tail(limit=1000)
            if not full_df.empty:
                start_messages = full_df[full_df['message'].str.contains('PIPELINE STARTED|STARTED|Starting', case=False)]
                end_messages = full_df[full_df['message'].str.contains('PIPELINE COMPLETED SUCCESSFULLY|COMPLETED|Finished', case=False)]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if not start_messages.empty:
                        st.metric("🚀 Pipeline Start", start_messages.iloc[-1]['timestamp'])
                    else:
                        st.metric("🚀 Pipeline Start", "N/A")
                
                with col2:
                    if not end_messages.empty:
                        st.metric("🏁 Pipeline End", end_messages.iloc[-1]['timestamp'])
                    else:
                        st.metric("🏁 Pipeline End", "N/A")
                
                with col3:
                    if not start_messages.empty and not end_messages.empty:
                        try:
                            start = datetime.strptime(start_messages.iloc[-1]['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                            end = datetime.strptime(end_messages.iloc[-1]['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                            runtime = end - start
                            st.metric("⏱️ Runtime", str(runtime).split('.')[0])
                        except:
                            st.metric("⏱️ Runtime", "N/A")
                    else:
                        st.metric("⏱️ Runtime", "N/A")
            
            # ── Error Summary ──
            errors = df[df['level'] == 'ERROR']
            if not errors.empty:
                st.markdown("---")
                st.warning(f"⚠️ {len(errors)} errors found in the logs")
                
                with st.expander(f"Show {len(errors)} errors", expanded=False):
                    # Show errors newest first
                    errors_sorted = errors.iloc[::-1]
                    for _, row in errors_sorted.head(20).iterrows():
                        st.code(f"{row['timestamp']} - {row['message']}")
                    
                    if len(errors) > 20:
                        st.caption(f"... and {len(errors) - 20} more errors")

# ──────────────────────────────────────────────────────────────
# TAB 6: DATA EXPLORER
# ──────────────────────────────────────────────────────────────

with tabs[5]:
    st.markdown("### 🗃️ Data Explorer")
    
    try:
        table_options = {
            'stg_games': '🏀 Games',
            'stg_playerStats': '👤 Player Stats',
            'stg_teamStats': '🏆 Team Stats',
            'stg_bettingLines': '📈 Betting Lines'
        }
        
        selected_table = st.selectbox(
            "Select Table",
            options=list(table_options.keys()),
            format_func=lambda x: table_options[x]
        )
        
        limit = st.slider("Rows to display", 10, 500, 100, step=10)
        
        if selected_table:
            df = get_table_data(selected_table, limit)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Showing {len(df)} of {get_table_counts().get(selected_table, 0):,} rows")
    
    except Exception as e:
        st.error(f"Error loading data explorer: {e}")

# ──────────────────────────────────────────────────────────────
# TAB 6: ABOUT
# ──────────────────────────────────────────────────────────────

with tabs[6]:
    st.markdown("### ℹ️ About This Project")
    
    st.markdown("""
    ## 🏀 NBA Data Ingestion Pipeline
    
    ### 📌 Overview
    This project demonstrates a complete ETL pipeline for NBA data, 
    ingesting from both CSV files and the NBA Stats API into PostgreSQL.
    
    ### 🛠️ Technologies Used
    - **Python**: Core ETL logic
    - **Pandas**: Data transformation and cleaning
    - **PostgreSQL**: Data storage
    - **NBA API**: Live data source
    - **Streamlit**: Dashboard visualization
    - **Plotly**: Interactive charts
    
    ### 🔄 Pipeline Features
    - ✅ Extract from CSV and API sources
    - ✅ Data validation and cleaning
    - ✅ Deduplication using matchKey
    - ✅ PostgreSQL staging tables
    - ✅ Data quality monitoring
    - ✅ Interactive dashboard
    
    ### 📊 Data Model
    - **stg_games**: Game-level data (scores, teams, dates)
    - **stg_playerStats**: Player performance statistics
    - **stg_teamStats**: Team performance statistics
    - **stg_bettingLines**: Betting odds and lines
    
    ### 🎯 Purpose
    This project was built as a data engineering portfolio piece 
    to demonstrate:
    1. Building production-ready ETL pipelines
    2. Working with multiple data sources
    3. Data quality monitoring
    4. Creating data dashboards
    5. Using modern data stack tools
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔗 Source Code**")
        st.code("https://github.com/jimsonjames0/nba_data_ingestion_pipeline")
    
    with col2:
        st.markdown("**📅 Last Updated**")
        st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────

st.divider()
st.caption("🏀 NBA Data Ingestion Pipeline · Built with Streamlit")

