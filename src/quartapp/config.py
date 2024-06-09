import json
from typing import Any
from uuid import uuid4

from quartapp.approaches.schemas import Context, DataPoint, JSONDataPoint, Message, RetrievalResponse, Thought
from quartapp.config_base import AppConfigBase


class AppConfig(AppConfigBase):

    async def run_keyword(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse:
        keyword_response, answer = await self.setup.keyword.run(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        if keyword_response is None or len(keyword_response) == 0:
            return RetrievalResponse(
                session_state=new_session_state,
                context=Context(DataPoint([JSONDataPoint()]), [Thought()]),
                delta={"role": "assistant"},
                message=Message(content="No results found", role="assistant"),
            )
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

        thoughts.append(Thought(description=keyword_response[0].metadata.get("source"), title="Source"))

        for res in keyword_response:
            raw_data = json.loads(res.page_content)
            json_data_point: JSONDataPoint = JSONDataPoint()
            json_data_point.name = raw_data.get("name")
            json_data_point.description = raw_data.get("description")
            json_data_point.price = raw_data.get("price")
            json_data_point.category = raw_data.get("category")
            json_data_point.collection = self.setup._database_setup._collection_name
            data_points.json.append(json_data_point)

        context: Context = Context(data_points=data_points, thoughts=thoughts)

        delta: dict[str, Any] = {"role": "assistant"}
        message: Message = Message(content=message_content, role="assistant")

        self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )

        return RetrievalResponse(context, delta, message, new_session_state)

    async def run_vector(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse:
        vector_response, answer = await self.setup.vector_search.run(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        if vector_response is None or len(vector_response) == 0:
            return RetrievalResponse(
                session_state=new_session_state,
                context=Context(DataPoint([JSONDataPoint()]), [Thought()]),
                delta={"role": "assistant"},
                message=Message(content="No results found", role="assistant"),
            )
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

        delta: dict[str, Any] = {"role": "assistant"}
        message: Message = Message(content=message_content, role="assistant")

        self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )

        return RetrievalResponse(context, delta, message, new_session_state)

    async def run_rag(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse:
        rag_response, answer = await self.setup.rag.run(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        if rag_response is None or len(rag_response) == 0:
            if answer:
                return RetrievalResponse(
                    session_state=new_session_state,
                    context=Context(DataPoint([JSONDataPoint()]), [Thought()]),
                    delta={"role": "assistant"},
                    message=Message(content=answer, role="assistant"),
                )
            else:
                return RetrievalResponse(
                    session_state=new_session_state,
                    context=Context(DataPoint([JSONDataPoint()]), [Thought()]),
                    delta={"role": "assistant"},
                    message=Message(content="No results found", role="assistant"),
                )

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

        delta: dict[str, Any] = {"role": "assistant"}
        message: Message = Message(content=answer, role="assistant")

        self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )

        return RetrievalResponse(context, delta, message, new_session_state)
