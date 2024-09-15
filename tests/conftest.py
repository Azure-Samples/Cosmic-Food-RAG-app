import os
from dataclasses import dataclass
from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import langchain_core
import mongomock
import openai
import openai.resources
import pytest
import pytest_asyncio
from langchain_core.documents import Document
from openai.types import CreateEmbeddingResponse, Embedding
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import (
    ChatCompletionMessage,
    Choice,
)
from openai.types.create_embedding_response import Usage
from pydantic import SecretStr

import quartapp
from quartapp.app import create_app
from quartapp.approaches.base import ApproachesBase
from quartapp.approaches.keyword import KeyWord
from quartapp.approaches.rag import RAG
from quartapp.approaches.setup import DatabaseSetup, Setup
from quartapp.approaches.vector import Vector
from quartapp.config import AppConfig


@pytest.fixture(scope="session")
def monkeypatch_session():
    with pytest.MonkeyPatch.context() as monkeypatch_session:
        yield monkeypatch_session


@pytest.fixture(scope="session")
def mock_session_env(monkeypatch_session):
    """Mock the environment variables for testing."""
    with mock.patch.dict(os.environ, clear=True):
        # Database
        monkeypatch_session.setenv("AZURE_COSMOS_CONNECTION_STRING", "test-connection-string")
        monkeypatch_session.setenv("AZURE_COSMOS_USERNAME", "test-username")
        monkeypatch_session.setenv("AZURE_COSMOS_PASSWORD", "test-password")
        monkeypatch_session.setenv("AZURE_COSMOS_DATABASE_NAME", "test-database")
        monkeypatch_session.setenv("AZURE_COSMOS_COLLECTION_NAME", "test-collection")
        monkeypatch_session.setenv("AZURE_COSMOS_INDEX_NAME", "test-index")
        # Azure Subscription
        monkeypatch_session.setenv("AZURE_SUBSCRIPTION_ID", "test-storage-subid")
        # Azure OpenAI
        monkeypatch_session.setenv("OPENAI_CHAT_HOST", "azure")
        monkeypatch_session.setenv("OPENAI_EMBED_HOST", "azure")
        monkeypatch_session.setenv("AZURE_OPENAI_ENDPOINT", "https://api.openai.com")
        monkeypatch_session.setenv("OPENAI_API_VERSION", "2024-03-01-preview")
        monkeypatch_session.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-35-turbo")
        monkeypatch_session.setenv("AZURE_OPENAI_CHAT_MODEL_NAME", "gpt-35-turbo")
        monkeypatch_session.setenv("AZURE_OPENAI_EMBEDDINGS_MODEL_NAME", "text-embedding-ada-002")
        monkeypatch_session.setenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME", "text-embedding-ada-002")
        monkeypatch_session.setenv("AZURE_OPENAI_EMBED_MODEL_DIMENSIONS", "1536")
        monkeypatch_session.setenv("AZURE_OPENAI_KEY", "fakekey")
        # Allowed Origin
        monkeypatch_session.setenv("ALLOWED_ORIGIN", "https://frontend.com")

        if os.getenv("AZURE_USE_AUTHENTICATION") is not None:
            monkeypatch_session.delenv("AZURE_USE_AUTHENTICATION")
        yield


@pytest.fixture
@patch.object(ApproachesBase, "__abstractmethods__", set())
def approaches_base_mock():
    """Mock quartapp.approaches.base.ApproachesBase."""

    # Mock Embedding
    mock_embedding = MagicMock()

    # Mock Vector Store
    mock_vector_store = MagicMock()
    mock_document = Document(
        page_content='{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
        metadata={"source": "test"},
    )
    mock_vector_store.as_retriever.return_value.ainvoke = AsyncMock(return_value=[mock_document])

    # Mock Chat
    mock_chat = MagicMock()

    # Mock Data Collection
    mock_mongo_document = {"textContent": mock_document.page_content, "metadata": {"source": "test"}}
    mock_data_collection = MagicMock()
    mock_data_collection.find = MagicMock()
    mock_data_collection.find.return_value.limit = MagicMock(return_value=[mock_mongo_document])

    return ApproachesBase(mock_vector_store, mock_embedding, mock_chat, mock_data_collection)  # type: ignore [abstract]


@pytest.fixture
def keyword_mock(approaches_base_mock):
    """Mock quartapp.approaches.keyword.KeyWord."""
    return KeyWord(
        approaches_base_mock._vector_store,
        approaches_base_mock._embedding,
        approaches_base_mock._chat,
        approaches_base_mock._data_collection,
    )


@pytest.fixture
def vector_mock(approaches_base_mock):
    """Mock quartapp.approaches.vector.Vector."""
    return Vector(
        approaches_base_mock._vector_store,
        approaches_base_mock._embedding,
        approaches_base_mock._chat,
        approaches_base_mock._data_collection,
    )


@pytest.fixture
def rag_mock(approaches_base_mock):
    """Mock quartapp.approaches.rag.RAG."""
    return RAG(
        approaches_base_mock._vector_store,
        approaches_base_mock._embedding,
        approaches_base_mock._chat,
        approaches_base_mock._data_collection,
    )


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
        data_collection=approaches_base_mock._data_collection,
    )

    return database_setup


@pytest.fixture
def setup_mock(rag_mock, vector_mock, database_mock, keyword_mock):
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
    setup.keyword = keyword_mock
    return setup


@pytest.fixture
def app_config_mock(setup_mock):
    """Mock quartapp.config.AppConfig."""
    app_config = AppConfig()
    app_config.setup = setup_mock
    return app_config


@pytest.fixture(autouse=True)
def setup_data_collection_mock(monkeypatch):
    """Mock quartapp.approaches.setup.setup_data_collection."""
    _mock = MagicMock()
    monkeypatch.setattr(quartapp.approaches.setup, quartapp.approaches.setup.setup_data_collection.__name__, _mock)
    return _mock


@pytest.fixture(autouse=True)
def mock_runnable_or(monkeypatch):
    """Mock langchain_core.runnables.base.Runnable.__or__."""

    @dataclass
    class MockContent:
        content: str

    or_return = MagicMock()
    or_return.ainvoke = AsyncMock(return_value=MockContent(content="content"))
    or_mock = MagicMock()
    or_mock.return_value = or_return
    monkeypatch.setattr(
        langchain_core.runnables.base.Runnable, langchain_core.runnables.base.Runnable.__or__.__name__, or_mock
    )
    return or_mock


@pytest.fixture(scope="session")
def mock_openai_embedding(monkeypatch_session):
    async def mock_acreate(*args, **kwargs):
        return CreateEmbeddingResponse(
            object="list",
            data=[
                Embedding(
                    embedding=[-124] * 768,
                    index=0,
                    object="embedding",
                )
            ],
            model="text-embedding-ada-002",
            usage=Usage(prompt_tokens=8, total_tokens=8),
        )

    monkeypatch_session.setattr(openai.resources.AsyncEmbeddings, "create", mock_acreate)

    yield


@pytest.fixture(scope="session")
def mock_openai_chatcompletion(monkeypatch_session):
    class AsyncChatCompletionIterator:
        def __init__(self, answer: str):
            chunk_id = "test-id"
            model = "gpt-35-turbo"
            self.responses = [
                {"object": "chat.completion.chunk", "choices": [], "id": chunk_id, "model": model, "created": 1},
                {
                    "object": "chat.completion.chunk",
                    "choices": [{"delta": {"role": "assistant"}, "index": 0, "finish_reason": None}],
                    "id": chunk_id,
                    "model": model,
                    "created": 1,
                },
            ]
            # Split at << to simulate chunked responses
            if answer.find("<<") > -1:
                parts = answer.split("<<")
                self.responses.append(
                    {
                        "object": "chat.completion.chunk",
                        "choices": [
                            {
                                "delta": {"role": "assistant", "content": parts[0] + "<<"},
                                "index": 0,
                                "finish_reason": None,
                            }
                        ],
                        "id": chunk_id,
                        "model": model,
                        "created": 1,
                    }
                )
                self.responses.append(
                    {
                        "object": "chat.completion.chunk",
                        "choices": [
                            {"delta": {"role": "assistant", "content": parts[1]}, "index": 0, "finish_reason": None}
                        ],
                        "id": chunk_id,
                        "model": model,
                        "created": 1,
                    }
                )
                self.responses.append(
                    {
                        "object": "chat.completion.chunk",
                        "choices": [{"delta": {"role": None, "content": None}, "index": 0, "finish_reason": "stop"}],
                        "id": chunk_id,
                        "model": model,
                        "created": 1,
                    }
                )
            else:
                self.responses.append(
                    {
                        "object": "chat.completion.chunk",
                        "choices": [{"delta": {"content": answer}, "index": 0, "finish_reason": None}],
                        "id": chunk_id,
                        "model": model,
                        "created": 1,
                    }
                )

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.responses:
                return ChatCompletionChunk.model_validate(self.responses.pop(0))
            else:
                raise StopAsyncIteration

    async def mock_acreate(*args, **kwargs):
        messages = kwargs["messages"]
        last_question = messages[-1]["content"]
        if last_question == "Generate search query for: What is the capital of France?":
            answer = "capital of France"
        elif last_question == "Generate search query for: Are interest rates high?":
            answer = "interest rates"
        elif isinstance(last_question, list) and last_question[2].get("image_url"):
            answer = "From the provided sources, the impact of interest rates and GDP growth on "
            "financial markets can be observed through the line graph. [Financial Market Analysis Report 2023-7.png]"
        else:
            answer = "The capital of France is Paris. [Benefit_Options-2.pdf]."
            if messages[0]["content"].find("Generate 3 very brief follow-up questions") > -1:
                answer = "The capital of France is Paris. [Benefit_Options-2.pdf]. <<What is the capital of Spain?>>"
        if "stream" in kwargs and kwargs["stream"] is True:
            return AsyncChatCompletionIterator(answer)
        else:
            return ChatCompletion(
                object="chat.completion",
                choices=[
                    Choice(
                        message=ChatCompletionMessage(role="assistant", content=answer), finish_reason="stop", index=0
                    )
                ],
                id="test-123",
                created=0,
                model="test-model",
            )

    monkeypatch_session.setattr(openai.resources.chat.completions.AsyncCompletions, "create", mock_acreate)

    yield


@pytest_asyncio.fixture
async def app_mock(mock_session_env, mock_openai_embedding, mock_openai_chatcompletion):
    """Create a test app with the test config mock."""
    app_mock = create_app()
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
