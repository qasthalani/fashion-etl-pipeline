import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, call
from utils.load import load_to_csv, load_to_google_sheets, load_to_postgresql

# Sample DataFrame untuk semua test
@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {
            "Title": "Casual Linen Shirt",
            "Price": 1920000.0,
            "Rating": 4.5,
            "Colors": 3,
            "Size": "M",
            "Gender": "Men",
            "Timestamp": "2026-05-01T10:00:00.000000"
        },
        {
            "Title": "Slim Fit Chinos",
            "Price": 1360000.0,
            "Rating": 3.8,
            "Colors": 2,
            "Size": "S",
            "Gender": "Unisex",
            "Timestamp": "2026-05-01T10:00:01.000000"
        }
    ])

# Test: load_to_csv
class TestLoadToCsv:

    def test_saves_csv_successfully(self, sample_df, tmp_path):
        """Harus menyimpan file CSV dengan benar."""
        file_path = str(tmp_path / "test_products.csv")
        load_to_csv(sample_df, file_name=file_path)

        result = pd.read_csv(file_path)
        assert len(result) == 2
        assert list(result.columns) == ["Title", "Price", "Rating", "Colors", "Size", "Gender", "Timestamp"]

    def test_csv_contains_correct_data(self, sample_df, tmp_path):
        """Data di CSV harus sesuai dengan DataFrame input."""
        file_path = str(tmp_path / "test_products.csv")
        load_to_csv(sample_df, file_name=file_path)

        result = pd.read_csv(file_path)
        assert result['Title'].iloc[0] == "Casual Linen Shirt"
        assert result['Price'].iloc[0] == 1920000.0

    def test_csv_no_index_column(self, sample_df, tmp_path):
        """CSV tidak boleh menyimpan kolom index (0, 1, 2...)."""
        file_path = str(tmp_path / "test_products.csv")
        load_to_csv(sample_df, file_name=file_path)

        result = pd.read_csv(file_path)
        assert 'Unnamed: 0' not in result.columns

    @patch('utils.load.pd.DataFrame.to_csv')
    def test_handles_csv_write_error(self, mock_to_csv, sample_df, capsys):
        """Harus menampilkan pesan error jika gagal menulis CSV."""
        mock_to_csv.side_effect = Exception("Disk full")
        load_to_csv(sample_df, file_name="/invalid/path/test.csv")

        captured = capsys.readouterr()
        assert "Gagal" in captured.out

# Test: load_to_google_sheets
class TestLoadToGoogleSheets:

    @patch('utils.load.gspread.authorize')
    @patch('utils.load.Credentials.from_service_account_file')
    def test_uploads_to_google_sheets_successfully(self, mock_creds, mock_authorize, sample_df, capsys):
        """Harus berhasil upload data ke Google Sheets."""
        mock_sheet = MagicMock()
        mock_client = MagicMock()
        mock_client.open.return_value.get_worksheet.return_value = mock_sheet
        mock_authorize.return_value = mock_client

        load_to_google_sheets(sample_df, "Fashion Products Database", "fake_key.json")

        mock_sheet.clear.assert_called_once()
        mock_sheet.update.assert_called_once()

        captured = capsys.readouterr()
        assert "berhasil" in captured.out

    @patch('utils.load.gspread.authorize')
    @patch('utils.load.Credentials.from_service_account_file')
    def test_uploads_correct_number_of_rows(self, mock_creds, mock_authorize, sample_df):
        """Data yang dikirim ke Sheets harus mencakup header + semua baris data."""
        mock_sheet = MagicMock()
        mock_client = MagicMock()
        mock_client.open.return_value.get_worksheet.return_value = mock_sheet
        mock_authorize.return_value = mock_client

        load_to_google_sheets(sample_df, "Fashion Products Database", "fake_key.json")

        args = mock_sheet.update.call_args[0][0]
        # args[0] = header, args[1:] = data rows
        assert len(args) == 3  # 1 header + 2 data rows

    @patch('utils.load.Credentials.from_service_account_file')
    def test_handles_google_sheets_error(self, mock_creds, sample_df, capsys):
        """Harus menampilkan pesan error jika koneksi Sheets gagal."""
        mock_creds.side_effect = Exception("File not found")

        load_to_google_sheets(sample_df, "Fashion Products Database", "fake_key.json")

        captured = capsys.readouterr()
        assert "Gagal" in captured.out

    @patch('utils.load.gspread.authorize')
    @patch('utils.load.Credentials.from_service_account_file')
    def test_uses_spreadsheet_name_parameter(self, mock_creds, mock_authorize, sample_df):
        """Harus membuka spreadsheet berdasarkan parameter, bukan hardcode."""
        mock_sheet = MagicMock()
        mock_client = MagicMock()
        mock_client.open.return_value.get_worksheet.return_value = mock_sheet
        mock_authorize.return_value = mock_client

        load_to_google_sheets(sample_df, "My Custom Sheet", "fake_key.json")

        mock_client.open.assert_called_with("My Custom Sheet")

# Test: load_to_postgresql
class TestLoadToPostgresql:

    @patch('utils.load.create_engine')
    def test_saves_to_postgresql_successfully(self, mock_engine, sample_df, capsys):
        """Harus berhasil menyimpan data ke PostgreSQL."""
        mock_eng = MagicMock()
        mock_engine.return_value = mock_eng

        with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
            load_to_postgresql(sample_df, "postgresql://developer:pass123@localhost:5432/fashiondb")
            mock_to_sql.assert_called_once_with('products', mock_eng, if_exists='replace', index=False)

        captured = capsys.readouterr()
        assert "berhasil" in captured.out

    @patch('utils.load.create_engine')
    def test_uses_db_config_parameter(self, mock_create_engine, sample_df):
        """Harus menggunakan db_config dari parameter, bukan hardcode."""
        custom_url = "postgresql://user:pass@remotehost:5432/mydb"
        mock_eng = MagicMock()
        mock_create_engine.return_value = mock_eng

        with patch.object(pd.DataFrame, 'to_sql'):
            load_to_postgresql(sample_df, custom_url)

        mock_create_engine.assert_called_with(custom_url)

    @patch('utils.load.create_engine')
    def test_handles_postgresql_connection_error(self, mock_create_engine, sample_df, capsys):
        """Harus menampilkan pesan error jika koneksi PostgreSQL gagal."""
        mock_create_engine.side_effect = Exception("Connection refused")

        load_to_postgresql(sample_df, "postgresql://developer:pass123@localhost:5432/fashiondb")

        captured = capsys.readouterr()
        assert "Gagal" in captured.out