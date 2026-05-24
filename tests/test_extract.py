"""
test_extract.py

Unit tests for the utils.extract module.
"""

import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from utils.extract import fetching_content, extract_data, scrape_website
from tests.conftest import MOCK_PAGE_HTML, MOCK_PAGE_LAST_HTML, MOCK_ARTICLE_HTML


class TestFetchingContent:

    @patch("utils.extract.requests.get")
    def test_fetching_content_success(self, mock_get):
        """Should return HTML string if request succeeds."""
        mock_response = MagicMock()
        mock_response.text = "<html>OK</html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetching_content("https://fashion-studio.dicoding.dev/")

        assert result == "<html>OK</html>"

    @patch("utils.extract.requests.get")
    def test_fetching_content_request_exception(self, mock_get):
        """Should return None if a connection error occurs."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        result = fetching_content("https://invalid-url.com/")

        assert result is None


class TestExtractData:

    def _make_article(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup.find("div", class_="collection-card")

    def test_extract_data_valid_article(self):
        """Should correctly extract all fields from a valid article."""
        article = self._make_article(MOCK_ARTICLE_HTML)
        result = extract_data(article)

        assert result is not None
        assert result["Title"] == "Casual Linen Shirt"
        assert result["Price"] == "$120.00"
        assert "4.5" in result["Rating"]
        assert result["Size"] == "M"
        assert result["Gender"] == "Men"
        assert result["Timestamp"] is not None

    def test_extract_data_missing_title(self):
        """Should fill 'Unknown Product' if title tag is not found."""
        html = """
        <div class="collection-card">
            <span class="price">$50.00</span>
            <p>Rating: ⭐ 4.0 / 5</p>
        </div>
        """
        article = self._make_article(html)
        result = extract_data(article)
        assert result["Title"] == "Unknown Product"

    def test_extract_data_missing_price(self):
        """Should return None for price if price tag is not found."""
        html = """
        <div class="collection-card">
            <h3 class="product-title">Some Product</h3>
            <p>Rating: ⭐ 4.0 / 5</p>
        </div>
        """
        article = self._make_article(html)
        result = extract_data(article)
        assert result["Price"] is None

    def test_extract_data_returns_dict_with_required_keys(self):
        """Result should contain exactly 7 expected keys."""
        article = self._make_article(MOCK_ARTICLE_HTML)
        result = extract_data(article)
        expected_keys = {"Title", "Price", "Rating", "Colors", "Size", "Gender", "Timestamp"}
        assert expected_keys == set(result.keys())

    def test_extract_data_timestamp_format(self):
        """Timestamp should follow ISO 8601 format."""
        import re
        article = self._make_article(MOCK_ARTICLE_HTML)
        result = extract_data(article)
        pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+"
        assert re.match(pattern, result["Timestamp"])


class TestScrapeWebsite:

    @patch("utils.extract.time.sleep")
    @patch("utils.extract.fetching_content")
    def test_scrape_website_stops_at_last_page(self, mock_fetch, mock_sleep):
        """Scraping should stop when Next button is not found."""
        mock_fetch.side_effect = [MOCK_PAGE_HTML, MOCK_PAGE_LAST_HTML]
        result = scrape_website(
            "https://fashion-studio.dicoding.dev/", start_page=1, delay=0
        )

        assert len(result) == 2
        assert result[0]["Title"] == "Casual Linen Shirt"
        assert result[1]["Title"] == "Slim Fit Chinos"

    @patch("utils.extract.fetching_content")
    def test_scrape_website_returns_empty_on_failed_fetch(self, mock_fetch):
        """Should return empty list if first fetch fails."""
        mock_fetch.return_value = None
        result = scrape_website(
            "https://fashion-studio.dicoding.dev/", start_page=1, delay=0
        )
        assert result == []

    @patch("utils.extract.time.sleep")
    @patch("utils.extract.fetching_content")
    def test_scrape_website_returns_list(self, mock_fetch, mock_sleep):
        """Return value should be a list."""
        mock_fetch.return_value = MOCK_PAGE_LAST_HTML
        result = scrape_website(
            "https://fashion-studio.dicoding.dev/", start_page=1, delay=0
        )
        assert isinstance(result, list)