"""
test_transform.py

Unit tests for the utils.transform module.
Tests cover all transformation functions and the full transform_data pipeline.
"""

import pytest
import pandas as pd
import numpy as np
from utils.transform import (
    transform_to_DataFrame,
    transform_price,
    transform_rating,
    transform_colors,
    transform_data,
)


class TestTransformToDataFrame:

    def test_converts_list_of_dicts_to_dataframe(self):
        """Should convert list of dicts to a DataFrame."""
        data = [{"Title": "Shirt", "Price": "$10.00"}]
        result = transform_to_DataFrame(data)
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["Title", "Price"]

    def test_returns_none_on_invalid_input(self):
        """Should return None if input is not valid."""
        result = transform_to_DataFrame("bukan list")
        assert result is None

    def test_empty_list_returns_empty_dataframe(self):
        """Empty list input should produce an empty DataFrame."""
        result = transform_to_DataFrame([])
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestTransformPrice:

    def test_valid_dollar_price(self):
        """Dollar price should be converted to IDR (x16000)."""
        result = transform_price("$120.00")
        assert result == 120.00 * 16000

    def test_unavailable_price_returns_none(self):
        """'Unavailable' price should return None."""
        result = transform_price("Price Unavailable")
        assert result is None

    def test_none_input_returns_none(self):
        """None input should return None."""
        result = transform_price(None)
        assert result is None

    def test_empty_string_returns_none(self):
        """Empty string should return None."""
        result = transform_price("")
        assert result is None

    def test_price_is_float(self):
        """Result should be of type float."""
        result = transform_price("$50.00")
        assert isinstance(result, float)

    def test_price_without_dollar_sign(self):
        """Number without $ sign should also be processed."""
        result = transform_price("50.00")
        assert result == 50.00 * 16000


class TestTransformRating:

    def test_valid_rating_with_star_emoji(self):
        """Format '⭐ 4.5 / 5' should return 4.5."""
        result = transform_rating("⭐ 4.5 / 5")
        assert result == 4.5

    def test_valid_rating_full_format(self):
        """Full format 'Rating: ⭐ 3.9 / 5' should return 3.9."""
        result = transform_rating("Rating: ⭐ 3.9 / 5")
        assert result == 3.9

    def test_invalid_rating_returns_none(self):
        """'Invalid Rating' should return None."""
        result = transform_rating("Rating: ⭐ Invalid Rating / 5")
        assert result is None

    def test_none_input_returns_none(self):
        """None input should return None."""
        result = transform_rating(None)
        assert result is None

    def test_rating_is_float(self):
        """Result should be of type float."""
        result = transform_rating("⭐ 4.0 / 5")
        assert isinstance(result, float)

    def test_rating_integer_value(self):
        """Rating without decimal like '4 / 5' should return 4.0."""
        result = transform_rating("⭐ 4 / 5")
        assert result == 4.0


class TestTransformColors:

    def test_valid_colors_string(self):
        """'3 colors' should return integer 3."""
        result = transform_colors("3 colors")
        assert result == 3

    def test_none_input_returns_zero(self):
        """None input should return 0."""
        result = transform_colors(None)
        assert result == 0

    def test_empty_string_returns_zero(self):
        """Empty string should return 0."""
        result = transform_colors("")
        assert result == 0

    def test_result_is_integer(self):
        """Result should be of type int."""
        result = transform_colors("5 colors")
        assert isinstance(result, int)


class TestTransformData:

    def _make_df(self, rows):
        return pd.DataFrame(rows)

    def test_valid_data_returns_dataframe(self, valid_raw_row):
        """Valid data should return a non-empty DataFrame."""
        df = self._make_df([valid_raw_row])
        result = transform_data(df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_removes_unknown_product(self, valid_raw_row):
        """Rows with Title 'Unknown Product' should be removed."""
        rows = [
            {**valid_raw_row, "Title": "Unknown Product"},
            {**valid_raw_row, "Title": "Real Product"},
        ]
        result = transform_data(self._make_df(rows))
        assert "Unknown Product" not in result["Title"].values

    def test_removes_row_with_invalid_rating(self, valid_raw_row):
        """Rows with invalid rating should be removed."""
        rows = [
            {**valid_raw_row, "Rating": "Rating: ⭐ Invalid Rating / 5"},
            valid_raw_row,
        ]
        result = transform_data(self._make_df(rows))
        assert len(result) == 1

    def test_removes_row_with_unavailable_price(self, valid_raw_row):
        """Rows with unavailable price should be removed."""
        rows = [
            {**valid_raw_row, "Price": "Price Unavailable"},
            valid_raw_row,
        ]
        result = transform_data(self._make_df(rows))
        assert len(result) == 1

    def test_removes_duplicates(self, valid_raw_row):
        """Duplicate rows should be removed."""
        result = transform_data(self._make_df([valid_raw_row] * 3))
        assert len(result) == 1

    def test_price_converted_to_rupiah(self, valid_raw_row):
        """Price column should be converted to IDR."""
        result = transform_data(self._make_df([valid_raw_row]))
        assert result["Price"].iloc[0] == 120.00 * 16000

    def test_size_label_removed(self, valid_raw_row):
        """Size column should not contain 'Size:' prefix."""
        result = transform_data(self._make_df([valid_raw_row]))
        assert result["Size"].iloc[0] == "M"

    def test_gender_label_removed(self, valid_raw_row):
        """Gender column should not contain 'Gender:' prefix."""
        result = transform_data(self._make_df([valid_raw_row]))
        assert result["Gender"].iloc[0] == "Men"

    def test_correct_dtypes(self, valid_raw_row):
        """Column data types should be correct after transformation."""
        result = transform_data(self._make_df([valid_raw_row]))
        assert result["Price"].dtype == np.float64
        assert result["Rating"].dtype == np.float64
        assert result["Colors"].dtype == np.int64

    def test_empty_dataframe_input(self):
        """Empty DataFrame input should not crash."""
        result = transform_data(self._make_df([]))
        assert result is None or isinstance(result, pd.DataFrame)