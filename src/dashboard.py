# src/dashboard.py
"""
NBA Data Ingestion Dashboard - Main Entry Point
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

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
    .pipeline-flow {
        text-align: center;
        font-size: 1.1rem;
        padding: 20px;
    }
    .flow-arrow {
        color: #1f77b4;
        font-size: 1.5rem;
    }
    .sidebar .sidebar-content {
        background-color: #0e1117;
    }
    .stSelectbox label, .stMultiSelect label {
        color: #fafafa !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🏀 NBA Pipeline")
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    
    # Show live counts in sidebar
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

# Create navigation tabs
tabs = st.tabs([
    "🏠 Overview",
    "📊 Database Metrics",
    "📋 Data Quality",
    "🏀 NBA Analytics",
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
        
        # Status row
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
        
        # ETL Flow
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
            
            # Status indicator
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
# In dashboard.py - TAB 2: DATABASE METRICS

with tabs[1]:
    st.markdown("### 📊 Database Metrics")
    
    try:
        counts = get_table_counts()
        
        # Show metric cards
        st.markdown("#### 📈 Table Row Counts")
        cols = st.columns(4)
        for i, (table, count) in enumerate(counts.items()):
            with cols[i % 4]:
                st.metric(
                    table.replace('stg_', ''),
                    f"{count:,}",
                    delta="✅" if count > 0 else "⚠️ Empty"
                )
        
        st.markdown("---")
        
        # ──────────────────────────────────────────────────────────────
        # TABLE DETAILS - WITH SCHEMA FOR EACH TABLE
        # ──────────────────────────────────────────────────────────────
        
        st.markdown("### 📋 Table Details with Schema")
        st.caption("Each table shows: Sample data (first 5 rows) + Column Types")
        
        # Get all table schemas
        schemas = get_table_schemas()
        
        for table, count in counts.items():
            if count > 0:
                expander_label = f"📁 {table} ({count:,} rows)"
            else:
                expander_label = f"📁 {table} (⚠️ EMPTY)"
            
            with st.expander(expander_label):
                # ── Get sample data ──
                df_sample = get_table_data(table, 5)
                
                # ── Show sample data ──
                st.markdown("**📊 Sample Data (first 5 rows)**")
                if not df_sample.empty:
                    st.dataframe(df_sample, use_container_width=True)
                else:
                    st.caption("No sample data available")
                
                st.markdown("---")
                
                # ── SHOW COLUMN INFORMATION ──
                st.markdown("**📋 Column Information**")
                
                if table in schemas and schemas[table]:
                    # Get column info
                    col_data = schemas[table]
                    
                    # Create schema DataFrame
                    schema_df = pd.DataFrame([
                        {'Column': col[0], 'Data Type': col[1], 'Nullable': col[2] if len(col) > 2 else 'YES'}
                        for col in col_data['columns']
                    ])
                    
                    # Add sample null counts
                    if not df_sample.empty:
                        null_counts = df_sample.isnull().sum().values
                        schema_df['Null in Sample'] = null_counts
                    
                    st.dataframe(schema_df, use_container_width=True)
                else:
                    st.warning("No column information available")
                
                # ── Show column count ──
                st.caption(f"📊 {len(schema_df)} columns total")
    
    except Exception as e:
        st.error(f"Error loading database metrics: {e}")
        import traceback
        with st.expander("Show error details"):
            st.code(traceback.format_exc())

# ──────────────────────────────────────────────────────────────
# TAB 3: DATA QUALITY
# ──────────────────────────────────────────────────────────────

# In dashboard.py - TAB 3: DATA QUALITY

with tabs[2]:
    st.markdown("### 📋 Data Quality Dashboard")
    
    try:
        metrics = get_data_quality_metrics()
        summary = get_pipeline_summary()
        
        # ── Show metrics cards ──
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
            # ✅ Show the 0 minutes issue prominently
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
        
        # ── Data Quality Score ──
        st.markdown(f"""
        ### 📊 Data Quality Score: {summary['quality_score']}%
        """)
        
        # Progress bar with color based on score
        score = summary['quality_score']
        if score >= 99:
            color = "green"
        elif score >= 95:
            color = "yellow"
        else:
            color = "red"
        
        st.progress(score / 100)
        
        # Show what's affecting the score
        st.caption(f"Based on {summary['total_rows']:,} total rows and {summary['issues']:,} issues found.")
        
        # ── Show issue breakdown ──
        st.markdown("### 🔍 Issue Breakdown")
        
        issues_df = pd.DataFrame([
            {'Issue': 'Missing Home Scores', 'Count': metrics['missing_home_score']},
            {'Issue': 'Missing Away Scores', 'Count': metrics['missing_away_score']},
            {'Issue': 'Players with 0 Minutes', 'Count': metrics['players_0_min']},
            {'Issue': 'Orphan Player Stats', 'Count': metrics['orphan_player_stats']},
            {'Issue': 'Orphan Team Stats', 'Count': metrics['orphan_team_stats']}
        ])
        
        # Only show issues with count > 0
        issues_df = issues_df[issues_df['Count'] > 0]
        
        if not issues_df.empty:
            st.dataframe(issues_df, use_container_width=True)
            
            # Visualize issues
            import plotly.express as px
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
        
        # ── Show the 0 minutes players as a warning ──
        if metrics['players_0_min'] > 0:
            with st.expander(f"⚠️ {metrics['players_0_min']} Players with 0 Minutes but Positive Points"):
                st.warning("""
                These players have recorded points but 0 minutes played.
                This typically indicates:
                - Data entry errors
                - Players who played less than 1 minute
                - Garbage time stats without minute tracking
                """)
                
                # Show sample of these players
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
                    st.caption("Showing first 10 of {metrics['players_0_min']} records")
        
    except Exception as e:
        st.error(f"Error loading data quality metrics: {e}")
# ──────────────────────────────────────────────────────────────
# TAB 4: NBA ANALYTICS
# ──────────────────────────────────────────────────────────────

with tabs[3]:
    st.markdown("### 🏀 NBA Analytics")
    
    try:
        # Season Trends
        st.markdown("#### 📈 Scoring Trends by Season")
        season_df = get_season_trends()
        
        if not season_df.empty:
            import plotly.express as px
            
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
        
        # Top Teams
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
        
        # Player Points Distribution
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
# TAB 5: DATA EXPLORER
# ──────────────────────────────────────────────────────────────

with tabs[4]:
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
        
        # Limit slider
        limit = st.slider("Rows to display", 10, 500, 100, step=10)
        
        if selected_table:
            df = get_table_data(selected_table, limit)
            st.dataframe(df, use_container_width=True)
            
            st.caption(f"Showing {len(df)} of {get_table_counts().get(selected_table, 0):,} rows")
            
            # Column info
            with st.expander("📋 Column Info"):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Null Count': df.isnull().sum().values,
                    'Unique Values': df.nunique().values
                })
                st.dataframe(col_info, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading data explorer: {e}")

# ──────────────────────────────────────────────────────────────
# TAB 6: ABOUT
# ──────────────────────────────────────────────────────────────

with tabs[5]:
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
        st.code("https://github.com/yourusername/nba_data_ingestion_pipeline")
    
    with col2:
        st.markdown("**📅 Last Updated**")
        st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────

st.divider()
st.caption("🏀 NBA Data Ingestion Pipeline · Built with Streamlit")