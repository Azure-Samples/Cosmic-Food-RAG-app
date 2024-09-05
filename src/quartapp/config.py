import json
from collections.abc import AsyncGenerator
from uuid import uuid4

from quartapp.approaches.schemas import (
    AIChatRoles,
    Context,
    DataPoint,
    Message,
    RetrievalResponse,
    RetrievalResponseDelta,
    Thought,
)
from quartapp.config_base import AppConfigBase


class AppConfig(AppConfigBase):
    async def run_keyword(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse:
        keyword_response, answer = await self.setup.keyword.run(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        if keyword_response is None or len(keyword_response) == 0:
            return RetrievalResponse(
                sessionState=new_session_state,
                context=Context([DataPoint()], [Thought()]),
                message=Message(content="No results found", role=AIChatRoles.ASSISTANT),
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
        context.thoughts.insert(0, Thought(description=answer, title="Cosmos Text Search Top Result"))
        context.thoughts.insert(0, Thought(description=str(keyword_response), title="Cosmos Text Search Result"))
        context.thoughts.insert(0, Thought(description=messages[-1]["content"], title="Cosmos Text Search Query"))
        message: Message = Message(content=message_content, role=AIChatRoles.ASSISTANT)

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
                sessionState=new_session_state,
                context=Context([DataPoint()], [Thought()]),
                message=Message(content="No results found", role=AIChatRoles.ASSISTANT),
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
        context.thoughts.insert(0, Thought(description=answer, title="Cosmos Vector Search Top Result"))
        context.thoughts.insert(0, Thought(description=str(vector_response), title="Cosmos Vector Search Result"))
        context.thoughts.insert(0, Thought(description=messages[-1]["content"], title="Cosmos Vector Search Query"))
        message: Message = Message(content=message_content, role=AIChatRoles.ASSISTANT)

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
        json_answer = json.loads(answer)

        new_session_state: str = session_state if session_state else str(uuid4())

        if rag_response is None or len(rag_response) == 0:
            if answer:
                return RetrievalResponse(
                    sessionState=new_session_state,
                    context=Context([DataPoint()], [Thought()]),
                    message=Message(content=json_answer.get("response"), role=AIChatRoles.ASSISTANT),
                )
            else:
                return RetrievalResponse(
                    sessionState=new_session_state,
                    context=Context([DataPoint()], [Thought()]),
                    message=Message(content="No results found", role=AIChatRoles.ASSISTANT),
                )

        context: Context = await self.get_context(rag_response)
        context.thoughts.insert(
            0, Thought(description=json_answer.get("response"), title="Cosmos RAG OpenAI Rephrased Response")
        )
        context.thoughts.insert(
            0, Thought(description=str(rag_response), title="Cosmos RAG Search Vector Search Result")
        )
        context.thoughts.insert(
            0, Thought(description=json_answer.get("rephrased_response"), title="Cosmos RAG OpenAI Rephrased Query")
        )
        context.thoughts.insert(0, Thought(description=messages[-1]["content"], title="Cosmos RAG Query"))
        message: Message = Message(content=json_answer.get("response"), role=AIChatRoles.ASSISTANT)

        await self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )

        return RetrievalResponse(context, message, new_session_state)

    async def run_rag_stream(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> AsyncGenerator[RetrievalResponseDelta, None]:
        rag_response, answer = await self.setup.rag.run_stream(messages, temperature, limit, score_threshold)

        new_session_state: str = session_state if session_state else str(uuid4())

        context: Context = await self.get_context(rag_response)
        context.thoughts.insert(
            0, Thought(description=str(rag_response), title="Cosmos RAG Search Vector Search Result")
        )
        context.thoughts.insert(0, Thought(description=messages[-1]["content"], title="Cosmos RAG Query"))

        yield RetrievalResponseDelta(context=context, sessionState=new_session_state)

        async for message_chunk in answer:
            message: Message = Message(content=str(message_chunk.content), role=AIChatRoles.ASSISTANT)
            yield RetrievalResponseDelta(
                delta=message,
            )

        await self.add_to_cosmos(
            old_messages=messages,
            new_message=message.to_dict(),
            session_state=session_state,
            new_session_state=new_session_state,
        )
