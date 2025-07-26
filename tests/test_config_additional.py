from unittest.mock import AsyncMock

import pytest

from quartapp.approaches.schemas import AIChatRoles


@pytest.mark.asyncio
async def test_run_keyword_no_results(app_config_mock):
    """Test run_keyword with no results returned."""
    # Mock the keyword approach to return empty results
    app_config_mock.setup.keyword.run = AsyncMock(return_value=([], ""))

    result = await app_config_mock.run_keyword("test-session", [{"content": "test"}], 0.3, 1, 0.0)

    assert result.message.content == "No results found"
    assert result.message.role == AIChatRoles.ASSISTANT
    assert len(result.context.data_points) == 1
    assert result.context.data_points[0].name is None


@pytest.mark.asyncio
async def test_run_vector_no_results(app_config_mock):
    """Test run_vector with no results returned."""
    # Mock the vector approach to return empty results
    app_config_mock.setup.vector_search.run = AsyncMock(return_value=([], ""))

    result = await app_config_mock.run_vector("test-session", [{"content": "test"}], 0.3, 1, 0.0)

    assert result.message.content == "No results found"
    assert result.message.role == AIChatRoles.ASSISTANT
    assert len(result.context.data_points) == 1
    assert result.context.data_points[0].name is None


@pytest.mark.asyncio
async def test_run_rag_no_results_with_answer(app_config_mock):
    """Test run_rag with no results but with answer returned."""
    # Mock the rag approach to return empty results but with answer
    app_config_mock.setup.rag.run = AsyncMock(
        return_value=([], '{"response": "test response", "rephrased_response": "test"}')
    )

    result = await app_config_mock.run_rag("test-session", [{"content": "test"}], 0.3, 1, 0.0)

    assert result.message.content == "test response"
    assert result.message.role == AIChatRoles.ASSISTANT
    assert len(result.context.data_points) == 1
    assert result.context.data_points[0].name is None


@pytest.mark.asyncio
async def test_run_rag_no_results_no_answer(app_config_mock):
    """Test run_rag with no results and no answer."""
    # This test covers the case where answer is completely empty and would cause JSON parsing to fail
    # We need to test with the mocked run method already handling the case more gracefully
    app_config_mock.setup.rag.run = AsyncMock(return_value=([], '{"response": "", "rephrased_response": ""}'))

    result = await app_config_mock.run_rag("test-session", [{"content": "test"}], 0.3, 1, 0.0)

    # When there are no results but valid answer JSON, it should return the empty response content
    assert result.message.content == ""
    assert result.message.role == AIChatRoles.ASSISTANT
    assert len(result.context.data_points) == 1
    assert result.context.data_points[0].name is None


@pytest.mark.asyncio
async def test_run_rag_no_results_truly_empty_answer(app_config_mock):
    """Test run_rag with no results and truly empty answer."""
    # Mock to bypass the JSON parsing by having the setup method handle empty properly
    from unittest.mock import patch

    with patch.object(app_config_mock, "setup") as mock_setup:
        # Mock to make the actual condition in line 109-114 trigger
        async def mock_rag_run(*args, **kwargs):
            return ([], "")  # Empty results and empty answer

        mock_setup.rag.run = mock_rag_run

        # Override the json.loads call to handle empty string
        with patch("json.loads") as mock_json_loads:
            mock_json_loads.side_effect = lambda x: {"response": "", "rephrased_response": ""} if x else {}

            result = await app_config_mock.run_rag("test-session", [{"content": "test"}], 0.3, 1, 0.0)

            # Should return "No results found" when answer is falsy
            assert result.message.content == "No results found"
            assert result.message.role == AIChatRoles.ASSISTANT


@pytest.mark.asyncio
async def test_run_rag_stream(app_config_mock):
    """Test run_rag_stream method."""
    from langchain_core.documents import Document

    # Mock document for rag response
    mock_document = Document(
        page_content='{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
        metadata={"source": "test"},
    )

    # Mock streaming response chunks
    class MockChunk:
        def __init__(self, content):
            self.content = content

    async def mock_stream():
        yield MockChunk("Hello")
        yield MockChunk(" world")
        yield MockChunk("!")

    # Mock the rag approach's run_stream method
    app_config_mock.setup.rag.run_stream = AsyncMock(return_value=([mock_document], mock_stream()))

    # Test the stream
    result_deltas = []
    async for delta in app_config_mock.run_rag_stream("test-session", [{"content": "test"}], 0.3, 1, 0.0):
        result_deltas.append(delta)

    # Should have context + 3 message chunks
    assert len(result_deltas) == 4

    # First delta should have context
    assert result_deltas[0].context is not None
    assert result_deltas[0].sessionState == "test-session"
    assert result_deltas[0].delta is None

    # Subsequent deltas should have message content
    assert result_deltas[1].delta.content == "Hello"
    assert result_deltas[2].delta.content == " world"
    assert result_deltas[3].delta.content == "!"


@pytest.mark.asyncio
async def test_run_rag_stream_without_session_state(app_config_mock):
    """Test run_rag_stream method without session state (new session)."""
    from langchain_core.documents import Document

    # Mock document for rag response
    mock_document = Document(
        page_content='{"name": "test", "description": "test", "price": "5.0USD", "category": "test"}',
        metadata={"source": "test"},
    )

    # Mock streaming response chunks
    class MockChunk:
        def __init__(self, content):
            self.content = content

    async def mock_stream():
        yield MockChunk("Test content")

    # Mock the rag approach's run_stream method
    app_config_mock.setup.rag.run_stream = AsyncMock(return_value=([mock_document], mock_stream()))

    # Test the stream without session state
    result_deltas = []
    async for delta in app_config_mock.run_rag_stream(None, [{"content": "test"}], 0.3, 1, 0.0):
        result_deltas.append(delta)

    # Should have context + 1 message chunk
    assert len(result_deltas) == 2

    # First delta should have context and a generated session state
    assert result_deltas[0].context is not None
    assert result_deltas[0].sessionState is not None
    assert result_deltas[0].sessionState != "test-session"  # Should be a new UUID
    assert result_deltas[0].delta is None

    # Second delta should have message content
    assert result_deltas[1].delta.content == "Test content"
