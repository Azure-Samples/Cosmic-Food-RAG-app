from abc import ABC, abstractmethod

from langchain_community.vectorstores import AzureCosmosDBVectorSearch
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from pymongo.collection import Collection


class ApproachesBase(ABC):
    def __init__(
        self,
        vector_store: AzureCosmosDBVectorSearch,
        embedding: Embeddings,
        chat: BaseChatModel,
        data_collection: Collection,
    ):
        self._vector_store = vector_store
        self._embedding = embedding
        self._chat = chat
        self._data_collection = data_collection

    @abstractmethod
    async def run(
        self, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> tuple[list[Document], str]:
        raise NotImplementedError
