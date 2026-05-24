"""
extract.py

This module handles the Extract stage of the ETL pipeline.
It is responsible for fetching and parsing product data from
the Fashion Studio website (https://fashion-studio.dicoding.dev/).
"""

import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from utils.logger import get_logger

logger = get_logger(__name__)


def fetching_content(url: str) -> str | None:
    """
    Fetch the HTML content of a given URL.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the page as a string.
        None: If the request fails due to a connection error or timeout.

    Raises:
        requests.exceptions.RequestException: Caught internally;
            returns None on failure.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.warning("Failed to fetch URL %s: %s", url, e)
        return None


def extract_data(article) -> dict | None:
    """
    Extract product data from a single HTML article element.

    Parses a BeautifulSoup element representing one product card
    and extracts the following fields:
        - Title: Product name (defaults to 'Unknown Product' if missing)
        - Price: Raw price string (e.g., '$120.00'), or None if missing
        - Rating: Raw rating string (e.g., '⭐ 4.5 / 5')
        - Colors: Number of available colors (e.g., '3 colors')
        - Size: Available size (e.g., 'M', 'L')
        - Gender: Target gender (e.g., 'Men', 'Women', 'Unisex')
        - Timestamp: ISO 8601 extraction timestamp

    Args:
        article (bs4.element.Tag): A BeautifulSoup Tag representing
            a single product card element.

    Returns:
        dict: A dictionary containing the 7 extracted fields.
        None: If an unexpected parsing error occurs.
    """
    try:
        title_tag = article.find("h3", class_="product-title")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"

        price_tag = article.find("span", class_="price") or article.find(
            "p", class_="price"
        )
        price = price_tag.get_text(strip=True) if price_tag else None

        details = {}
        for p in article.find_all("p"):
            text = p.get_text(strip=True)
            if ":" in text:
                key, value = text.split(":", 1)
                details[key.strip()] = value.strip()
            elif re.search(r"\d+\s*Colors", text, re.IGNORECASE):
                details["Colors"] = text

        return {
            "Title": title,
            "Price": price,
            "Rating": details.get("Rating", None),
            "Colors": details.get("Colors", None),
            "Size": details.get("Size", None),
            "Gender": details.get("Gender", None),
            "Timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
        }

    except Exception as e:
        logger.error("Error parsing article: %s", e)
        return None


def scrape_website(
    base_url: str, start_page: int = 1, delay: int = 2
) -> list[dict]:
    """
    Scrape all product data from the Fashion Studio website.

    Iterates through paginated product pages starting from `start_page`,
    extracting all product cards on each page. Stops when the 'Next'
    pagination button is no longer found or when the page limit (50)
    is reached.

    Args:
        base_url (str): The base URL of the website to scrape.
        start_page (int): The page number to start scraping from. Defaults to 1.
        delay (int): Number of seconds to wait between page requests
            to avoid overwhelming the server. Defaults to 2.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains
            the extracted data for one product. Returns an empty list
            if the first page fails to load.
    """
    all_data = []
    page_number = start_page

    try:
        while page_number <= 50:
            url = base_url if page_number == 1 else f"{base_url}page{page_number}"
            content = fetching_content(url)

            if not content:
                logger.warning("Failed to load content on page %d", page_number)
                break

            soup = BeautifulSoup(content, "html.parser")
            articles = soup.find_all("div", class_="collection-card")

            if not articles:
                logger.warning("No articles found on page %d", page_number)
                break

            for article in articles:
                data = extract_data(article)
                if data:
                    all_data.append(data)

            logger.info(
                "Successfully extracted page %d. Total records: %d",
                page_number,
                len(all_data),
            )

            next_button = soup.find("li", class_="next")
            if not next_button:
                logger.info("Next button not found. Scraping complete.")
                break

            page_number += 1
            time.sleep(delay)

    except Exception as e:
        logger.error("Unexpected error occurred: %s", e)

    return all_data