from unittest.mock import MagicMock, patch

import pytest
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from pydantic import SecretStr
from pymongo.errors import ServerSelectionTimeoutError

from quartapp.approaches.utils import (
    chat_api,
    embeddings_api,
    setup_data_collection,
    setup_users_collection,
    vector_store_api,
)


def test_embeddings_api():
    """Test embeddings_api function."""
    result = embeddings_api(
        openai_embeddings_model="text-embedding-3-small",
        openai_embeddings_deployment="test-deployment",
        api_key=SecretStr("test-key"),
        api_version="2024-03-01-preview",
        azure_endpoint="https://test.openai.azure.com/",
    )

    assert isinstance(result, AzureOpenAIEmbeddings)
    # Check that the embedding instance was created successfully
    assert result is not None


def test_chat_api():
    """Test chat_api function."""
    result = chat_api(
        openai_chat_model="gpt-4o-mini",
        openai_chat_deployment="test-deployment",
        api_key=SecretStr("test-key"),
        api_version="2024-03-01-preview",
        azure_endpoint="https://test.openai.azure.com/",
    )

    assert isinstance(result, AzureChatOpenAI)
    # Check that the chat instance was created successfully
    assert result is not None


def test_vector_store_api():
    """Test vector_store_api function."""
    mock_embedding = MagicMock()

    with patch("quartapp.approaches.utils.AzureCosmosDBVectorSearch.from_connection_string") as mock_vector_store:
        mock_vector_store.return_value = MagicMock()

        vector_store_api(connection_string="test-connection", namespace="test-namespace", embedding=mock_embedding)

        mock_vector_store.assert_called_once_with(
            connection_string="test-connection", namespace="test-namespace", embedding=mock_embedding
        )


def test_setup_users_collection():
    """Test setup_users_collection function."""
    with patch("quartapp.approaches.utils.MongoClient") as mock_mongo_client:
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        result = setup_users_collection(connection_string="test-connection", database_name="test-db")

        mock_mongo_client.assert_called_once_with("test-connection")
        mock_client_instance.__getitem__.assert_called_once_with("test-db")
        mock_db.__getitem__.assert_called_once_with("Users")
        assert result == mock_collection


def test_setup_data_collection_success():
    """Test setup_data_collection function with successful connection."""
    with patch("quartapp.approaches.utils.MongoClient") as mock_mongo_client:
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        result = setup_data_collection(
            connection_string="test-connection", database_name="test-db", collection_name="test-collection"
        )

        mock_mongo_client.assert_called_once_with("test-connection", serverSelectionTimeoutMS=1000)
        mock_client_instance.__getitem__.assert_called_once_with("test-db")
        mock_db.__getitem__.assert_called_once_with("test-collection")
        mock_collection.create_index.assert_called_once_with({"textContent": "text"}, name="search_text_index")
        assert result == mock_collection


def test_setup_data_collection_timeout_error():
    """Test setup_data_collection function with ServerSelectionTimeoutError."""
    with patch("quartapp.approaches.utils.MongoClient") as mock_mongo_client:
        mock_mongo_client.side_effect = ServerSelectionTimeoutError("Timeout")

        with pytest.raises(ServerSelectionTimeoutError):
            setup_data_collection(
                connection_string="test-connection", database_name="test-db", collection_name="test-collection"
            )

        mock_mongo_client.assert_called_once_with("test-connection", serverSelectionTimeoutMS=1000)
