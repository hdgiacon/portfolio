import json
import pytest
from pytest_mock import MockerFixture

from src.domains.ingest.transform import TransformData

@pytest.fixture
def transformer(tmp_path, mocker: MockerFixture):
    """"""

    mock_settings = mocker.patch("src.domains.ingest.transform.get_settings")
    mock_settings.return_value.IGNORE_REPOS = [] 
    mock_settings.return_value.GITHUB_TOKEN = "fake_token"

    t = TransformData()
    
    t.output_github_json = str(tmp_path / "github_test.json")
    t.output_curriculum_json = str(tmp_path / "curriculum_test.json")
    
    return t


def test_clean_markdown(transformer: TransformData):
    """"""

    dirty_markdown = """
    # Title
    Texto com **negrito** e [link](http://url.com).
    ![image](img.png)
    - Item list
    ```python
    print('code')
    ```
    """
    
    processed_md = transformer.clean_markdown(dirty_markdown)
    
    assert "#" not in processed_md
    assert "**" not in processed_md
    assert "http://url.com" not in processed_md
    assert "imagem" not in processed_md
    assert "print('code')" not in processed_md
    assert "Texto com negrito e link." in processed_md


def test_structured_curriculum_parser(transformer: TransformData):
    """"""
    
    curriculum_text = """Ignorar 1
...
Ignorar 11
Experiência Profissional
Empresa X
Atuei com Python

Tecnologia
Python | Docker
"""
    
    transformer.parse_structured_curriculum(curriculum_text)
    
    with open(transformer.output_curriculum_json, 'r', encoding = 'utf-8') as f:
        dados = json.load(f)

    assert len(dados) == 2
    
    doc_exp = next(d for d in dados if d["metadata"]["type"] == "experience")
    assert "Empresa X" in doc_exp["content"]
    
    
    doc_tech = next(d for d in dados if d["metadata"]["type"] == "tech_stack")
    assert "docker" in doc_tech["metadata"]["tags"]