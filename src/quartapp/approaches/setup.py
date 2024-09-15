from abc import ABC

from langchain_community.vectorstores import AzureCosmosDBVectorSearch
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from pydantic import SecretStr
from pymongo.collection import Collection

from quartapp.approaches.keyword import KeyWord
from quartapp.approaches.rag import RAG
from quartapp.approaches.utils import (
    chat_api,
    embeddings_api,
    setup_data_collection,
    setup_users_collection,
    vector_store_api,
)
from quartapp.approaches.vector import Vector


class OpenAISetup(ABC):
    def __init__(
        self,
        embeddings_api: AzureOpenAIEmbeddings,
        chat_api: AzureChatOpenAI,
    ):
        self._embeddings_api = embeddings_api
        self._chat_api = chat_api


class DatabaseSetup(ABC):
    def __init__(
        self,
        connection_string: str,
        database_name: str,
        collection_name: str,
        index_name: str,
        vector_store_api: AzureCosmosDBVectorSearch,
        users_collection: Collection,
        data_collection: Collection,
    ):
        self._connection_string = connection_string
        self._database_name = database_name
        self._collection_name = collection_name
        self._index_name = index_name
        self._vector_store_api = vector_store_api
        self._users_collection = users_collection
        self._data_collection = data_collection


class Setup(ABC):
    def __init__(
        self,
        openai_embeddings_model: str,
        openai_embeddings_deployment: str,
        openai_chat_model: str,
        openai_chat_deployment: str,
        connection_string: str,
        database_name: str,
        collection_name: str,
        index_name: str,
        api_key: SecretStr,
        api_version: str,
        azure_endpoint: str,
    ):
        self._openai_setup = OpenAISetup(
            embeddings_api=embeddings_api(
                openai_embeddings_model,
                openai_embeddings_deployment,
                api_key,
                api_version,
                azure_endpoint,
            ),
            chat_api=chat_api(
                openai_chat_model,
                openai_chat_deployment,
                api_key,
                api_version,
                azure_endpoint,
            ),
        )
        self._database_setup = DatabaseSetup(
            connection_string=connection_string,
            database_name=database_name,
            collection_name=collection_name,
            index_name=index_name,
            vector_store_api=vector_store_api(
                connection_string=connection_string,
                namespace=f"{database_name}.{collection_name}",
                embedding=self._openai_setup._embeddings_api,
            ),
            users_collection=setup_users_collection(connection_string=connection_string, database_name=database_name),
            data_collection=setup_data_collection(
                connection_string=connection_string, database_name=database_name, collection_name=collection_name
            ),
        )

        self.vector_search = Vector(
            vector_store=self._database_setup._vector_store_api,
            embedding=self._openai_setup._embeddings_api,
            chat=self._openai_setup._chat_api,
            data_collection=self._database_setup._data_collection,
        )
        self.rag = RAG(
            vector_store=self._database_setup._vector_store_api,
            embedding=self._openai_setup._embeddings_api,
            chat=self._openai_setup._chat_api,
            data_collection=self._database_setup._data_collection,
        )
        self.keyword = KeyWord(
            vector_store=self._database_setup._vector_store_api,
            embedding=self._openai_setup._embeddings_api,
            chat=self._openai_setup._chat_api,
            data_collection=self._database_setup._data_collection,
        )
