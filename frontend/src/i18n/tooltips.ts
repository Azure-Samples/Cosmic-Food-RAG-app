// Keep values less than 20 words.
// Don't add links to the tooltips.
export const toolTipText = {
    promptTemplate: "Overrides the prompt used to generate the answer based on the question and search results.",
    temperature:
        "Sets the temperature of the request to the LLM that generates the answer. Higher temperatures result in more creative responses, but they may be less grounded.",
    searchScore: "Sets a minimum score for search results coming back from Azure Cosmos DB for MongoDB vCore.",
    retrieveNumber:
        "Sets the number of search results to retrieve from Azure Cosmos DB for MongoDB vCore. More results may increase the likelihood of finding the correct answer, but may lead to the model getting 'lost in the middle'.",
    retrievalMode:
        "Sets the retrieval mode for the Azure Cosmos DB for MongoDB vCore query. `RAG with Vector Search` uses a combination of vector search and LLM rephrasing, `Vectors` uses only vector search, and `Text` uses only full text search.",
    streamChat: "Continuously streams the response to the chat UI as it is generated."
};
