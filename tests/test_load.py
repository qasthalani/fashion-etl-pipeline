"""
test_load.py

Unit tests for the utils.load module.
Tests cover load_to_csv, load_to_google_sheets, and load_to_postgresql functions.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from utils.load import load_to_csv, load_to_google_sheets, load_to_postgresql


class TestLoadToCsv:

    def test_saves_csv_successfully(self, sample_df, tmp_path):
        """Should save CSV file correctly."""
        file_path = str(tmp_path / "test_products.csv")
        load_to_csv(sample_df, file_name=file_path)

        result = pd.read_csv(file_path)
        assert len(result) == 2
        assert list(result.columns) == ["Title", "Price", "Rating", "Colors", "Size", "Gender", "Timestamp"]

    def test_csv_contains_correct_data(self, sample_df, tmp_path):
        """Data in CSV should match the input DataFrame."""
        file_path = str(tmp_path / "test_products.csv")
        load_to_csv(sample_df, file_name=file_path)

        result = pd.read_csv(file_path)
        assert result["Title"].iloc[0] == "Casual Linen Shirt"
        assert result["Price"].iloc[0] == 1920000.0

    def test_csv_no_index_column(self, sample_df, tmp_path):
        """CSV should not contain an index column."""
        file_path = str(tmp_path / "test_products.csv")
        load_to_csv(sample_df, file_name=file_path)

        result = pd.read_csv(file_path)
        assert "Unnamed: 0" not in result.columns

    @patch("utils.load.pd.DataFrame.to_csv")
    # test 1
    def test_handles_csv_write_error(self, mock_to_csv, sample_df, caplog):
        """Should log error message if CSV write fails."""
        mock_to_csv.side_effect = Exception("Disk full")
        
        with caplog.at_level("ERROR"):
            load_to_csv(sample_df, file_name="/invalid/path/test.csv")
            
        assert "Failed" in caplog.text


class TestLoadToGoogleSheets:

    @patch("utils.load.gspread.authorize")
    @patch("utils.load.Credentials.from_service_account_file")
    def test_uploads_to_google_sheets_successfully(self, mock_creds, mock_authorize, sample_df, capsys):
        """Should successfully upload data to Google Sheets."""
        mock_sheet = MagicMock()
        mock_client = MagicMock()
        mock_client.open.return_value.get_worksheet.return_value = mock_sheet
        mock_authorize.return_value = mock_client

        load_to_google_sheets(sample_df, "Fashion Products Database", "fake_key.json")

        mock_sheet.clear.assert_called_once()
        mock_sheet.update.assert_called_once()

    @patch("utils.load.gspread.authorize")
    @patch("utils.load.Credentials.from_service_account_file")
    def test_uploads_correct_number_of_rows(self, mock_creds, mock_authorize, sample_df):
        """Data sent to Sheets should include header + all data rows."""
        mock_sheet = MagicMock()
        mock_client = MagicMock()
        mock_client.open.return_value.get_worksheet.return_value = mock_sheet
        mock_authorize.return_value = mock_client

        load_to_google_sheets(sample_df, "Fashion Products Database", "fake_key.json")

        args = mock_sheet.update.call_args[0][0]
        assert len(args) == 3  # 1 header + 2 data rows

    @patch("utils.load.Credentials.from_service_account_file")
    def test_handles_google_sheets_error(self, mock_creds, sample_df, caplog):
        """Should log error message if Sheets connection fails."""
        mock_creds.side_effect = Exception("File not found")
        
        with caplog.at_level("ERROR"):
            load_to_google_sheets(sample_df, "Fashion Products Database", "fake_key.json")
            
        assert "Failed" in caplog.text

    @patch("utils.load.gspread.authorize")
    @patch("utils.load.Credentials.from_service_account_file")
    def test_uses_spreadsheet_name_parameter(self, mock_creds, mock_authorize, sample_df):
        """Should open spreadsheet based on parameter, not hardcoded."""
        mock_sheet = MagicMock()
        mock_client = MagicMock()
        mock_client.open.return_value.get_worksheet.return_value = mock_sheet
        mock_authorize.return_value = mock_client

        load_to_google_sheets(sample_df, "My Custom Sheet", "fake_key.json")

        mock_client.open.assert_called_with("My Custom Sheet")


class TestLoadToPostgresql:

    @patch("utils.load.create_engine")
    def test_saves_to_postgresql_successfully(self, mock_engine, sample_df, capsys):
        """Should successfully save data to PostgreSQL."""
        mock_eng = MagicMock()
        mock_engine.return_value = mock_eng

        with patch.object(pd.DataFrame, "to_sql") as mock_to_sql:
            load_to_postgresql(sample_df, "postgresql://developer:pass123@localhost:5432/fashiondb")
            mock_to_sql.assert_called_once_with("products", mock_eng, if_exists="replace", index=False)

    @patch("utils.load.create_engine")
    def test_uses_db_config_parameter(self, mock_create_engine, sample_df):
        """Should use db_config from parameter, not hardcoded."""
        custom_url = "postgresql://user:pass@remotehost:5432/mydb"
        mock_eng = MagicMock()
        mock_create_engine.return_value = mock_eng

        with patch.object(pd.DataFrame, "to_sql"):
            load_to_postgresql(sample_df, custom_url)

        mock_create_engine.assert_called_with(custom_url)

    @patch("utils.load.create_engine")
    def test_handles_postgresql_connection_error(self, mock_create_engine, sample_df, caplog):
        """Should log error message if PostgreSQL connection fails."""
        mock_create_engine.side_effect = Exception("Connection refused")
        
        with caplog.at_level("ERROR"):
            load_to_postgresql(sample_df, "postgresql://developer:pass123@localhost:5432/fashiondb")
            
        assert "Failed" in caplog.text