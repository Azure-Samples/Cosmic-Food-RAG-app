import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from quart import Response

from quartapp.app import format_as_ndjson
from quartapp.approaches.schemas import AIChatRoles, Context, DataPoint, Message, RetrievalResponseDelta, Thought


@pytest.mark.asyncio
async def test_format_as_ndjson_success():
    """Test the format_as_ndjson function with successful stream."""
    async def mock_stream():
        delta = RetrievalResponseDelta(
            context=Context(
                data_points=[DataPoint(name="test", description="test description")],
                thoughts=[Thought(title="test", description="test thought")]
            ),
            delta=Message(content="test message", role=AIChatRoles.ASSISTANT),
            sessionState="test-session"
        )
        yield delta

    result = []
    async for line in format_as_ndjson(mock_stream()):
        result.append(line)
    
    assert len(result) == 1
    assert result[0].endswith('\n')
    parsed = json.loads(result[0].strip())
    assert parsed['sessionState'] == 'test-session'


@pytest.mark.asyncio
async def test_format_as_ndjson_exception():
    """Test the format_as_ndjson function with exception in stream."""
    async def mock_stream_with_error():
        yield RetrievalResponseDelta(sessionState="test")
        raise ValueError("Test error")

    result = []
    async for line in format_as_ndjson(mock_stream_with_error()):
        result.append(line)
    
    assert len(result) == 2
    # First line should be the successful yield
    parsed_first = json.loads(result[0].strip())
    assert parsed_first['sessionState'] == 'test'
    
    # Second line should be the error
    parsed_error = json.loads(result[1].strip())
    assert 'error' in parsed_error
    assert 'Test error' in parsed_error['error']





@pytest.mark.asyncio
async def test_chat_with_empty_messages_list(client_mock):
    """Test the chat route with empty messages list."""
    response: Response = await client_mock.post(
        "/chat",
        json={
            "sessionState": "test-session",
            "messages": [],
            "context": {"overrides": {"retrieval_mode": "vector"}}
        },
    )

    assert response.status_code == 400
    data = await response.get_json()
    assert data["error"] == "request must have a message"


@pytest.mark.asyncio
async def test_chat_stream_with_empty_messages_list(client_mock):
    """Test the stream chat route with empty messages list."""
    response: Response = await client_mock.post(
        "/chat/stream",
        json={
            "session_state": "test-session",
            "messages": [],
            "context": {"overrides": {"retrieval_mode": "rag"}}
        },
    )

    assert response.status_code == 400
    data = await response.get_json()
    assert data["error"] == "request must have a message"


