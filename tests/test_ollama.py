"""Unit tests for Ollama client, health check, and error handling."""
import pytest
from unittest.mock import patch, MagicMock
from app.agent.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaModelNotFoundError,
)


@patch("httpx.Client.get")
def test_ollama_health_check_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [{"name": "qwen3.5:4b"}, {"name": "llama3:latest"}]
    }
    mock_get.return_value = mock_resp

    client = OllamaClient(model="qwen3.5:4b")
    status = client.check_health()
    assert status["status"] == "ok"
    assert "qwen3.5:4b" in status["models"]


@patch("httpx.Client.get")
def test_ollama_missing_model_error(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [{"name": "llama3:8b"}]
    }
    mock_get.return_value = mock_resp

    client = OllamaClient(model="qwen3.5:4b")
    with pytest.raises(OllamaModelNotFoundError) as exc_info:
        client.check_health()
    assert "Required model 'qwen3.5:4b' is not available" in str(exc_info.value)
    assert "ollama pull qwen3.5:4b" in str(exc_info.value)


@patch("httpx.Client.post")
def test_ollama_generate_json_fenced(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "response": "```json\n{\"extracted\": [\"claim 1\", \"claim 2\"], \"confidence\": 0.9}\n```"
    }
    mock_post.return_value = mock_resp

    client = OllamaClient()
    parsed = client.generate_json("extract claims")
    assert parsed["confidence"] == 0.9
    assert len(parsed["extracted"]) == 2


@patch("httpx.Client.get")
def test_ollama_connection_error(mock_get):
    import httpx
    mock_get.side_effect = httpx.ConnectError("Connection refused")

    client = OllamaClient()
    with pytest.raises(OllamaConnectionError) as exc_info:
        client.check_health()
    assert "Cannot connect to Ollama" in str(exc_info.value)

