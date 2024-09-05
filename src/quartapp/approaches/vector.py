from langchain_core.documents import Document

from quartapp.approaches.base import ApproachesBase


class Vector(ApproachesBase):
    async def run(
        self, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> tuple[list[Document], str]:
        query = messages[-1]["content"]
        retriever = self._vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": limit, "score_threshold": score_threshold}
        )
        vector_response = await retriever.ainvoke(query)
        documents_list: list[Document] = []

        if vector_response:
            for document in vector_response:
                documents_list.append(
                    Document(page_content=document.page_content, metadata={"source": document.metadata["source"]})
                )
            if documents_list:
                return documents_list, documents_list[0].page_content
        return [], ""
