import pytest
from pytest_mock import MockerFixture

from src.domains.ingest.extract import ExtractData


def test_github_connection(mocker: MockerFixture):
    """"""
    
    mock_settings_func = mocker.patch("src.domains.ingest.extract.get_settings")
    
    mock_settings_func.return_value.GITHUB_TOKEN = "fake_token_123"
    mock_settings_func.return_value.IGNORE_REPOS = []

    mock_github_class = mocker.patch("src.domains.ingest.extract.Github")
    mock_instance = mock_github_class.return_value
    mock_instance.get_user.return_value = "FakeUser"

    extractor = ExtractData()
    user = extractor.get_github_info()

    mock_github_class.assert_called_once_with("fake_token_123")
    assert user == "FakeUser"

def test_extract_pdf_text(mocker: MockerFixture):
    """"""

    mock_settings_func = mocker.patch("src.domains.ingest.extract.get_settings")
    mock_settings_func.return_value.GITHUB_TOKEN = "fake_token"

    mock_fitz = mocker.patch("src.domains.ingest.extract.fitz")
    mock_doc = mocker.MagicMock()
    mock_page = mocker.MagicMock()
    
    mock_page.get_text.return_value = "Page Content"
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz.open.return_value = mock_doc

    extractor = ExtractData()
    texto = extractor.get_pdf_text()

    assert "Page Content" in texto

def test_pdf_extract_error(mocker: MockerFixture):
    """"""
    
    mock_settings_func = mocker.patch("src.domains.ingest.extract.get_settings")
    mock_settings_func.return_value.GITHUB_TOKEN = "fake_token"

    mocker.patch("src.domains.ingest.extract.fitz.open", side_effect = Exception("Corrupted File"))
    
    extractor = ExtractData()
    texto = extractor.get_pdf_text()
    
    assert texto == ""