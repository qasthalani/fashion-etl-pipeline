"""
load.py

This module handles the Load stage of the ETL pipeline.
It saves the cleaned product DataFrame to three destinations:
    - CSV file (local)
    - Google Sheets (via gspread)
    - PostgreSQL database (via SQLAlchemy)
"""

import os
import pandas as pd
import numpy as np
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from sqlalchemy import create_engine
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


def load_to_csv(df: pd.DataFrame, file_name: str = "products.csv") -> None:
    """
    Save the DataFrame to a local CSV file.

    Args:
        df (pd.DataFrame): The cleaned DataFrame to save.
        file_name (str): The output file path. Defaults to 'products.csv'.

    Returns:
        None
    """
    try:
        df.to_csv(file_name, index=False)
        logger.info("Data successfully saved to %s", file_name)
    except Exception as e:
        logger.error("Failed to save CSV: %s", e)


def load_to_google_sheets(
    df: pd.DataFrame,
    spreadsheet_name: str | None = None,
    json_keyfile: str | None = None,
) -> None:
    """
    Upload the DataFrame to a Google Sheets spreadsheet.

    Clears the first worksheet and replaces its content with
    the DataFrame's headers and rows. Handles numpy type conversion
    to ensure compatibility with the Sheets API.

    Args:
        df (pd.DataFrame): The cleaned DataFrame to upload.
        spreadsheet_name (str | None): The name of the target Google Sheets file.
            Falls back to the SPREADSHEET_NAME environment variable if not provided.
        json_keyfile (str | None): Path to the Google Service Account JSON key file.
            Falls back to the JSON_KEY_PATH environment variable if not provided.

    Returns:
        None
    """
    try:
        spreadsheet_name = spreadsheet_name or os.getenv("SPREADSHEET_NAME")
        json_keyfile = json_keyfile or os.getenv("JSON_KEY_PATH")

        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_file(
            json_keyfile, scopes=scope
        )
        client = gspread.authorize(credentials)
        sheet = client.open(spreadsheet_name).get_worksheet(0)
        sheet.clear()

        def safe_value(v):
            if isinstance(v, np.integer):
                return int(v)
            elif isinstance(v, np.floating):
                return None if np.isnan(v) else float(v)
            elif isinstance(v, float) and np.isnan(v):
                return None
            return v

        headers = df.columns.values.tolist()
        rows = [[safe_value(v) for v in row] for row in df.values.tolist()]

        sheet.update([headers] + rows)
        logger.info(
            "Data successfully uploaded to Google Sheets: %s", spreadsheet_name
        )
    except Exception as e:
        logger.error("Failed to upload to Google Sheets: %s", e)


def load_to_postgresql(
    df: pd.DataFrame,
    db_config: str | None = None,
) -> None:
    """
    Save the DataFrame to a PostgreSQL database table.

    Connects to the database using SQLAlchemy and writes the DataFrame
    to a table named 'products'. Replaces the table if it already exists.

    Args:
        df (pd.DataFrame): The cleaned DataFrame to save.
        db_config (str | None): A SQLAlchemy-compatible database URL.
            Falls back to the DB_URL environment variable if not provided.

    Returns:
        None
    """
    try:
        db_config = db_config or os.getenv("DB_URL")
        engine = create_engine(db_config)
        df.to_sql("products", engine, if_exists="replace", index=False)
        logger.info("Data successfully saved to PostgreSQL")
    except Exception as e:
        logger.error("Failed to save to PostgreSQL: %s", e)