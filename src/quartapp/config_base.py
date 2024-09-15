import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from urllib.parse import quote_plus

from langchain_core.documents import Document
from pydantic import SecretStr
from pymongo.errors import (
    ConfigurationError,
    InvalidName,
    InvalidOperation,
    OperationFailure,
)

from quartapp.approaches.schemas import Context, DataPoint, RetrievalResponse, Thought
from quartapp.approaches.setup import Setup


def read_and_parse_connection_string() -> str:
    mongo_connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING", "YOUR-COSMOS-DB-CONNECTION-STRING")
    mongo_username = quote_plus(os.getenv("AZURE_COSMOS_USERNAME", "YOUR-COSMOS-DB-USERNAME"))
    mongo_password = quote_plus(os.getenv("AZURE_COSMOS_PASSWORD", "YOUR-COSMOS-DB-PASSWORD"))
    mongo_connection_string = mongo_connection_string.replace("<user>", mongo_username).replace(
        "<password>", mongo_password
    )
    return mongo_connection_string


class AppConfigBase(ABC):
    def __init__(self) -> None:
        openai_embeddings_model = os.getenv("AZURE_OPENAI_EMBEDDINGS_MODEL_NAME", "text-embedding-ada-002")
        openai_embeddings_deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME", "text-embedding")
        openai_chat_model = os.getenv("AZURE_OPENAI_CHAT_MODEL_NAME", "gpt-35-turbo")
        openai_chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "chat-gpt")
        connection_string = read_and_parse_connection_string()
        database_name = os.getenv("AZURE_COSMOS_DATABASE_NAME", "<COSMOS-DB-NEW-UNIQUE-DATABASE-NAME>")
        collection_name = os.getenv("AZURE_COSMOS_COLLECTION_NAME", "<COSMOS-DB-NEW-UNIQUE-DATABASE-NAME>")
        index_name = os.getenv("AZURE_COSMOS_INDEX_NAME", "<COSMOS-DB-NEW-UNIQUE-INDEX-NAME>")
        api_key = SecretStr(os.getenv("AZURE_OPENAI_API_KEY", "<YOUR-DEPLOYMENT-KEY>"))
        api_version = os.getenv("OPENAI_API_VERSION", "2023-09-15-preview")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://<YOUR-OPENAI-DEPLOYMENT-NAME>.openai.azure.com/")
        self.setup = Setup(
            openai_embeddings_model=openai_embeddings_model,
            openai_embeddings_deployment=openai_embeddings_deployment,
            openai_chat_model=openai_chat_model,
            openai_chat_deployment=openai_chat_deployment,
            connection_string=connection_string,
            database_name=database_name,
            collection_name=collection_name,
            index_name=index_name,
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )

    async def add_to_cosmos(
        self, old_messages: list, new_message: dict, session_state: str | None, new_session_state: str
    ) -> bool:
        is_first_message: bool = True if not session_state else False
        if is_first_message:
            try:
                if len(old_messages) == 0 or len(new_message) == 0 or len(new_session_state) == 0:
                    raise IndexError
                old_messages.append(new_message)
                self.setup._database_setup._users_collection.insert_one(
                    {
                        "_id": new_session_state,
                        "messages": old_messages,
                        "created_at": datetime.now(timezone.utc),  # noqa: UP017
                        "updated_at": datetime.now(timezone.utc),  # noqa: UP017
                    }
                )
                return True
            except (AttributeError, ConfigurationError, InvalidName, InvalidOperation, OperationFailure, IndexError):
                return False
        else:
            try:
                if len(old_messages) == 0 or len(new_message) == 0 or len(new_session_state) == 0:
                    raise IndexError
                self.setup._database_setup._users_collection.update_one(
                    {"_id": new_session_state},
                    {"$push": {"messages": {"$each": [old_messages[-1], new_message]}}},  # noqa: UP017
                )
                self.setup._database_setup._users_collection.update_one(
                    {"_id": new_session_state},
                    {"$set": {"updated_at": datetime.now(timezone.utc)}},  # noqa: UP017
                )
                return True
            except (AttributeError, ConfigurationError, InvalidName, InvalidOperation, OperationFailure, IndexError):
                return False

    def _get_thoughts(self, documents: list[Document]) -> list[Thought]:
        thoughts: list[Thought] = []
        thoughts.append(Thought(description=documents[0].metadata.get("source"), title="Source"))
        return thoughts

    def _get_data_points(self, documents: list[Document]) -> list[DataPoint]:
        data_points: list[DataPoint] = []

        for res in documents:
            raw_data = json.loads(res.page_content)
            json_data_point: DataPoint = DataPoint()
            json_data_point.name = raw_data.get("name")
            json_data_point.description = raw_data.get("description")
            json_data_point.price = raw_data.get("price")
            json_data_point.category = raw_data.get("category")
            json_data_point.collection = self.setup._database_setup._collection_name
            data_points.append(json_data_point)
        return data_points

    async def get_context(self, documents: list[Document]) -> Context:
        data_points = self._get_data_points(documents)
        thoughts = self._get_thoughts(documents)
        return Context(data_points=data_points, thoughts=thoughts)

    @abstractmethod
    async def run_vector(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse: ...

    @abstractmethod
    async def run_rag(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse: ...

    @abstractmethod
    async def run_keyword(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse: ...
