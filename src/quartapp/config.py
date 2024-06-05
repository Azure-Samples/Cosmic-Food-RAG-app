import json
import os
from uuid import uuid4

from pydantic.v1 import SecretStr
from pymongo.errors import (
    ConfigurationError,
    InvalidName,
    InvalidOperation,
    OperationFailure,
)

from quartapp.approaches.schemas import Context, DataPoint, JSONDataPoint, Message, RetrievalResponse, Thought
from quartapp.approaches.setup import Setup


class AppConfig:
    def __init__(self) -> None:
        openai_embeddings_model = os.getenv("AZURE_OPENAI_EMBEDDINGS_MODEL_NAME", "text-embedding-ada-002")
        openai_embeddings_deployment = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME", "text-embedding")
        openai_chat_model = os.getenv("AZURE_OPENAI_CHAT_MODEL_NAME", "gpt-35-turbo")
        openai_chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "chat-gpt")
        connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING", "<YOUR-COSMOS-DB-CONNECTION-STRING>")
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

    def add_to_cosmos(
        self, old_messages: list, new_message: dict, session_state: str | None, new_session_state: str
    ) -> bool:
        is_first_message: bool = True if not session_state else False
        if is_first_message:
            try:
                if len(old_messages) == 0 or len(new_message) == 0 or len(new_session_state) == 0:
                    raise IndexError
                old_messages.append(new_message)
                self.setup._database_setup._users_collection.insert_one(
                    {"_id": new_session_state, "messages": old_messages}
                )
                return True
            except (AttributeError, ConfigurationError, InvalidName, InvalidOperation, OperationFailure, IndexError):
                return False
        else:
            try:
                if len(old_messages) == 0 or len(new_message) == 0 or len(new_session_state) == 0:
                    raise IndexError
                self.setup._database_setup._users_collection.update_one(
                    {"_id": new_session_state}, {"$push": {"messages": old_messages[-1]}}
                )
                self.setup._database_setup._users_collection.update_one(
                    {"_id": new_session_state}, {"$push": {"messages": new_message}}
                )
                return True
            except (AttributeError, ConfigurationError, InvalidName, InvalidOperation, OperationFailure, IndexError):
                return False

    async def run_vector(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> list[RetrievalResponse]:
        vector_response, answer = await self.setup.vector_search.run(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        if vector_response is None or len(vector_response) == 0:
            return [
                RetrievalResponse(
                    session_state=new_session_state,
                    context=Context(DataPoint([JSONDataPoint()]), [Thought()]),
                    index=0,
                    message=Message(content="No results found", role="assistant"),
                )
            ]
        top_result = json.loads(answer)

        message_content = f"""
            Name: {top_result.get('name')}
            Description: {top_result.get('description')}
            Price: {top_result.get('price')}
            Category: {top_result.get('category')}
            Collection: {self.setup._database_setup._collection_name}
        """

        data_points: DataPoint = DataPoint(json=[])
        thoughts: list[Thought] = []

        thoughts.append(Thought(description=vector_response[0].metadata.get("source"), title="Source"))

        for res in vector_response:
            raw_data = json.loads(res.page_content)
            json_data_point: JSONDataPoint = JSONDataPoint()
            json_data_point.name = raw_data.get("name")
            json_data_point.description = raw_data.get("description")
            json_data_point.price = raw_data.get("price")
            json_data_point.category = raw_data.get("category")
            json_data_point.collection = self.setup._database_setup._collection_name
            data_points.json.append(json_data_point)

        context: Context = Context(data_points=data_points, thoughts=thoughts)

        index: int = vector_response[0].metadata.get("seq_num", 0)
        message: Message = Message(content=message_content, role="assistant")

        self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )

        return [RetrievalResponse(context, index, message, new_session_state)]

    async def run_rag(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> list[RetrievalResponse]:
        rag_response, answer = await self.setup.rag.run(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        if rag_response is None or len(rag_response) == 0:
            if answer:
                return [
                    RetrievalResponse(
                        session_state=new_session_state,
                        context=Context(DataPoint([JSONDataPoint()]), [Thought()]),
                        index=0,
                        message=Message(content=answer, role="assistant"),
                    )
                ]
            else:
                return [
                    RetrievalResponse(
                        session_state=new_session_state,
                        context=Context(DataPoint([JSONDataPoint()]), [Thought()]),
                        index=0,
                        message=Message(content="No results found", role="assistant"),
                    )
                ]

        data_points: DataPoint = DataPoint(json=[])
        thoughts: list[Thought] = []

        thoughts.append(Thought(description=rag_response[0].metadata.get("source"), title="Source"))

        for res in rag_response:
            raw_data = json.loads(res.page_content)
            json_data_point: JSONDataPoint = JSONDataPoint()
            json_data_point.name = raw_data.get("name")
            json_data_point.description = raw_data.get("description")
            json_data_point.price = raw_data.get("price")
            json_data_point.category = raw_data.get("category")
            json_data_point.collection = self.setup._database_setup._collection_name
            data_points.json.append(json_data_point)

        context: Context = Context(data_points=data_points, thoughts=thoughts)

        index: int = rag_response[0].metadata.get("seq_num", 0)
        message: Message = Message(content=answer, role="assistant")

        self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )

        return [RetrievalResponse(context, index, message, new_session_state)]

    async def run_keyword(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> list[RetrievalResponse]:
        keyword_response = None

        new_session_state: str = session_state if session_state else str(uuid4())

        if keyword_response is None or len(keyword_response) == 0:
            return [
                RetrievalResponse(
                    session_state=new_session_state,
                    context=Context(DataPoint([JSONDataPoint()]), [Thought()]),
                    index=0,
                    message=Message(content="No results found", role="assistant"),
                )
            ]
