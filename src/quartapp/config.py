import json
from collections.abc import AsyncGenerator
from uuid import uuid4

from quartapp.approaches.schemas import Context, DataPoint, Message, RetrievalResponse, Thought
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
                context=Context([DataPoint()], [Thought()]),
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

        context: Context = await self.get_context(keyword_response)

        message: Message = Message(content=message_content, role="assistant")

        await self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )

        return RetrievalResponse(context, message, new_session_state)

    async def run_vector(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse:
        vector_response, answer = await self.setup.vector_search.run(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        if vector_response is None or len(vector_response) == 0:
            return RetrievalResponse(
                session_state=new_session_state,
                context=Context([DataPoint()], [Thought()]),
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

        context: Context = await self.get_context(vector_response)
        message: Message = Message(content=message_content, role="assistant")

        await self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )

        return RetrievalResponse(context, message, new_session_state)

    async def run_rag(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse:
        rag_response, answer = await self.setup.rag.run(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        if rag_response is None or len(rag_response) == 0:
            if answer:
                return RetrievalResponse(
                    session_state=new_session_state,
                    context=Context([DataPoint()], [Thought()]),
                    message=Message(content=answer, role="assistant"),
                )
            else:
                return RetrievalResponse(
                    session_state=new_session_state,
                    context=Context([DataPoint()], [Thought()]),
                    message=Message(content="No results found", role="assistant"),
                )

        context: Context = await self.get_context(rag_response)
        message: Message = Message(content=answer, role="assistant")

        await self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )

        return RetrievalResponse(context, message, new_session_state)

    async def run_rag_stream(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> AsyncGenerator[RetrievalResponse | Message, None]:
        rag_response, answer = await self.setup.rag.run_stream(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        context: Context = await self.get_context(rag_response)

        empty_message: Message = Message(content="", role="assistant")

        yield RetrievalResponse(context, empty_message, new_session_state)

        async for message_chunk in answer:
            message: Message = Message(content=str(message_chunk.content), role="assistant")
            yield message

        await self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )
