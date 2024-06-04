import pytest
from langchain_core.documents import Document


@pytest.mark.asyncio
async def test_approaches_base(approaches_base_mock):
    """Test the ApproachesBase class."""
    assert approaches_base_mock._vector_store
    assert approaches_base_mock._embedding
    assert approaches_base_mock._chat

    with pytest.raises(NotImplementedError):
        await approaches_base_mock.run([], 0.0, 0, 0.0)


@pytest.mark.asyncio
async def test_vector(vector_mock):
    """Test the Vector class."""
    assert vector_mock._vector_store
    assert vector_mock._embedding
    assert vector_mock._chat
    assert await vector_mock.run([], 0.0, 0, 0.0) == ([], "")


@pytest.mark.asyncio
async def test_vector_run(vector_mock):
    """Test the Vector class run method."""
    result = vector_mock.run([{"content": "test"}], 0.0, 0, 0.0)
    assert await result == ([Document(page_content="content")], "content")


@pytest.mark.asyncio
async def test_rag(rag_mock):
    """Test the RAG class."""
    assert rag_mock._vector_store
    assert rag_mock._embedding
    assert rag_mock._chat
    assert await rag_mock.run([], 0.0, 0, 0.0) == ([], "")


@pytest.mark.asyncio
async def test_rag_run(rag_mock):
    """Test the RAG class run method."""
    result = rag_mock.run([{"content": "test"}], 0.0, 0, 0.0)
    assert await result == ([Document(page_content="content")], "content")
