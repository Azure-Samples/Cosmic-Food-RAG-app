#!/usr/bin/env python3

import json
import logging
import os
from argparse import ArgumentParser, Namespace

from langchain.docstore.document import Document
from langchain_community.vectorstores.azure_cosmos_db import (
    AzureCosmosDBVectorSearch,
    CosmosDBSimilarityType,
    CosmosDBVectorSearchType,
)
from langchain_openai import AzureOpenAIEmbeddings
from pymongo import MongoClient
from pymongo.collection import Collection

from quartapp.approaches.setup import Setup
from quartapp.config import AppConfig

setup: Setup = AppConfig().setup


logging.basicConfig(
    handlers=[logging.StreamHandler()],
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    level=logging.INFO,
)


def read_data(file_path: str) -> list[Document]:
    # Load JSON file
    with open(file_path) as file:
        json_data = json.load(file)

    documents = []
    absolute_path = os.path.abspath(file_path)
    # Process each item in the JSON data
    for idx, item in enumerate(json_data):
        documents.append(
            Document(page_content=json.dumps(item), metadata={"source": absolute_path, "seq_num": idx + 1})
        )
    return documents


async def generate_embeddings_and_add_data(
    documents: list[Document],
    collection: Collection,
    index_name: str,
    embeddings: AzureOpenAIEmbeddings,
) -> AzureCosmosDBVectorSearch:
    # Create embeddings from the data, save to the database and return a connection to MongoDB vCore
    return await AzureCosmosDBVectorSearch.afrom_documents(
        documents=documents,
        embedding=embeddings,
        collection=collection,
        index_name=index_name,
    )


async def add_data(input_args: Namespace) -> None:
    documents = read_data(input_args.file)

    logging.info("✨ Successfully Read the data...")

    mongo_client: MongoClient = MongoClient(setup._database_setup._connection_string)

    # Create the database
    db = mongo_client[setup._database_setup._database_name]

    # Create the collection
    collection: Collection = db[setup._database_setup._collection_name]

    vector_store = await generate_embeddings_and_add_data(
        documents=documents,
        collection=collection,
        index_name=setup._database_setup._index_name,
        embeddings=setup._openai_setup._embeddings_api,
    )

    logging.info("✨ Successfully Created the Collection, Embeddings and Added the Data the Collection...")

    # Read more about these variables in detail here. https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/vcore/vector-search
    num_lists = 100
    dimensions = 1536
    similarity_algorithm = CosmosDBSimilarityType.COS
    kind = CosmosDBVectorSearchType.VECTOR_HNSW
    m = 16
    ef_construction = 64

    # Create the index overt the collection
    index_creation = vector_store.create_index(num_lists, dimensions, similarity_algorithm, kind, m, ef_construction)

    logging.info(f"✨ Successfully Created the HNSW Index Over the data...{index_creation}")
    logging.info("✅✅ Done! ✅✅")


def get_input_args() -> Namespace:
    # Parse using ArgumentParser
    parser = ArgumentParser()

    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default="./data/food_items.json",
        help="path to the JSON file containing the data",
    )

    return parser.parse_args()


if __name__ == "__main__":
    import asyncio

    input_args = get_input_args()
    asyncio.run(add_data(input_args))
