from abc import ABC, abstractmethod

from langchain_community.vectorstores import AzureCosmosDBVectorSearch
from langchain_core.documents import Document
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings


class ApproachesBase(ABC):
    def __init__(
        self,
        vector_store: AzureCosmosDBVectorSearch,
        embedding: AzureOpenAIEmbeddings,
        chat: AzureChatOpenAI,
    ):
        self._vector_store = vector_store
        self._embedding = embedding
        self._chat = chat

    @abstractmethod
    async def run(
        self, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> tuple[list[Document], str]:
        raise NotImplementedError
