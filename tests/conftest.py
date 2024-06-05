from unittest.mock import AsyncMock, MagicMock, patch

import mongomock
import pytest
import pytest_asyncio
from langchain_core.documents import Document
from pydantic.v1 import SecretStr

import quartapp
from quartapp.app import create_app
from quartapp.approaches.base import ApproachesBase
from quartapp.approaches.rag import RAG
from quartapp.approaches.setup import DatabaseSetup, Setup
from quartapp.approaches.vector import Vector
from quartapp.config import AppConfig


@pytest_asyncio.fixture
async def app():
    """Create a test app with the test config."""
    app_config = AppConfig()
    app = create_app(app_config=app_config)
    app.config.update(
        {
            "TESTING": True,
        }
    )
    async with app.test_app() as test_app:
        yield test_app


@pytest.fixture
def client(app):
    """Create a test client for the test app."""
    return app.test_client()


@pytest.fixture
@patch.object(ApproachesBase, "__abstractmethods__", set())
def approaches_base_mock():
    """Mock quartapp.approaches.base.ApproachesBase."""

    # Mock Embedding
    mock_embedding = MagicMock()

    # Mock Vector Store
    mock_vector_store = MagicMock()
    mock_retriever = MagicMock()
    mock_document = Document(
        page_content='{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}'
    )
    mock_retriever.ainvoke = AsyncMock(return_value=[mock_document])  # Assume there is always a response
    mock_vector_store.as_retriever.return_value = mock_retriever

    # Mock Chat
    mock_chat = MagicMock()

    mock_content = MagicMock()
    mock_content.content = "content"

    runnable_return = MagicMock()
    runnable_return.to_json = MagicMock(return_value={"kwargs": {"messages": [mock_content]}})

    mock_runnable = MagicMock()
    mock_runnable.ainvoke = AsyncMock(return_value=runnable_return)

    mock_chat.__or__.return_value = mock_runnable

    mock_chat.ainvoke = AsyncMock(return_value=mock_content)

    return ApproachesBase(mock_vector_store, mock_embedding, mock_chat)  # type: ignore [abstract]


@pytest.fixture
def vector_mock(approaches_base_mock):
    """Mock quartapp.approaches.vector.Vector."""
    return Vector(approaches_base_mock._vector_store, approaches_base_mock._embedding, approaches_base_mock._chat)


@pytest.fixture
def rag_mock(approaches_base_mock):
    """Mock quartapp.approaches.rag.RAG."""
    return RAG(approaches_base_mock._vector_store, approaches_base_mock._embedding, approaches_base_mock._chat)


@pytest.fixture
def database_mock(approaches_base_mock):
    """Mock quartapp.approaches.setup.DatabaseSetup."""

    mock_collection: mongomock.Collection = mongomock.MongoClient().db.collection

    database_setup = DatabaseSetup(
        connection_string="connection_string",
        database_name="database_name",
        collection_name="collection_name",
        index_name="index_name",
        vector_store_api=approaches_base_mock._vector_store,
        users_collection=mock_collection,
    )

    return database_setup


@pytest.fixture
def setup_mock(rag_mock, vector_mock, database_mock):
    """Mock quartapp.approaches.setup.Setup."""
    setup = Setup(
        openai_embeddings_model="openai_embeddings_model",
        openai_embeddings_deployment="openai_embeddings_deployment",
        openai_chat_model="openai_chat_model",
        openai_chat_deployment="openai_chat_deployment",
        connection_string="connection_string",
        database_name="database_name",
        collection_name="collection_name",
        index_name="index_name",
        api_key=SecretStr("api_key"),
        api_version="api_version",
        azure_endpoint="azure_endpoint",
    )

    setup._database_setup = database_mock
    setup.vector_search = vector_mock
    setup.rag = rag_mock
    return setup


@pytest.fixture
def app_config_mock(setup_mock):
    """Mock quartapp.config.AppConfig."""
    app_config = AppConfig()
    app_config.setup = setup_mock
    return app_config


@pytest.fixture(autouse=True)
def create_stuff_documents_chain_mock(monkeypatch):
    """Mock quartapp.approaches.rag.create_stuff_documents_chain."""
    document_chain_mock = MagicMock()
    document_chain_mock.ainvoke = AsyncMock(return_value="content")
    _mock = MagicMock()
    _mock.return_value = document_chain_mock
    monkeypatch.setattr(quartapp.approaches.rag, quartapp.approaches.rag.create_stuff_documents_chain.__name__, _mock)
    return _mock


@pytest_asyncio.fixture
async def app_mock(app_config_mock):
    """Create a test app with the test config mock."""
    app_mock = create_app(app_config=app_config_mock)
    app_mock.config.update(
        {
            "TESTING": True,
        }
    )
    async with app_mock.test_app() as test_app_mock:
        yield test_app_mock


@pytest.fixture
def client_mock(app_mock):
    """Create a test client for the test app mock."""
    return app_mock.test_client()
