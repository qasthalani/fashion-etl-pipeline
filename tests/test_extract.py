import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from utils.extract import fetching_content, extract_data, scrape_website

# HTML palsu yang meniru struktur website asli
MOCK_ARTICLE_HTML = """
<div class="collection-card">
    <h3 class="product-title">Casual Linen Shirt</h3>
    <span class="price">$120.00</span>
    <p>Rating: ⭐ 4.5 / 5</p>
    <p>Colors: 3 colors</p>
    <p>Size: M</p>
    <p>Gender: Men</p>
</div>
"""

MOCK_ARTICLE_INVALID_HTML = """
<div class="collection-card">
    <h3 class="product-title">Unknown Product</h3>
    <span class="price">Price Unavailable</span>
    <p>Rating: ⭐ Invalid Rating / 5</p>
    <p>Colors: </p>
    <p>Size: L</p>
    <p>Gender: Women</p>
</div>
"""

MOCK_PAGE_HTML = """
<html><body>
    <div class="collection-card">
        <h3 class="product-title">Casual Linen Shirt</h3>
        <span class="price">$120.00</span>
        <p>Rating: ⭐ 4.5 / 5</p>
        <p>Colors: 3 colors</p>
        <p>Size: M</p>
        <p>Gender: Men</p>
    </div>
    <ul class="pagination"><li class="next"><a>Next</a></li></ul>
</body></html>
"""

MOCK_PAGE_LAST_HTML = """
<html><body>
    <div class="collection-card">
        <h3 class="product-title">Slim Fit Chinos</h3>
        <span class="price">$85.00</span>
        <p>Rating: ⭐ 3.8 / 5</p>
        <p>Colors: 2 colors</p>
        <p>Size: S</p>
        <p>Gender: Unisex</p>
    </div>
</body></html>
"""

# Test: fetching_content
class TestFetchingContent:

    @patch('utils.extract.requests.get')
    def test_fetching_content_success(self, mock_get):
        """Harus mengembalikan HTML string jika request berhasil."""
        mock_response = MagicMock()
        mock_response.text = "<html>OK</html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetching_content("https://fashion-studio.dicoding.dev/")

        assert result == "<html>OK</html>"

    @patch('utils.extract.requests.get')
    def test_fetching_content_request_exception(self, mock_get):
        """Harus mengembalikan None jika terjadi error koneksi."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        result = fetching_content("https://invalid-url.com/")

        assert result is None

# Test: extract_data
class TestExtractData:

    def _make_article(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find('div', class_='collection-card')

    def test_extract_data_valid_article(self):
        """Harus mengekstrak semua field dengan benar dari artikel valid."""
        article = self._make_article(MOCK_ARTICLE_HTML)
        result = extract_data(article)

        assert result is not None
        assert result['Title'] == 'Casual Linen Shirt'
        assert result['Price'] == '$120.00'
        assert '4.5' in result['Rating']
        assert result['Size'] == 'M'
        assert result['Gender'] == 'Men'
        assert result['Timestamp'] is not None

    def test_extract_data_missing_title(self):
        """Harus mengisi 'Unknown Product' jika tag title tidak ditemukan."""
        html = """
        <div class="collection-card">
            <span class="price">$50.00</span>
            <p>Rating: ⭐ 4.0 / 5</p>
        </div>
        """
        article = self._make_article(html)
        result = extract_data(article)

        assert result['Title'] == 'Unknown Product'

    def test_extract_data_missing_price(self):
        """Harus mengisi None jika price tag tidak ditemukan."""
        html = """
        <div class="collection-card">
            <h3 class="product-title">Some Product</h3>
            <p>Rating: ⭐ 4.0 / 5</p>
        </div>
        """
        article = self._make_article(html)
        result = extract_data(article)

        assert result['Price'] is None

    def test_extract_data_returns_dict_with_required_keys(self):
        """Hasil extract harus memiliki 7 key yang diharapkan."""
        article = self._make_article(MOCK_ARTICLE_HTML)
        result = extract_data(article)

        expected_keys = {'Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender', 'Timestamp'}
        assert expected_keys == set(result.keys())

    def test_extract_data_timestamp_format(self):
        """Timestamp harus mengikuti format ISO 8601."""
        import re
        article = self._make_article(MOCK_ARTICLE_HTML)
        result = extract_data(article)

        pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+'
        assert re.match(pattern, result['Timestamp'])

# Test: scrape_website
class TestScrapeWebsite:

    @patch('utils.extract.time.sleep')
    @patch('utils.extract.fetching_content')
    def test_scrape_website_stops_at_last_page(self, mock_fetch, mock_sleep):
        """Scraping harus berhenti saat tombol Next tidak ditemukan."""
        # Halaman 1 ada tombol Next, halaman 2 tidak
        mock_fetch.side_effect = [MOCK_PAGE_HTML, MOCK_PAGE_LAST_HTML]

        result = scrape_website("https://fashion-studio.dicoding.dev/", start_page=1, delay=0)

        assert len(result) == 2  # 1 produk per halaman
        assert result[0]['Title'] == 'Casual Linen Shirt'
        assert result[1]['Title'] == 'Slim Fit Chinos'

    @patch('utils.extract.fetching_content')
    def test_scrape_website_returns_empty_on_failed_fetch(self, mock_fetch):
        """Harus mengembalikan list kosong jika fetch pertama gagal."""
        mock_fetch.return_value = None

        result = scrape_website("https://fashion-studio.dicoding.dev/", start_page=1, delay=0)

        assert result == []

    @patch('utils.extract.time.sleep')
    @patch('utils.extract.fetching_content')
    def test_scrape_website_returns_list(self, mock_fetch, mock_sleep):
        """Return value harus berupa list."""
        mock_fetch.return_value = MOCK_PAGE_LAST_HTML

        result = scrape_website("https://fashion-studio.dicoding.dev/", start_page=1, delay=0)

        assert isinstance(result, list)