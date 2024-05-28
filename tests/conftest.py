from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from langchain_core.documents import Document

import quartapp
from quartapp.app import create_app
from quartapp.approaches.base import ApproachesBase
from quartapp.approaches.rag import RAG
from quartapp.approaches.vector import Vector
from quartapp.config import AppConfig


@pytest_asyncio.fixture
async def app():
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
    return app.test_client()


@pytest.fixture
@patch.object(ApproachesBase, "__abstractmethods__", set())
def approaches_base_mock():
    # Mock quartapp.approaches.base.ApproachesBase
    mock_embedding = MagicMock()

    # Mock Vector Store
    mock_vector_store = MagicMock()
    mock_retriever = MagicMock()
    mock_document = Document(page_content="content")
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
    # Mock quartapp.approaches.vector.Vector
    return Vector(approaches_base_mock._vector_store, approaches_base_mock._embedding, approaches_base_mock._chat)


@pytest.fixture
def rag_mock(approaches_base_mock):
    # Mock quartapp.approaches.rag.RAG
    return RAG(approaches_base_mock._vector_store, approaches_base_mock._embedding, approaches_base_mock._chat)


@pytest.fixture(autouse=True)
def create_stuff_documents_chain_mock(monkeypatch):
    document_chain_mock = MagicMock()
    document_chain_mock.ainvoke = AsyncMock(return_value="content")
    _mock = MagicMock()
    _mock.return_value = document_chain_mock
    monkeypatch.setattr(quartapp.approaches.rag, quartapp.approaches.rag.create_stuff_documents_chain.__name__, _mock)
    return _mock
