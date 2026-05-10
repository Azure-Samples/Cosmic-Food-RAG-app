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
    @staticmethod
    def _parse_embedding_dimensions(dimensions_str: str | None, env_var_name: str) -> int | None:
        if dimensions_str is not None:
            dimensions_str = dimensions_str.strip()
            if dimensions_str:
                try:
                    return int(dimensions_str)
                except ValueError:
                    raise ValueError(
                        f"Invalid {env_var_name} value: {dimensions_str!r}. It must be an integer or unset."
                    )
        return None

    def __init__(self) -> None:
        openai_chat_host = os.getenv("CHAT_MODEL_HOST", "azure")
        openai_embed_host = os.getenv("EMBED_MODEL_HOST", "azure")

        # Read chat model config based on host
        if openai_chat_host == "azure":
            chat_model = os.getenv("AZURE_OPENAI_CHAT_MODEL", "gpt-4o-mini")
            chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
            chat_api_key = SecretStr(os.getenv("AZURE_OPENAI_KEY", ""))
            chat_api_version = os.getenv("AZURE_OPENAI_VERSION", "2024-10-21")
            chat_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        elif openai_chat_host == "openai":
            chat_model = os.getenv("OPENAICOM_CHAT_MODEL", "gpt-4o-mini")
            chat_deployment = ""
            chat_api_key = SecretStr(os.getenv("OPENAICOM_KEY", ""))
            chat_api_version = ""
            chat_endpoint = ""
        elif openai_chat_host == "github":
            chat_model = os.getenv("GITHUB_MODEL", "gpt-4o-mini")
            chat_deployment = ""
            chat_api_key = SecretStr(os.getenv("GITHUB_TOKEN", ""))
            chat_api_version = ""
            chat_endpoint = os.getenv("GITHUB_ENDPOINT", "https://models.github.ai/inference")
        elif openai_chat_host == "ollama":
            chat_model = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2")
            chat_deployment = ""
            chat_api_key = SecretStr(os.getenv("OLLAMA_API_KEY", "nokeyneeded"))
            chat_api_version = ""
            chat_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/v1")
        else:
            raise ValueError(
                f"Unsupported CHAT_MODEL_HOST '{openai_chat_host}'. "
                "Supported values are: 'azure', 'openai', 'ollama', 'github'."
            )

        # Read embed model config based on host
        if openai_embed_host == "azure":
            embed_model = os.getenv("AZURE_OPENAI_EMBED_MODEL", "text-embedding-3-small")
            embed_deployment = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-small")
            embed_api_key = SecretStr(os.getenv("AZURE_OPENAI_KEY", ""))
            embed_api_version = os.getenv("AZURE_OPENAI_VERSION", "2024-10-21")
            embed_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
            embedding_dimensions = self._parse_embedding_dimensions(
                os.getenv("AZURE_OPENAI_EMBED_DIMENSIONS"), "AZURE_OPENAI_EMBED_DIMENSIONS"
            )
        elif openai_embed_host == "openai":
            embed_model = os.getenv("OPENAICOM_EMBED_MODEL", "text-embedding-3-small")
            embed_deployment = ""
            embed_api_key = SecretStr(os.getenv("OPENAICOM_KEY", ""))
            embed_api_version = ""
            embed_endpoint = ""
            embedding_dimensions = self._parse_embedding_dimensions(
                os.getenv("OPENAICOM_EMBED_DIMENSIONS"), "OPENAICOM_EMBED_DIMENSIONS"
            )
        elif openai_embed_host == "github":
            embed_model = os.getenv("GITHUB_EMBED_MODEL", "text-embedding-3-small")
            embed_deployment = ""
            embed_api_key = SecretStr(os.getenv("GITHUB_TOKEN", ""))
            embed_api_version = ""
            embed_endpoint = os.getenv("GITHUB_ENDPOINT", "https://models.github.ai/inference")
            embedding_dimensions = self._parse_embedding_dimensions(
                os.getenv("GITHUB_EMBED_DIMENSIONS"), "GITHUB_EMBED_DIMENSIONS"
            )
        elif openai_embed_host == "ollama":
            embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
            embed_deployment = ""
            embed_api_key = SecretStr(os.getenv("OLLAMA_API_KEY", "nokeyneeded"))
            embed_api_version = ""
            embed_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/v1")
            embedding_dimensions = self._parse_embedding_dimensions(
                os.getenv("OLLAMA_EMBED_DIMENSIONS"), "OLLAMA_EMBED_DIMENSIONS"
            )
        else:
            raise ValueError(
                f"Unsupported EMBED_MODEL_HOST '{openai_embed_host}'. "
                "Supported values are: 'azure', 'openai', 'ollama', 'github'."
            )

        connection_string = read_and_parse_connection_string()
        database_name = os.getenv("AZURE_COSMOS_DATABASE_NAME", "<COSMOS-DB-NEW-UNIQUE-DATABASE-NAME>")
        collection_name = os.getenv("AZURE_COSMOS_COLLECTION_NAME", "<COSMOS-DB-NEW-UNIQUE-DATABASE-NAME>")
        index_name = os.getenv("AZURE_COSMOS_INDEX_NAME", "<COSMOS-DB-NEW-UNIQUE-INDEX-NAME>")

        self.embedding_dimensions = embedding_dimensions
        self.setup = Setup(
            openai_embeddings_model=embed_model,
            openai_embeddings_deployment=embed_deployment,
            openai_chat_model=chat_model,
            openai_chat_deployment=chat_deployment,
            connection_string=connection_string,
            database_name=database_name,
            collection_name=collection_name,
            index_name=index_name,
            chat_api_key=chat_api_key,
            chat_api_version=chat_api_version,
            chat_endpoint=chat_endpoint,
            embed_api_key=embed_api_key,
            embed_api_version=embed_api_version,
            embed_endpoint=embed_endpoint,
            openai_chat_host=openai_chat_host,
            openai_embed_host=openai_embed_host,
            embedding_dimensions=embedding_dimensions,
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
