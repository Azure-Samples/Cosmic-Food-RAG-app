import json
from collections.abc import AsyncIterator

from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

from quartapp.approaches.base import ApproachesBase
from quartapp.approaches.schemas import DataPoint


def get_data_points(documents: list[Document]) -> list[DataPoint]:
    data_points: list[DataPoint] = []

    for res in documents:
        raw_data = json.loads(res.page_content)
        json_data_point: DataPoint = DataPoint()
        json_data_point.name = raw_data.get("name")
        json_data_point.description = raw_data.get("description")
        json_data_point.price = raw_data.get("price")
        json_data_point.category = raw_data.get("category")
        data_points.append(json_data_point)
    return data_points


REPHRASE_PROMPT = """\
Given the following conversation and a follow up question, rephrase the follow up \
question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone Question:"""

CONTEXT_PROMPT = """\
You are a restaurant chatbot, tasked with answering any question about \
food dishes from the contex.

Generate a response of 80 words or less for the \
given question based solely on the provided search results (name, description, price, and category). \
You must only use information from the provided search results. Use an unbiased and \
fun tone. Do not repeat text. Your response must be solely based on the provided context.

If there is nothing in the context relevant to the question at hand, just say "Hmm, \
I'm not sure." Don't try to make up an answer.

Anything between the following `context` html blocks is retrieved from a knowledge \
bank, not part of the conversation with the user.

<context>
    {context}
<context/>

REMEMBER: If there is no relevant information within the context, just say "Hmm, I'm \
not sure." Don't try to make up an answer. Anything between the preceding 'context' \
html blocks is retrieved from a knowledge bank, not part of the conversation with the \
user.\

User Question: {input}

Chatbot Response:"""


class RAG(ApproachesBase):
    async def run(
        self, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> tuple[list[Document], str]:
        # Create a vector store retriever
        retriever = self._vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": limit, "score_threshold": score_threshold}
        )

        self._chat.temperature = 0.3

        # Create a vector context aware chat retriever
        rephrase_prompt_template = ChatPromptTemplate.from_template(REPHRASE_PROMPT)
        rephrase_chain = rephrase_prompt_template | self._chat

        # Rephrase the question
        rephrased_question = await rephrase_chain.ainvoke({"chat_history": messages[:-1], "question": messages[-1]})

        print(rephrased_question.content)
        # Perform vector search
        vector_context = await retriever.ainvoke(str(rephrased_question.content))
        data_points: list[DataPoint] = get_data_points(vector_context)

        # Create a vector context aware chat retriever
        context_prompt_template = ChatPromptTemplate.from_template(CONTEXT_PROMPT)
        self._chat.temperature = temperature
        context_chain = context_prompt_template | self._chat
        documents_list: list[Document] = []
        if data_points:
            # Perform RAG search
            response = await context_chain.ainvoke(
                {"context": [dp.to_dict() for dp in data_points], "input": rephrased_question.content}
            )
            for document in vector_context:
                documents_list.append(
                    Document(page_content=document.page_content, metadata={"source": document.metadata["source"]})
                )
            formatted_response = (
                f'{{"response": "{response.content}", "rephrased_response": "{rephrased_question.content}"}}'
            )
            return documents_list, str(formatted_response)

        # Perform RAG search with no context
        response = await context_chain.ainvoke({"context": [], "input": rephrased_question.content})
        return [], str(response.content)

    async def run_stream(
        self, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> tuple[list[Document], AsyncIterator[BaseMessage]]:
        # Create a vector store retriever
        retriever = self._vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": limit, "score_threshold": score_threshold}
        )

        self._chat.temperature = 0.3

        # Create a vector context aware chat retriever
        rephrase_prompt_template = ChatPromptTemplate.from_template(REPHRASE_PROMPT)
        rephrase_chain = rephrase_prompt_template | self._chat

        # Rephrase the question
        rephrased_question = await rephrase_chain.ainvoke({"chat_history": messages[:-1], "question": messages[-1]})

        print(rephrased_question.content)
        # Perform vector search
        vector_context = await retriever.ainvoke(str(rephrased_question.content))
        data_points: list[DataPoint] = get_data_points(vector_context)

        # Create a vector context aware chat retriever
        context_prompt_template = ChatPromptTemplate.from_template(CONTEXT_PROMPT)
        self._chat.temperature = temperature
        context_chain = context_prompt_template | self._chat
        documents_list: list[Document] = []

        if data_points:
            # Perform RAG search
            response = context_chain.astream(
                {"context": [dp.to_dict() for dp in data_points], "input": rephrased_question.content}
            )
            for document in vector_context:
                documents_list.append(
                    Document(page_content=document.page_content, metadata={"source": document.metadata["source"]})
                )
            return documents_list, response

        # Perform RAG search with no context
        response = context_chain.astream({"context": [], "input": rephrased_question.content})
        return [], response
