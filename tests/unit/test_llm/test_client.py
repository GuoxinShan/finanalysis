# tests/unit/test_llm/test_client.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.finanalysis.llm.client import LLMClient
from src.finanalysis.config import Settings


@patch('src.finanalysis.llm.client.OpenAI')
def test_llm_client_initialization(mock_openai):
    """Test LLM client initialization"""
    mock_openai.return_value = Mock()

    settings = Settings(
        openai_api_key="test-key",
        openai_base_url="https://api.example.com/v1",
        llm_model="qwen3.5-flash"
    )

    client = LLMClient(settings=settings)

    assert client.model == "qwen3.5-flash"
    assert client.settings == settings
    mock_openai.assert_called_once_with(
        api_key="test-key",
        base_url="https://api.example.com/v1"
    )


@patch('src.finanalysis.llm.client.OpenAI')
def test_llm_client_complete(mock_openai):
    """Test LLM client complete method"""
    # Mock the OpenAI client and response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    settings = Settings(
        openai_api_key="test-key",
        llm_model="qwen3.5-flash"
    )

    client = LLMClient(settings=settings)
    response = client.complete(messages=[{"role": "user", "content": "Test prompt"}])

    assert response == "Test response"
    mock_client.chat.completions.create.assert_called_once()


@patch('src.finanalysis.llm.client.OpenAI')
def test_llm_client_with_system_prompt(mock_openai):
    """Test LLM client with system prompt"""
    # Mock the OpenAI client and response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    settings = Settings(
        openai_api_key="test-key",
        llm_model="qwen3.5-flash"
    )

    client = LLMClient(settings=settings, system_prompt="You are a financial analyst.")
    response = client.complete(messages=[{"role": "user", "content": "Analyze this"}])

    assert response == "Response"

    # Verify system prompt was included
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]['messages']
    assert any(m['role'] == 'system' for m in messages)
