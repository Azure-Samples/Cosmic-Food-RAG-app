import os

from langchain_community.vectorstores import AzureCosmosDBVectorSearch
from langchain_core.embeddings import Embeddings
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings, ChatOpenAI, OpenAIEmbeddings
from langchain_openai.chat_models.base import BaseChatOpenAI
from pydantic import SecretStr
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ServerSelectionTimeoutError


def embeddings_api(
    openai_embeddings_model: str,
    openai_embeddings_deployment: str,
    api_key: SecretStr,
    api_version: str,
    azure_endpoint: str,
    openai_embed_host: str = "azure",
    embedding_dimensions: int | None = None,
) -> Embeddings:
    if openai_embed_host == "azure":
        kwargs: dict = {
            "model": openai_embeddings_model,
            "azure_deployment": openai_embeddings_deployment,
            "api_key": api_key,
            "api_version": api_version,
            "azure_endpoint": azure_endpoint,
        }
        if embedding_dimensions is not None:
            kwargs["dimensions"] = embedding_dimensions
        return AzureOpenAIEmbeddings(**kwargs)
    elif openai_embed_host == "ollama":
        kwargs = {
            "model": openai_embeddings_model,
            "base_url": azure_endpoint
            if azure_endpoint != ""
            else os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/v1"),
            "api_key": SecretStr(os.getenv("OLLAMA_API_KEY", "nokeyneeded")),
            "check_embedding_ctx_length": False,
        }
        if embedding_dimensions is not None:
            kwargs["dimensions"] = embedding_dimensions
        return OpenAIEmbeddings(**kwargs)
    elif openai_embed_host == "github":
        kwargs = {
            "model": openai_embeddings_model,
            "base_url": os.getenv("GITHUB_MODELS_ENDPOINT", "https://models.github.ai/inference"),
            "api_key": api_key,
        }
        if embedding_dimensions is not None:
            kwargs["dimensions"] = embedding_dimensions
        return OpenAIEmbeddings(**kwargs)
    elif openai_embed_host == "openai":
        kwargs = {
            "model": openai_embeddings_model,
            "api_key": api_key,
        }
        if embedding_dimensions is not None:
            kwargs["dimensions"] = embedding_dimensions
        return OpenAIEmbeddings(**kwargs)
    else:
        raise ValueError(
            f"Unsupported EMBED_MODEL_HOST '{openai_embed_host}'. "
            "Supported values are: 'azure', 'openai', 'ollama', 'github'."
        )


def chat_api(
    openai_chat_model: str,
    openai_chat_deployment: str,
    api_key: SecretStr,
    api_version: str,
    azure_endpoint: str,
    openai_chat_host: str = "azure",
) -> BaseChatOpenAI:
    if openai_chat_host == "azure":
        return AzureChatOpenAI(
            model=openai_chat_model,
            azure_deployment=openai_chat_deployment,
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )
    elif openai_chat_host == "ollama":
        return ChatOpenAI(
            model=openai_chat_model,
            base_url=azure_endpoint
            if azure_endpoint != ""
            else os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/v1"),
            api_key=SecretStr(os.getenv("OLLAMA_API_KEY", "nokeyneeded")),
        )
    elif openai_chat_host == "github":
        return ChatOpenAI(
            model=openai_chat_model,
            base_url=os.getenv("GITHUB_MODELS_ENDPOINT", "https://models.github.ai/inference"),
            api_key=api_key,
        )
    elif openai_chat_host == "openai":
        return ChatOpenAI(
            model=openai_chat_model,
            api_key=api_key,
        )
    else:
        raise ValueError(
            f"Unsupported CHAT_MODEL_HOST '{openai_chat_host}'. "
            "Supported values are: 'azure', 'openai', 'ollama', 'github'."
        )


def vector_store_api(connection_string: str, namespace: str, embedding: Embeddings) -> AzureCosmosDBVectorSearch:
    return AzureCosmosDBVectorSearch.from_connection_string(
        connection_string=connection_string,
        namespace=namespace,
        embedding=embedding,
    )


def setup_users_collection(connection_string: str, database_name: str) -> Collection:
    mongo_client: MongoClient = MongoClient(connection_string)
    db = mongo_client[database_name]
    collection: Collection = db["Users"]
    return collection


def setup_data_collection(connection_string: str, database_name: str, collection_name: str) -> Collection:
    try:
        mongo_client: MongoClient = MongoClient(connection_string, serverSelectionTimeoutMS=1000)
        db = mongo_client[database_name]
        collection: Collection = db[collection_name]
        collection.create_index({"textContent": "text"}, name="search_text_index")
        return collection
    except ServerSelectionTimeoutError:
        raise ServerSelectionTimeoutError
