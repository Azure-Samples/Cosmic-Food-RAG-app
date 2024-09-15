from langchain_community.vectorstores import AzureCosmosDBVectorSearch
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
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
) -> AzureOpenAIEmbeddings:
    return AzureOpenAIEmbeddings(
        model=openai_embeddings_model,
        azure_deployment=openai_embeddings_deployment,
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
    )


def chat_api(
    openai_chat_model: str, openai_chat_deployment: str, api_key: SecretStr, api_version: str, azure_endpoint: str
) -> AzureChatOpenAI:
    return AzureChatOpenAI(
        model=openai_chat_model,
        azure_deployment=openai_chat_deployment,
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=azure_endpoint,
    )


def vector_store_api(
    connection_string: str, namespace: str, embedding: AzureOpenAIEmbeddings
) -> AzureCosmosDBVectorSearch:
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
