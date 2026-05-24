"""
transform.py

This module handles the Transform stage of the ETL pipeline.
It cleans, converts, and validates raw product data extracted
from the Fashion Studio website, preparing it for loading.
"""

import re
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)


def transform_to_DataFrame(data) -> pd.DataFrame | None:
    """
    Convert a list of dictionaries into a pandas DataFrame.

    Args:
        data (list[dict]): A list of product dictionaries from the extract stage.

    Returns:
        pd.DataFrame: A DataFrame constructed from the input list.
        None: If the input is not a list or conversion fails.
    """
    try:
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        logger.error("Error converting data to DataFrame: %s", e)
        return None


def transform_price(price_str: str | None) -> float | None:
    """
    Convert a raw price string to Indonesian Rupiah (IDR).

    Strips the '$' symbol and any non-numeric characters, then
    multiplies the USD value by a fixed exchange rate of 16,000.

    Args:
        price_str (str | None): The raw price string (e.g., '$120.00',
            'Price Unavailable', or None).

    Returns:
        float: The price converted to IDR (e.g., 1,920,000.0).
        None: If the input is None, empty, or contains 'Unavailable'.
    """
    try:
        if not price_str or "Unavailable" in str(price_str):
            return None

        clean_price = "".join(
            filter(lambda x: x.isdigit() or x == ".", str(price_str))
        )
        if not clean_price:
            return None

        return float(clean_price) * 16000
    except Exception:
        return None


def transform_rating(rating_str: str | None) -> float | None:
    """
    Extract a numeric rating value from a raw rating string.

    Supports formats such as:
        - '⭐ 4.5 / 5'
        - 'Rating: ⭐ 3.9 / 5'
        - '4 / 5'

    Args:
        rating_str (str | None): The raw rating string, or None.

    Returns:
        float: The extracted rating value (e.g., 4.5).
        None: If the input is None, empty, or contains 'Invalid'.
    """
    try:
        if not rating_str or "Invalid" in str(rating_str):
            return None

        match = re.search(r"(\d+(?:\.\d+)?)\s*/", str(rating_str))
        if match:
            return float(match.group(1))

        numbers = re.findall(r"\d+(?:\.\d+)?", str(rating_str))
        if numbers:
            return float(numbers[0])

        return None
    except Exception:
        return None


def transform_colors(color_str: str | None) -> int:
    """
    Extract the number of available colors from a raw color string.

    Args:
        color_str (str | None): The raw color string (e.g., '3 colors'),
            or None.

    Returns:
        int: The number of colors as an integer (e.g., 3).
            Returns 0 if the input is None, empty, or cannot be parsed.
    """
    try:
        if not color_str:
            return 0
        return int("".join(filter(str.isdigit, str(color_str))))
    except Exception:
        return 0


def transform_data(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Clean and validate the raw product DataFrame.

    Applies the following transformation steps in order:
        1. Remove duplicate rows based on all key product fields
        2. Remove rows where Title is 'Unknown Product'
        3. Convert Price from USD string to IDR float (x16,000)
        4. Extract numeric Rating from raw string
        5. Extract integer Colors count from raw string
        6. Strip 'Size:' and 'Gender:' label prefixes
        7. Drop rows with missing Title, Price, or Rating
        8. Cast columns to correct data types

    Args:
        df (pd.DataFrame): The raw DataFrame from transform_to_DataFrame().

    Returns:
        pd.DataFrame: A cleaned DataFrame ready for the load stage.
        None: If the input DataFrame is empty or an error occurs.
    """
    try:
        df = df.copy()

        df = df.drop_duplicates(
            subset=["Title", "Price", "Rating", "Colors", "Size", "Gender"]
        )
        df = df[df["Title"] != "Unknown Product"]

        df["Price"] = df["Price"].apply(transform_price)
        df["Rating"] = df["Rating"].apply(transform_rating)
        df["Colors"] = df["Colors"].apply(transform_colors)

        df["Size"] = df["Size"].str.replace("Size:", "", regex=False).str.strip()
        df["Gender"] = df["Gender"].str.replace("Gender:", "", regex=False).str.strip()

        df = df.dropna(subset=["Title", "Price", "Rating"])

        df["Colors"] = df["Colors"].astype("int64")
        df["Price"] = df["Price"].astype("float64")
        df["Rating"] = df["Rating"].astype("float64")

        logger.info("Transformation complete. Total valid rows: %d", len(df))
        return df
    except Exception as e:
        logger.error("Error in Transformation: %s", e)
        return None