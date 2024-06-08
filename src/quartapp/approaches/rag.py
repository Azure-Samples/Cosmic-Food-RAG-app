from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from quartapp.approaches.base import ApproachesBase

chat_history_prompt = """\
Given the following conversation and a follow up question, rephrase the follow up \
question to be a standalone question.

Chat History:
{messages}

Standalone Question:"""

context_prompt = """You are a chatbot that can have a conversation about Food dishes from the context.
Answer the following question based only on the provided context:

Context:
{context}

Question: {input}"""


class RAG(ApproachesBase):
    async def run(
        self, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> tuple[list[Document], str]:
        if messages:
            # Create a vector store retriever
            retriever = self._vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": limit, "score_threshold": score_threshold}
            )

            self._chat.temperature = 0.3

            # Create a vector context aware chat retriever
            history_prompt_template = ChatPromptTemplate.from_template(chat_history_prompt)
            history_chain = history_prompt_template | self._chat

            # Rephrase the question
            rephrased_question = await history_chain.ainvoke(messages)

            print(rephrased_question.content)
            # Perform vector search
            vector_context = await retriever.ainvoke(rephrased_question.content)

            # Create a vector context aware chat retriever
            context_prompt_template = ChatPromptTemplate.from_template(context_prompt)
            document_chain = create_stuff_documents_chain(self._chat, context_prompt_template)

            self._chat.temperature = temperature

            if vector_context:
                # Perform RAG search
                response = await document_chain.ainvoke(
                    {"context": vector_context, "input": rephrased_question.content}
                )

                return vector_context, response

            # Perform RAG search with no context
            response = await document_chain.ainvoke({"context": vector_context, "input": rephrased_question.content})
            return [], response
        return [], ""
