"""
main.py

Entry point for the Fashion Studio ETL Pipeline.

This script orchestrates the full Extract, Transform, Load (ETL) process:
    1. Extract: Scrapes product data from the Fashion Studio website
    2. Transform: Cleans and validates the raw data
    3. Load: Saves the cleaned data to CSV, Google Sheets, and PostgreSQL

Environment variables are loaded from a .env file using python-dotenv.
"""

import os
from dotenv import load_dotenv
from utils.extract import scrape_website
from utils.transform import transform_to_DataFrame, transform_data
from utils.load import load_to_csv, load_to_google_sheets, load_to_postgresql
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


def main() -> None:
    """
    Run the full ETL pipeline.

    Reads configuration from environment variables, then sequentially
    runs the Extract, Transform, and Load stages. Exits early if
    extraction returns no data or transformation fails.
    """
    BASE_URL = os.getenv("BASE_URL")
    JSON_KEY = os.getenv("JSON_KEY_PATH")
    SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
    DB_URL = os.getenv("DB_URL")

    # 1. EXTRACT
    logger.info("Starting Extraction Stage...")
    raw_data = scrape_website(BASE_URL)

    if not raw_data:
        logger.warning("No data extracted. Pipeline stopped.")
        return

    # 2. TRANSFORM
    logger.info("Starting Transformation Stage...")
    df_raw = transform_to_DataFrame(raw_data)
    df_clean = transform_data(df_raw)

    if df_clean is not None:
        # 3. LOAD
        logger.info("Starting Loading Stage...")
        load_to_csv(df_clean)
        load_to_google_sheets(df_clean, SPREADSHEET_NAME, JSON_KEY)
        load_to_postgresql(df_clean, DB_URL)
        logger.info("ETL Pipeline Completed Successfully!")
    else:
        logger.error("Process stopped due to transformation error.")


if __name__ == "__main__":
    main()