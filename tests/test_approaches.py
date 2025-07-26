from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from pydantic import SecretStr
from pymongo.errors import ServerSelectionTimeoutError

from quartapp.approaches.schemas import AIChatRoles, Context, DataPoint, Message, RetrievalResponse, Thought
from quartapp.approaches.utils import (
    chat_api,
    embeddings_api,
    setup_data_collection,
    setup_users_collection,
    vector_store_api,
)


@pytest.mark.asyncio
async def test_approaches_base(approaches_base_mock):
    """Test the ApproachesBase class."""
    assert approaches_base_mock._vector_store
    assert approaches_base_mock._embedding
    assert approaches_base_mock._chat
    assert approaches_base_mock._data_collection

    with pytest.raises(NotImplementedError):
        await approaches_base_mock.run([], 0.0, 0, 0.0)


@pytest.mark.asyncio
async def test_keyword_no_messages(keyword_mock):
    """Test the keyword class."""
    assert keyword_mock._vector_store
    assert keyword_mock._embedding
    assert keyword_mock._chat
    assert keyword_mock._data_collection
    with pytest.raises(IndexError):
        await keyword_mock.run([], 0.0, 0, 0.0) == ([], "")


@pytest.mark.asyncio
async def test_keyword_run(keyword_mock):
    """Test the Vector class run method."""
    result = keyword_mock.run([{"content": "test"}], 0.0, 0, 0.0)
    assert await result == (
        [
            Document(
                page_content='{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
                metadata={"source": "test"},
            )
        ],
        '{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
    )


@pytest.mark.asyncio
async def test_vector_no_messages(vector_mock):
    """Test the Vector class."""
    assert vector_mock._vector_store
    assert vector_mock._embedding
    assert vector_mock._chat
    assert vector_mock._data_collection
    with pytest.raises(IndexError):
        await vector_mock.run([], 0.0, 0, 0.0) == ([], "")


@pytest.mark.asyncio
async def test_vector_run(vector_mock):
    """Test the Vector class run method."""
    result = vector_mock.run([{"content": "test"}], 0.0, 0, 0.0)
    assert await result == (
        [
            Document(
                metadata={"source": "test"},
                page_content='{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
            )
        ],
        '{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
    )


@pytest.mark.asyncio
async def test_rag_no_messages(rag_mock):
    """Test the RAG class."""
    assert rag_mock._vector_store
    assert rag_mock._embedding
    assert rag_mock._chat
    assert rag_mock._data_collection
    with pytest.raises(IndexError):
        await rag_mock.run([], 0.0, 0, 0.0) == ([], "")


@pytest.mark.asyncio
async def test_rag_run(rag_mock):
    """Test the RAG class run method."""
    result = rag_mock.run([{"content": "test"}], 0.0, 0, 0.0)
    assert await result == (
        [
            Document(
                metadata={"source": "test"},
                page_content='{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
            )
        ],
        '{"response": "content", "rephrased_response": "content"}',
    )


@pytest.mark.asyncio
async def test_app_setup(setup_mock):
    """Test the Setup class."""
    assert setup_mock._openai_setup
    assert setup_mock._database_setup
    assert setup_mock.vector_search
    assert setup_mock.rag
    assert setup_mock.keyword


@pytest.mark.asyncio
async def test_app_config(app_config_mock):
    """Test the AppConfig class."""
    assert app_config_mock.setup
    assert app_config_mock.setup._openai_setup
    assert app_config_mock.setup._database_setup
    assert app_config_mock.setup.vector_search
    assert app_config_mock.setup.rag
    assert app_config_mock.setup.keyword


@pytest.mark.asyncio
async def test_app_config_run_keyword(app_config_mock):
    """Test the AppConfig class run_keyword method."""
    result = app_config_mock.run_keyword("test", [{"content": "test"}], 0.3, 1, 0.0)
    assert await result == RetrievalResponse(
        context=Context(
            data_points=[
                DataPoint(
                    name="test",
                    description="test",
                    price="5.0USD",
                    category="test",
                    collection="collection_name",
                )
            ],
            thoughts=[
                Thought(
                    title="Cosmos Text Search Query",
                    description="test",
                ),
                Thought(
                    title="Cosmos Text Search Result",
                    description="[Document(metadata={'source': 'test'}, "
                    'page_content=\'{"name": "test", "description": "test", '
                    '"price": "5.0USD", "category": "test"}\')]',
                ),
                Thought(
                    title="Cosmos Text Search Top Result",
                    description='{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
                ),
                Thought(title="Source", description="test"),
            ],
        ),
        message=Message(
            content="\n            Name: test\n            Description: test\n            Price: 5.0USD\n"
            "            Category: test\n            Collection: collection_name\n        ",
            role=AIChatRoles.ASSISTANT,
        ),
        sessionState="test",
    )


@pytest.mark.asyncio
async def test_app_config_run_vector(app_config_mock):
    """Test the AppConfig class run_vector method."""
    result = app_config_mock.run_vector("test", [{"content": "test"}], 0.3, 1, 0.0)
    assert await result == RetrievalResponse(
        context=Context(
            data_points=[
                DataPoint(
                    name="test",
                    description="test",
                    price="5.0USD",
                    category="test",
                    collection="collection_name",
                )
            ],
            thoughts=[
                Thought(
                    title="Cosmos Vector Search Query",
                    description="test",
                ),
                Thought(
                    title="Cosmos Vector Search Result",
                    description="[Document(metadata={'source': 'test'}, "
                    'page_content=\'{"name": "test", "description": "test", '
                    '"price": "5.0USD", "category": "test"}\')]',
                ),
                Thought(
                    title="Cosmos Vector Search Top Result",
                    description='{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
                ),
                Thought(title="Source", description="test"),
            ],
        ),
        message=Message(
            content="\n            Name: test\n            Description: test\n            Price: 5.0USD\n"
            "            Category: test\n            Collection: collection_name\n        ",
            role=AIChatRoles.ASSISTANT,
        ),
        sessionState="test",
    )


@pytest.mark.asyncio
async def test_app_config_run_rag(app_config_mock):
    """Test the AppConfig class run_rag method."""
    result = app_config_mock.run_rag("test", [{"content": "test"}], 0.3, 1, 0.0)
    assert await result == RetrievalResponse(
        context=Context(
            data_points=[
                DataPoint(
                    name="test",
                    description="test",
                    price="5.0USD",
                    category="test",
                    collection="collection_name",
                )
            ],
            thoughts=[
                Thought(
                    title="Cosmos RAG Query",
                    description="test",
                ),
                Thought(
                    title="Cosmos RAG OpenAI Rephrased Query",
                    description="content",
                ),
                Thought(
                    title="Cosmos RAG Search Vector Search Result",
                    description="[Document(metadata={'source': 'test'}, "
                    'page_content=\'{"name": "test", "description": "test", '
                    '"price": "5.0USD", "category": "test"}\')]',
                ),
                Thought(
                    title="Cosmos RAG OpenAI Rephrased Response",
                    description="content",
                ),
                Thought(title="Source", description="test"),
            ],
        ),
        message=Message(content="content", role=AIChatRoles.ASSISTANT),
        sessionState="test",
    )


@pytest.mark.asyncio
async def test_app_config_run_keyword_no_message(app_config_mock):
    """Test the AppConfig class run_keyword method without messages."""
    with pytest.raises(IndexError):
        await app_config_mock.run_keyword("test", [], 0.3, 1, 0.0)


@pytest.mark.asyncio
async def test_app_config_run_vector_no_message(app_config_mock):
    """Test the AppConfig class run_vector method without messages."""
    with pytest.raises(IndexError):
        await app_config_mock.run_vector("test", [], 0.3, 1, 0.0)


@pytest.mark.asyncio
async def test_app_config_run_rag_no_message(app_config_mock):
    """Test the AppConfig class run_rag method without messages."""
    with pytest.raises(IndexError):
        await app_config_mock.run_vector("test", [], 0.3, 1, 0.0)


@pytest.mark.asyncio
async def test_add_to_cosmos_with_session_id(app_config_mock):
    """Test the AppConfig class add_to_cosmos method with session_id."""
    is_added = await app_config_mock.add_to_cosmos(
        old_messages=[{"content": "test"}],
        new_message={"content": "test"},
        session_state="test",
        new_session_state="test",
    )
    assert is_added is True


@pytest.mark.asyncio
async def test_add_to_cosmos_without_session_id(app_config_mock):
    """Test the AppConfig class add_to_cosmos method without session_id."""
    is_added = await app_config_mock.add_to_cosmos(
        old_messages=[{"content": "test"}],
        new_message={"content": "test"},
        session_state=None,
        new_session_state="test",
    )
    assert is_added is True


@pytest.mark.asyncio
async def test_add_to_cosmos_without_messages(app_config_mock):
    """Test the AppConfig class add_to_cosmos method without messages."""
    is_added = await app_config_mock.add_to_cosmos(
        old_messages=[],
        new_message={},
        session_state=None,
        new_session_state="rebgverrberberebernb",
    )
    assert is_added is False


@pytest.mark.asyncio
async def test_add_to_cosmos_without_id(app_config_mock):
    """Test the AppConfig class add_to_cosmos method without id."""
    is_added = await app_config_mock.add_to_cosmos(
        old_messages=[],
        new_message={},
        session_state=None,
        new_session_state="",
    )
    assert is_added is False


@pytest.mark.asyncio
async def test_add_to_cosmos_with_id_and_without_messages(app_config_mock):
    """Test the AppConfig class add_to_cosmos method with id and  without messages."""
    is_added = await app_config_mock.add_to_cosmos(
        old_messages=[],
        new_message={},
        session_state="test",
        new_session_state="test",
    )
    assert is_added is False


# Schema tests
def test_thought_to_dict_with_none_values():
    """Test Thought to_dict method with None values."""
    from quartapp.approaches.schemas import Thought

    thought = Thought()
    result = thought.to_dict()
    expected = {"title": None, "description": None}
    assert result == expected


def test_context_to_dict():
    """Test Context to_dict method."""
    data_points = [
        DataPoint(name="test1", description="desc1", price="10USD", category="food"),
        DataPoint(name="test2", description="desc2", price="15USD", category="drink"),
    ]
    thoughts = [Thought(title="title1", description="desc1"), Thought(title="title2", description="desc2")]

    context = Context(data_points=data_points, thoughts=thoughts)
    result = context.to_dict()

    assert "data_points" in result
    assert "thoughts" in result
    assert len(result["data_points"]) == 2
    assert len(result["thoughts"]) == 2
    assert result["data_points"][0]["name"] == "test1"
    assert result["thoughts"][0]["title"] == "title1"


def test_retrieval_response_to_dict():
    """Test RetrievalResponse to_dict method."""
    data_point = DataPoint(name="test", description="test description")
    thought = Thought(title="test title", description="test thought")
    context = Context(data_points=[data_point], thoughts=[thought])
    message = Message(content="test message", role=AIChatRoles.ASSISTANT)

    response = RetrievalResponse(context=context, message=message, sessionState="test-session")

    result = response.to_dict()

    assert "context" in result
    assert "message" in result
    assert "sessionState" in result
    assert result["sessionState"] == "test-session"
    assert isinstance(result["message"], dict)
    assert result["message"]["content"] == "test message"  # type: ignore[index]
    assert result["message"]["role"] == AIChatRoles.ASSISTANT  # type: ignore[index]


def test_retrieval_response_delta_to_dict_with_all_none():
    """Test RetrievalResponseDelta to_dict method with all None values."""
    from quartapp.approaches.schemas import RetrievalResponseDelta

    delta = RetrievalResponseDelta()
    result = delta.to_dict()

    expected = {"context": None, "delta": None, "sessionState": None}
    assert result == expected


def test_retrieval_response_delta_to_dict_with_partial_values():
    """Test RetrievalResponseDelta to_dict method with some None values."""
    from quartapp.approaches.schemas import RetrievalResponseDelta

    message = Message(content="test message", role=AIChatRoles.ASSISTANT)
    delta = RetrievalResponseDelta(
        delta=message,
        sessionState="test-session",
        # context is None
    )
    result = delta.to_dict()

    assert result["context"] is None
    assert isinstance(result["delta"], dict)
    assert result["delta"]["content"] == "test message"  # type: ignore[index]
    assert result["sessionState"] == "test-session"


def test_retrieval_response_delta_to_dict_full():
    """Test RetrievalResponseDelta to_dict method with all values."""
    from quartapp.approaches.schemas import RetrievalResponseDelta

    data_point = DataPoint(name="test", description="test description")
    thought = Thought(title="test title", description="test thought")
    context = Context(data_points=[data_point], thoughts=[thought])
    message = Message(content="test message", role=AIChatRoles.ASSISTANT)

    delta = RetrievalResponseDelta(context=context, delta=message, sessionState="test-session")
    result = delta.to_dict()

    assert result["context"] is not None
    assert result["delta"] is not None
    assert result["sessionState"] == "test-session"
    assert isinstance(result["context"], dict)
    assert isinstance(result["delta"], dict)
    assert result["context"]["data_points"][0]["name"] == "test"  # type: ignore[index]
    assert result["delta"]["content"] == "test message"  # type: ignore[index]


def test_message_default_role():
    """Test Message default role assignment."""
    message = Message(content="test")
    assert message.role == AIChatRoles.ASSISTANT

    result = message.to_dict()
    assert result["role"] == AIChatRoles.ASSISTANT


def test_datapoint_all_none():
    """Test DataPoint with all None values."""
    data_point = DataPoint()
    result = data_point.to_dict()

    expected = {"name": None, "description": None, "price": None, "category": None, "collection": None}
    assert result == expected


def test_enum_values():
    """Test enum values."""
    assert AIChatRoles.USER == "user"
    assert AIChatRoles.ASSISTANT == "assistant"
    assert AIChatRoles.SYSTEM == "system"


# Utils tests
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


# RAG additional tests
@pytest.mark.asyncio
async def test_rag_run_no_data_points(rag_mock):
    """Test RAG run method when no data points are found."""
    # Mock the retriever to return no documents
    rag_mock._vector_store.as_retriever.return_value.ainvoke = AsyncMock(return_value=[])

    # Mock the chat response
    mock_response = MagicMock()
    mock_response.content = "No relevant information found"
    rag_mock._chat.ainvoke = AsyncMock(return_value=mock_response)

    # Mock the chain to avoid external API calls
    with patch("quartapp.approaches.rag.ChatPromptTemplate") as mock_template:
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_template.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = await rag_mock.run([{"content": "test question"}], 0.3, 1, 0.0)

        documents, answer = result
        assert documents == []
        assert "No relevant information found" in answer
        assert "rephrased_response" in answer


@pytest.mark.asyncio
async def test_rag_temperature_setting(rag_mock):
    """Test that RAG properly sets temperature values."""
    # Mock the retriever and responses
    rag_mock._vector_store.as_retriever.return_value.ainvoke = AsyncMock(return_value=[])

    mock_rephrase_response = MagicMock()
    mock_rephrase_response.content = "test"

    mock_context_response = MagicMock()
    mock_context_response.content = "test response"

    # Mock the chat chain
    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(side_effect=[mock_rephrase_response, mock_context_response])

    with patch("quartapp.approaches.rag.ChatPromptTemplate") as mock_template:
        mock_template.from_template.return_value = MagicMock()
        mock_template.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)

        # Test with specific temperature
        await rag_mock.run([{"content": "test"}], 0.8, 1, 0.0)

        # Should set temperature to 0.3 for rephrase, then to specified temperature
        assert rag_mock._chat.temperature == 0.8
