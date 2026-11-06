"""Project constraints that do not need a model or Qdrant."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_env_example_has_two_empty_model_ids():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "\nEMBEDDING_MODEL_ID=\n" in text or text.startswith("EMBEDDING_MODEL_ID=\n")
    assert "\nGENERATION_MODEL_ID=\n" in text
    assert "FOURGEEKS_API_TOKEN" not in text
    assert "langchain" not in text.lower()


def test_python_code_does_not_read_the_forbidden_token_or_frameworks():
    banned = ("FOURGEEKS_API_TOKEN", "langchain", "llama_index", "LlamaIndex")
    for path in list((ROOT / "data").rglob("*.py")) + list((ROOT / "services").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for token in banned:
            assert token not in text, path


def test_dependencies_are_declared_for_uv():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
    assert "qdrant-client" in text
    assert "fastapi" in text
    assert "openai" in text
    assert "langchain" not in text
    assert "llama-index" not in text


def test_compose_file_defines_qdrant():
    text = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "qdrant/qdrant" in text
    assert "6333" in text
