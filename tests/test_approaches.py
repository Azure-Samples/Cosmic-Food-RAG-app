from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document

from quartapp.approaches.schemas import AIChatRoles, Context, DataPoint, Message, RetrievalResponse, Thought


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
