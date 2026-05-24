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

# Test: transform_to_DataFrame
class TestTransformToDataFrame:

    def test_converts_list_of_dicts_to_dataframe(self):
        """mengubah list of dict menjadi DataFrame."""
        data = [{"Title": "Shirt", "Price": "$10.00"}]
        result = transform_to_DataFrame(data)

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["Title", "Price"]

    def test_returns_none_on_invalid_input(self):
        """mengembalikan None jika input tidak valid."""
        result = transform_to_DataFrame("bukan list")

        assert result is None

    def test_empty_list_returns_empty_dataframe(self):
        """Input list kosong harus menghasilkan DataFrame kosong."""
        result = transform_to_DataFrame([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

# Test: transform_price
class TestTransformPrice:

    def test_valid_dollar_price(self):
        """Harga dalam dollar harus dikonversi ke Rupiah (x16000)."""
        result = transform_price("$120.00")
        assert result == 120.00 * 16000

    def test_unavailable_price_returns_none(self):
        """Harga 'Unavailable' harus menghasilkan None."""
        result = transform_price("Price Unavailable")
        assert result is None

    def test_none_input_returns_none(self):
        """Input None harus menghasilkan None."""
        result = transform_price(None)
        assert result is None

    def test_empty_string_returns_none(self):
        """String kosong harus menghasilkan None."""
        result = transform_price("")
        assert result is None

    def test_price_is_float(self):
        """Hasil harus bertipe float."""
        result = transform_price("$50.00")
        assert isinstance(result, float)

    def test_price_without_dollar_sign(self):
        """Angka tanpa tanda $ juga harus bisa diproses."""
        result = transform_price("50.00")
        assert result == 50.00 * 16000

# Test: transform_rating
class TestTransformRating:

    def test_valid_rating_with_star_emoji(self):
        """Format '⭐ 4.5 / 5' harus menghasilkan 4.5."""
        result = transform_rating("⭐ 4.5 / 5")
        assert result == 4.5

    def test_valid_rating_full_format(self):
        """Format penuh 'Rating: ⭐ 3.9 / 5' harus menghasilkan 3.9."""
        result = transform_rating("Rating: ⭐ 3.9 / 5")
        assert result == 3.9

    def test_invalid_rating_returns_none(self):
        """Rating 'Invalid Rating' harus menghasilkan None."""
        result = transform_rating("Rating: ⭐ Invalid Rating / 5")
        assert result is None

    def test_none_input_returns_none(self):
        """Input None harus menghasilkan None."""
        result = transform_rating(None)
        assert result is None

    def test_rating_is_float(self):
        """Hasil harus bertipe float."""
        result = transform_rating("⭐ 4.0 / 5")
        assert isinstance(result, float)

    def test_rating_integer_value(self):
        """Rating tanpa desimal seperti '4 / 5' harus menghasilkan 4.0."""
        result = transform_rating("⭐ 4 / 5")
        assert result == 4.0

# Test: transform_colors
class TestTransformColors:

    def test_valid_colors_string(self):
        """'3 colors' harus menghasilkan integer 3."""
        result = transform_colors("3 colors")
        assert result == 3

    def test_none_input_returns_zero(self):
        """Input None harus menghasilkan 0."""
        result = transform_colors(None)
        assert result == 0

    def test_empty_string_returns_zero(self):
        """String kosong harus menghasilkan 0."""
        result = transform_colors("")
        assert result == 0

    def test_result_is_integer(self):
        """Hasil harus bertipe int."""
        result = transform_colors("5 colors")
        assert isinstance(result, int)

# Test: transform_data 
class TestTransformData:

    def _make_df(self, rows):
        return pd.DataFrame(rows)

    def _valid_row(self, **kwargs):
        row = {
            "Title": "Casual Shirt",
            "Price": "$120.00",
            "Rating": "Rating: ⭐ 4.5 / 5",
            "Colors": "3 colors",
            "Size": "Size: M",
            "Gender": "Gender: Men",
            "Timestamp": "2026-05-01T10:00:00.000000"
        }
        row.update(kwargs)
        return row

    def test_valid_data_returns_dataframe(self):
        """Data valid harus menghasilkan DataFrame yang tidak kosong."""
        df = self._make_df([self._valid_row()])
        result = transform_data(df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_removes_unknown_product(self):
        """Baris dengan Title 'Unknown Product' harus dihapus."""
        df = self._make_df([
            self._valid_row(Title="Unknown Product"),
            self._valid_row(Title="Real Product"),
        ])
        result = transform_data(df)

        assert "Unknown Product" not in result['Title'].values

    def test_removes_row_with_invalid_rating(self):
        """Baris dengan rating 'Invalid' harus dihapus karena Rating jadi None."""
        df = self._make_df([
            self._valid_row(Rating="Rating: ⭐ Invalid Rating / 5"),
            self._valid_row(),
        ])
        result = transform_data(df)

        assert len(result) == 1

    def test_removes_row_with_unavailable_price(self):
        """Baris dengan Price 'Unavailable' harus dihapus."""
        df = self._make_df([
            self._valid_row(Price="Price Unavailable"),
            self._valid_row(),
        ])
        result = transform_data(df)

        assert len(result) == 1

    def test_removes_duplicates(self):
        """Baris duplikat harus dihapus."""
        row = self._valid_row()
        df = self._make_df([row, row, row])
        result = transform_data(df)

        assert len(result) == 1

    def test_price_converted_to_rupiah(self):
        """Kolom Price harus sudah dikonversi ke Rupiah."""
        df = self._make_df([self._valid_row(Price="$120.00")])
        result = transform_data(df)

        assert result['Price'].iloc[0] == 120.00 * 16000

    def test_size_label_removed(self):
        """Kolom Size tidak boleh mengandung prefix 'Size:'."""
        df = self._make_df([self._valid_row(Size="Size: M")])
        result = transform_data(df)

        assert result['Size'].iloc[0] == 'M'

    def test_gender_label_removed(self):
        """Kolom Gender tidak boleh mengandung prefix 'Gender:'."""
        df = self._make_df([self._valid_row(Gender="Gender: Men")])
        result = transform_data(df)

        assert result['Gender'].iloc[0] == 'Men'

    def test_correct_dtypes(self):
        """Tipe data kolom harus sesuai setelah transformasi."""
        df = self._make_df([self._valid_row()])
        result = transform_data(df)

        assert result['Price'].dtype == np.float64
        assert result['Rating'].dtype == np.float64
        assert result['Colors'].dtype == np.int64

    def test_empty_dataframe_input(self):
        """Input DataFrame kosong tidak boleh crash, kembalikan None atau df kosong."""
        df = self._make_df([])
        result = transform_data(df)

        assert result is None or isinstance(result, pd.DataFrame)