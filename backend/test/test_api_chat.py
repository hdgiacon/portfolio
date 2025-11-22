import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from src.domains.chat.service import get_chat_service
from src import main


@pytest.fixture(autouse = True)
def setup_env(monkeypatch: pytest.MonkeyPatch):
    """"""

    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    monkeypatch.setenv("IGNORE_REPOS", "[]")
    monkeypatch.setenv("GROQ_API_KEY", "fake_groq_key")
    
    monkeypatch.setenv("SENTENSE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2") 
    monkeypatch.setenv("GROK_MODEL", "llama-3.3-70b-versatile")


@pytest.fixture
def client(mocker: MockerFixture):
    """"""

    mocker.patch.object(main, "run_full_ingest_pipeline")
    mocker.patch("os.path.exists", return_value = True)

    with TestClient(main.app) as c:
        yield c


def test_success_chat_endpoint(client, mocker: MockerFixture):
    """"""

    mock_service = mocker.AsyncMock()
    mock_service.get_response.return_value = "AI mocked answer"
    
    main.app.dependency_overrides[get_chat_service] = lambda: mock_service
    
    try:
        payload = {"message": "Qual o perfil do Hector?"}
        response = client.post("/api/chat", json = payload) 
        
        assert response.status_code == 200
        assert response.json() == {"response": "AI mocked answer"}
        
    finally:
        main.app.dependency_overrides = {}


def test_internal_error_chat_endpoint(client, mocker: MockerFixture):
    """"""

    mock_service = mocker.AsyncMock()
    mock_service.get_response.side_effect = Exception("ChromaDB Error")

    main.app.dependency_overrides[get_chat_service] = lambda: mock_service

    try:
        response = client.post("/api/chat", json = {"message": "Error"})

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal process error answer"
        
    finally:
        main.app.dependency_overrides = {}