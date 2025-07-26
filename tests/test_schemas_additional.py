import pytest

from quartapp.approaches.schemas import (
    AIChatRoles,
    Context,
    DataPoint,
    Message,
    RetrievalResponse,
    RetrievalResponseDelta,
    Thought,
)


def test_thought_to_dict_with_none_values():
    """Test Thought to_dict method with None values."""
    thought = Thought()
    result = thought.to_dict()
    expected = {"title": None, "description": None}
    assert result == expected


def test_context_to_dict():
    """Test Context to_dict method."""
    data_points = [
        DataPoint(name="test1", description="desc1", price="10USD", category="food"),
        DataPoint(name="test2", description="desc2", price="15USD", category="drink")
    ]
    thoughts = [
        Thought(title="title1", description="desc1"),
        Thought(title="title2", description="desc2")
    ]
    
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
    
    response = RetrievalResponse(
        context=context,
        message=message,
        sessionState="test-session"
    )
    
    result = response.to_dict()
    
    assert "context" in result
    assert "message" in result
    assert "sessionState" in result
    assert result["sessionState"] == "test-session"
    assert result["message"]["content"] == "test message"
    assert result["message"]["role"] == AIChatRoles.ASSISTANT


def test_retrieval_response_delta_to_dict_with_all_none():
    """Test RetrievalResponseDelta to_dict method with all None values."""
    delta = RetrievalResponseDelta()
    result = delta.to_dict()
    
    expected = {
        "context": None,
        "delta": None,
        "sessionState": None
    }
    assert result == expected


def test_retrieval_response_delta_to_dict_with_partial_values():
    """Test RetrievalResponseDelta to_dict method with some None values."""
    message = Message(content="test message", role=AIChatRoles.ASSISTANT)
    delta = RetrievalResponseDelta(
        delta=message,
        sessionState="test-session"
        # context is None
    )
    result = delta.to_dict()
    
    assert result["context"] is None
    assert result["delta"]["content"] == "test message"
    assert result["sessionState"] == "test-session"


def test_retrieval_response_delta_to_dict_full():
    """Test RetrievalResponseDelta to_dict method with all values."""
    data_point = DataPoint(name="test", description="test description")
    thought = Thought(title="test title", description="test thought")
    context = Context(data_points=[data_point], thoughts=[thought])
    message = Message(content="test message", role=AIChatRoles.ASSISTANT)
    
    delta = RetrievalResponseDelta(
        context=context,
        delta=message,
        sessionState="test-session"
    )
    result = delta.to_dict()
    
    assert result["context"] is not None
    assert result["delta"] is not None
    assert result["sessionState"] == "test-session"
    assert result["context"]["data_points"][0]["name"] == "test"
    assert result["delta"]["content"] == "test message"


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
    
    expected = {
        "name": None,
        "description": None,
        "price": None,
        "category": None,
        "collection": None
    }
    assert result == expected


def test_enum_values():
    """Test enum values."""
    assert AIChatRoles.USER == "user"
    assert AIChatRoles.ASSISTANT == "assistant"
    assert AIChatRoles.SYSTEM == "system"