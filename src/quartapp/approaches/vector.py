from langchain_core.documents import Document

from quartapp.approaches.base import ApproachesBase


class Vector(ApproachesBase):
    async def run(
        self, messages: list, temperature: float, limit: int, score_threshold: float
    ) -> tuple[list[Document], str]:
        if messages:
            query = messages[-1]["content"]
            retriever = self._vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": limit, "score_threshold": score_threshold}
            )
            vector_response = await retriever.ainvoke(query)
            if vector_response:
                return vector_response, vector_response[0].page_content
        return [], ""
