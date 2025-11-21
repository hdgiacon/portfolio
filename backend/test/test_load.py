import json
import pytest

from src.domains.ingest.load import LoadData


@pytest.fixture
def loader(tmp_path: str) -> LoadData:
    """"""

    loader = LoadData()

    loader.default_json_dir = str(tmp_path)

    return loader


def test_correct_schema(loader: LoadData, tmp_path: str):
    """"""

    json_file = tmp_path / "valid.json"
    
    data = [{
        "id": "123", 
        "content": "Content", 
        "metadata": {"source": "test"}
    }]
    
    json_file.write_text(json.dumps(data), encoding = "utf-8")
    
    docs = loader.load_and_validate()
    
    assert len(docs) == 1
    assert docs[0].page_content == "Content"


def test_reject_invalid_data(loader: LoadData, tmp_path: str):
    """"""

    json_file = tmp_path / "invalid.json"
    
    data = [{
        "id": "123", 
        "metadata": {} 
    }]
    
    json_file.write_text(json.dumps(data), encoding = "utf-8")
    
    docs = loader.load_and_validate()
    
    assert len(docs) == 0