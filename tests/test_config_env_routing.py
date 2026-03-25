"""Tests for AppConfigBase env var routing per provider."""

import os
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from quartapp.config import AppConfig

# Common database env vars needed by all providers
_DB_ENV = {
    "AZURE_COSMOS_CONNECTION_STRING": "mongodb://testhost",
    "AZURE_COSMOS_USERNAME": "user",
    "AZURE_COSMOS_PASSWORD": "pass",
    "AZURE_COSMOS_DATABASE_NAME": "testdb",
    "AZURE_COSMOS_COLLECTION_NAME": "testcol",
    "AZURE_COSMOS_INDEX_NAME": "testidx",
}


def _make_env(provider_env: dict) -> dict:
    """Merge provider env vars with the common DB env vars."""
    return {**_DB_ENV, **provider_env}


@pytest.fixture(autouse=True)
def _patch_setup():
    """Patch Setup.__init__ to capture args without creating real clients."""
    with patch("quartapp.config_base.Setup") as mock_setup_cls:
        mock_setup_cls.return_value = MagicMock()
        yield mock_setup_cls


def test_azure_env_routing(_patch_setup):
    """Test that Azure provider env vars are routed correctly."""
    env = _make_env(
        {
            "CHAT_MODEL_HOST": "azure",
            "EMBED_MODEL_HOST": "azure",
            "AZURE_OPENAI_KEY": "azure-key-123",
            "AZURE_OPENAI_VERSION": "2024-10-21",
            "AZURE_OPENAI_ENDPOINT": "https://myservice.openai.azure.com",
            "AZURE_OPENAI_CHAT_MODEL": "gpt-4o",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4o-deploy",
            "AZURE_OPENAI_EMBED_MODEL": "text-embedding-3-small",
            "AZURE_OPENAI_EMBED_DEPLOYMENT": "embed-deploy",
            "AZURE_OPENAI_EMBED_DIMENSIONS": "256",
        }
    )
    with mock.patch.dict(os.environ, env, clear=True):
        AppConfig()

    kwargs = _patch_setup.call_args.kwargs
    assert kwargs["openai_chat_model"] == "gpt-4o"
    assert kwargs["openai_chat_deployment"] == "gpt-4o-deploy"
    assert kwargs["chat_api_key"] == SecretStr("azure-key-123")
    assert kwargs["chat_api_version"] == "2024-10-21"
    assert kwargs["chat_endpoint"] == "https://myservice.openai.azure.com"
    assert kwargs["openai_chat_host"] == "azure"

    assert kwargs["openai_embeddings_model"] == "text-embedding-3-small"
    assert kwargs["openai_embeddings_deployment"] == "embed-deploy"
    assert kwargs["embed_api_key"] == SecretStr("azure-key-123")
    assert kwargs["embed_api_version"] == "2024-10-21"
    assert kwargs["embed_endpoint"] == "https://myservice.openai.azure.com"
    assert kwargs["openai_embed_host"] == "azure"
    assert kwargs["embedding_dimensions"] == 256


def test_openai_env_routing(_patch_setup):
    """Test that OpenAI.com provider env vars are routed correctly."""
    env = _make_env(
        {
            "CHAT_MODEL_HOST": "openai",
            "EMBED_MODEL_HOST": "openai",
            "OPENAICOM_KEY": "sk-openai-key",
            "OPENAICOM_CHAT_MODEL": "gpt-4-turbo",
            "OPENAICOM_EMBED_MODEL": "text-embedding-3-large",
            "OPENAICOM_EMBED_DIMENSIONS": "3072",
        }
    )
    with mock.patch.dict(os.environ, env, clear=True):
        AppConfig()

    kwargs = _patch_setup.call_args.kwargs
    assert kwargs["openai_chat_model"] == "gpt-4-turbo"
    assert kwargs["openai_chat_deployment"] == ""
    assert kwargs["chat_api_key"] == SecretStr("sk-openai-key")
    assert kwargs["chat_api_version"] == ""
    assert kwargs["chat_endpoint"] == ""
    assert kwargs["openai_chat_host"] == "openai"

    assert kwargs["openai_embeddings_model"] == "text-embedding-3-large"
    assert kwargs["openai_embeddings_deployment"] == ""
    assert kwargs["embed_api_key"] == SecretStr("sk-openai-key")
    assert kwargs["embed_api_version"] == ""
    assert kwargs["embed_endpoint"] == ""
    assert kwargs["openai_embed_host"] == "openai"
    assert kwargs["embedding_dimensions"] == 3072


def test_github_env_routing(_patch_setup):
    """Test that GitHub Models provider env vars are routed correctly."""
    env = _make_env(
        {
            "CHAT_MODEL_HOST": "github",
            "EMBED_MODEL_HOST": "github",
            "GITHUB_TOKEN": "ghp_testtoken",
            "GITHUB_MODEL": "gpt-4o-mini",
            "GITHUB_EMBED_MODEL": "text-embedding-3-small",
            "GITHUB_EMBED_DIMENSIONS": "1536",
            "GITHUB_ENDPOINT": "https://models.github.ai/inference",
        }
    )
    with mock.patch.dict(os.environ, env, clear=True):
        AppConfig()

    kwargs = _patch_setup.call_args.kwargs
    assert kwargs["openai_chat_model"] == "gpt-4o-mini"
    assert kwargs["openai_chat_deployment"] == ""
    assert kwargs["chat_api_key"] == SecretStr("ghp_testtoken")
    assert kwargs["chat_api_version"] == ""
    assert kwargs["chat_endpoint"] == "https://models.github.ai/inference"
    assert kwargs["openai_chat_host"] == "github"

    assert kwargs["openai_embeddings_model"] == "text-embedding-3-small"
    assert kwargs["openai_embeddings_deployment"] == ""
    assert kwargs["embed_api_key"] == SecretStr("ghp_testtoken")
    assert kwargs["embed_api_version"] == ""
    assert kwargs["embed_endpoint"] == "https://models.github.ai/inference"
    assert kwargs["openai_embed_host"] == "github"
    assert kwargs["embedding_dimensions"] == 1536


def test_ollama_env_routing(_patch_setup):
    """Test that Ollama provider env vars are routed correctly."""
    env = _make_env(
        {
            "CHAT_MODEL_HOST": "ollama",
            "EMBED_MODEL_HOST": "ollama",
            "OLLAMA_ENDPOINT": "http://myhost:11434/v1",
            "OLLAMA_CHAT_MODEL": "llama3.2",
            "OLLAMA_EMBED_MODEL": "nomic-embed-text",
            "OLLAMA_EMBED_DIMENSIONS": "768",
        }
    )
    with mock.patch.dict(os.environ, env, clear=True):
        AppConfig()

    kwargs = _patch_setup.call_args.kwargs
    assert kwargs["openai_chat_model"] == "llama3.2"
    assert kwargs["openai_chat_deployment"] == ""
    assert kwargs["chat_api_key"] == SecretStr("nokeyneeded")
    assert kwargs["chat_api_version"] == ""
    assert kwargs["chat_endpoint"] == "http://myhost:11434/v1"
    assert kwargs["openai_chat_host"] == "ollama"

    assert kwargs["openai_embeddings_model"] == "nomic-embed-text"
    assert kwargs["openai_embeddings_deployment"] == ""
    assert kwargs["embed_api_key"] == SecretStr("nokeyneeded")
    assert kwargs["embed_api_version"] == ""
    assert kwargs["embed_endpoint"] == "http://myhost:11434/v1"
    assert kwargs["openai_embed_host"] == "ollama"
    assert kwargs["embedding_dimensions"] == 768


def test_mixed_hosts_env_routing(_patch_setup):
    """Test mixing Azure for chat and Ollama for embeddings."""
    env = _make_env(
        {
            "CHAT_MODEL_HOST": "azure",
            "EMBED_MODEL_HOST": "ollama",
            "AZURE_OPENAI_KEY": "azure-key",
            "AZURE_OPENAI_VERSION": "2024-10-21",
            "AZURE_OPENAI_ENDPOINT": "https://myservice.openai.azure.com",
            "AZURE_OPENAI_CHAT_MODEL": "gpt-4o-mini",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4o-mini",
            "OLLAMA_ENDPOINT": "http://localhost:11434/v1",
            "OLLAMA_EMBED_MODEL": "nomic-embed-text",
            "OLLAMA_EMBED_DIMENSIONS": "768",
        }
    )
    with mock.patch.dict(os.environ, env, clear=True):
        AppConfig()

    kwargs = _patch_setup.call_args.kwargs
    # Chat should use Azure
    assert kwargs["chat_api_key"] == SecretStr("azure-key")
    assert kwargs["chat_endpoint"] == "https://myservice.openai.azure.com"
    assert kwargs["openai_chat_host"] == "azure"
    # Embed should use Ollama
    assert kwargs["embed_api_key"] == SecretStr("nokeyneeded")
    assert kwargs["embed_endpoint"] == "http://localhost:11434/v1"
    assert kwargs["openai_embed_host"] == "ollama"
    assert kwargs["openai_embeddings_model"] == "nomic-embed-text"
    assert kwargs["embedding_dimensions"] == 768


def test_unsupported_chat_host():
    """Test that unsupported CHAT_MODEL_HOST raises ValueError."""
    env = _make_env(
        {
            "CHAT_MODEL_HOST": "invalid",
            "EMBED_MODEL_HOST": "azure",
        }
    )
    with mock.patch.dict(os.environ, env, clear=True):
        with pytest.raises(ValueError, match="Unsupported CHAT_MODEL_HOST 'invalid'"):
            AppConfig()


def test_unsupported_embed_host():
    """Test that unsupported EMBED_MODEL_HOST raises ValueError."""
    env = _make_env(
        {
            "CHAT_MODEL_HOST": "azure",
            "EMBED_MODEL_HOST": "invalid",
            "AZURE_OPENAI_KEY": "key",
        }
    )
    with mock.patch.dict(os.environ, env, clear=True):
        with pytest.raises(ValueError, match="Unsupported EMBED_MODEL_HOST 'invalid'"):
            AppConfig()


def test_embedding_dimensions_not_set(_patch_setup):
    """Test that embedding_dimensions is None when env var is unset."""
    env = _make_env(
        {
            "CHAT_MODEL_HOST": "openai",
            "EMBED_MODEL_HOST": "openai",
            "OPENAICOM_KEY": "sk-key",
        }
    )
    with mock.patch.dict(os.environ, env, clear=True):
        config = AppConfig()

    assert config.embedding_dimensions is None
    assert _patch_setup.call_args.kwargs["embedding_dimensions"] is None


def test_embedding_dimensions_invalid():
    """Test that invalid embedding dimensions raises ValueError."""
    env = _make_env(
        {
            "CHAT_MODEL_HOST": "azure",
            "EMBED_MODEL_HOST": "azure",
            "AZURE_OPENAI_KEY": "key",
            "AZURE_OPENAI_EMBED_DIMENSIONS": "not-a-number",
        }
    )
    with mock.patch.dict(os.environ, env, clear=True):
        with pytest.raises(ValueError, match="Invalid AZURE_OPENAI_EMBED_DIMENSIONS"):
            AppConfig()
