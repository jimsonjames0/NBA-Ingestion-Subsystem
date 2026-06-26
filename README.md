# NBA Data Ingestion Pipeline

A Python-based data ingestion pipeline for NBA statistics and betting data.

## Features

- **CSV Ingestion**: Load historical NBA data from CSV files
- **API Integration**: Fetch live data from NBA API
- **Data Cleaning**: Automated data validation and cleaning
- **PostgreSQL Storage**: Structured staging tables with matchKey deduplication
- **Streamlit Dashboard**: Visual analytics for betting insights

## Tech Stack

- Python 3.10+
- PostgreSQL
- Streamlit
- nba_api
- Pandas

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your credentials
6. Create the database: `python -m src.database`
7. Run the pipeline: `python -m src.main --source all --init`

## Usage

```bash
# Load CSV data
python -m src.main --source csv --init

# Load API data
python -m src.main --source api --season 2024-25 --players "LeBron James"

# Run dashboard
streamlit run src/dashboard.py
