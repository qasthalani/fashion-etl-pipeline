"""
conftest.py

Shared fixtures and mock data for the ETL pipeline test suite.
Automatically discovered and loaded by pytest for all test modules.
"""

import pytest
import pandas as pd


# ── Mock HTML constants ──────────────────────────────────────

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


# ── Shared fixtures ──────────────────────────────────────────

@pytest.fixture
def sample_df():
    """
    Return a small cleaned DataFrame simulating transform output.
    Used by load tests to avoid re-running the full pipeline.
    """
    return pd.DataFrame([
        {
            "Title": "Casual Linen Shirt",
            "Price": 1920000.0,
            "Rating": 4.5,
            "Colors": 3,
            "Size": "M",
            "Gender": "Men",
            "Timestamp": "2026-05-24T10:00:00.000000",
        },
        {
            "Title": "Slim Fit Chinos",
            "Price": 1360000.0,
            "Rating": 3.8,
            "Colors": 2,
            "Size": "S",
            "Gender": "Unisex",
            "Timestamp": "2026-05-24T10:00:01.000000",
        },
    ])


@pytest.fixture
def valid_raw_row():
    """
    Return a single valid raw product row as scraped (pre-transform).
    Used by transform tests as a base template.
    """
    return {
        "Title": "Casual Shirt",
        "Price": "$120.00",
        "Rating": "Rating: ⭐ 4.5 / 5",
        "Colors": "3 colors",
        "Size": "Size: M",
        "Gender": "Gender: Men",
        "Timestamp": "2026-05-24T10:00:00.000000",
    }