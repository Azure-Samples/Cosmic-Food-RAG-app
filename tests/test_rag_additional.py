from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document

from quartapp.approaches.rag import RAG


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
    with patch('quartapp.approaches.rag.ChatPromptTemplate') as mock_template:
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
    
    with patch('quartapp.approaches.rag.ChatPromptTemplate') as mock_template:
        mock_template.from_template.return_value = MagicMock()
        mock_template.from_template.return_value.__or__ = MagicMock(return_value=mock_chain)
        
        # Test with specific temperature
        await rag_mock.run([{"content": "test"}], 0.8, 1, 0.0)
        
        # Should set temperature to 0.3 for rephrase, then to specified temperature
        assert rag_mock._chat.temperature == 0.8