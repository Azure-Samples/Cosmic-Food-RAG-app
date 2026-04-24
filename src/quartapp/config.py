import json
from collections.abc import AsyncGenerator
from uuid import uuid4

from pymongo.errors import OperationFailure

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

MISSING_SIMILARITY_INDEX_ERROR = "Similarity index was not found for a vector similarity search query."


def is_missing_similarity_index_error(error: OperationFailure) -> bool:
    return error.code == 2 and MISSING_SIMILARITY_INDEX_ERROR in str(error)


class AppConfig(AppConfigBase):
    def _no_results_context(self) -> Context:
        return Context([DataPoint()], [Thought()])

    def _no_results_response(self, session_state: str) -> RetrievalResponse:
        return RetrievalResponse(
            sessionState=session_state,
            context=self._no_results_context(),
            message=Message(content="No results found", role=AIChatRoles.ASSISTANT),
        )

    async def run_keyword(
        self, session_state: str | None, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> RetrievalResponse:
        new_session_state: str = session_state if session_state else str(uuid4())

        try:
            keyword_response, answer = await self.setup.keyword.run(messages, temperature, limit, score_threshold)
        except OperationFailure:
            return self._no_results_response(new_session_state)

        if keyword_response is None or len(keyword_response) == 0:
            return self._no_results_response(new_session_state)
        top_result = json.loads(answer)

        message_content = f"""
            Name: {top_result.get("name")}
            Description: {top_result.get("description")}
            Price: {top_result.get("price")}
            Category: {top_result.get("category")}
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
        new_session_state: str = session_state if session_state else str(uuid4())

        try:
            vector_response, answer = await self.setup.vector_search.run(messages, temperature, limit, score_threshold)
        except OperationFailure:
            return self._no_results_response(new_session_state)

        if vector_response is None or len(vector_response) == 0:
            return self._no_results_response(new_session_state)
        top_result = json.loads(answer)

        message_content = f"""
            Name: {top_result.get("name")}
            Description: {top_result.get("description")}
            Price: {top_result.get("price")}
            Category: {top_result.get("category")}
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
        new_session_state: str = session_state if session_state else str(uuid4())

        try:
            rag_response, answer = await self.setup.rag.run(messages, temperature, limit, score_threshold)
        except OperationFailure as error:
            if not is_missing_similarity_index_error(error):
                raise
            return self._no_results_response(new_session_state)

        json_answer = json.loads(answer)

        if rag_response is None or len(rag_response) == 0:
            if answer:
                return RetrievalResponse(
                    sessionState=new_session_state,
                    context=self._no_results_context(),
                    message=Message(content=json_answer.get("response"), role=AIChatRoles.ASSISTANT),
                )
            else:
                return self._no_results_response(new_session_state)

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
        new_session_state: str = session_state if session_state else str(uuid4())

        try:
            rag_response, answer = await self.setup.rag.run_stream(messages, temperature, limit, score_threshold)
        except OperationFailure as error:
            if not is_missing_similarity_index_error(error):
                raise

            yield RetrievalResponseDelta(context=self._no_results_context(), sessionState=new_session_state)
            yield RetrievalResponseDelta(delta=Message(content="No results found", role=AIChatRoles.ASSISTANT))
            return

        context: Context = await self.get_context(rag_response)
        context.thoughts.insert(
            0, Thought(description=str(rag_response), title="Cosmos RAG Search Vector Search Result")
        )
        context.thoughts.insert(0, Thought(description=messages[-1]["content"], title="Cosmos RAG Query"))

        yield RetrievalResponseDelta(context=context, sessionState=new_session_state)

        full_message_content = ""
        async for message_chunk in answer:
            chunk_content = str(message_chunk.content)
            full_message_content += chunk_content
            message = Message(content=chunk_content, role=AIChatRoles.ASSISTANT)
            yield RetrievalResponseDelta(delta=message)

        # Only save to Cosmos if we have content
        if full_message_content:
            full_message = Message(content=full_message_content, role=AIChatRoles.ASSISTANT)
            await self.add_to_cosmos(
                old_messages=messages,
                new_message=full_message.to_dict(),
                session_state=session_state,
                new_session_state=new_session_state,
            )
