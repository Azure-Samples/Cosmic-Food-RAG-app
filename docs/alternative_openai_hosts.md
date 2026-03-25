# Alternative OpenAI hosts

In addition to Azure OpenAI, this project supports using other OpenAI-compatible hosts for both chat and embeddings models. Configure the host using the `CHAT_MODEL_HOST` and `EMBED_MODEL_HOST` environment variables.

Supported values: `azure` (default), `openai`, `github`, `ollama`

You can mix hosts — for example, use Azure for embeddings and Ollama for chat.

## Azure OpenAI (default)

The default host uses [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/overview). No additional configuration is needed if you deploy using `azd up`.

For more information:

- [Azure OpenAI Service documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure OpenAI quickstart](https://learn.microsoft.com/azure/ai-services/openai/chatgpt-quickstart)
- [Azure OpenAI models](https://learn.microsoft.com/azure/ai-services/openai/concepts/models)

## OpenAI.com

Use models directly from [OpenAI](https://platform.openai.com/). You will need an [OpenAI API key](https://platform.openai.com/api-keys).

For more information:

- [OpenAI API documentation](https://platform.openai.com/docs/api-reference)
- [OpenAI models](https://platform.openai.com/docs/models)
- [OpenAI embeddings guide](https://platform.openai.com/docs/guides/embeddings)

```env
CHAT_MODEL_HOST="openai"
EMBED_MODEL_HOST="openai"
AZURE_OPENAI_API_KEY="<YOUR-OPENAI-COM-API-KEY>"
AZURE_OPENAI_CHAT_MODEL_NAME="gpt-4o-mini"
AZURE_OPENAI_EMBEDDINGS_MODEL_NAME="text-embedding-3-small"
AZURE_OPENAI_EMBEDDINGS_DIMENSIONS="1536"
```

## GitHub Models

Use models from [GitHub Models](https://github.com/marketplace/models). You will need a [GitHub personal access token](https://docs.github.com/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

For more information:

- [GitHub Models documentation](https://docs.github.com/github-models)
- [GitHub Models marketplace](https://github.com/marketplace/models)
- [Getting started with GitHub Models](https://docs.github.com/github-models/prototyping-with-ai-models)

```env
CHAT_MODEL_HOST="github"
EMBED_MODEL_HOST="github"
AZURE_OPENAI_API_KEY="<YOUR-GITHUB-TOKEN>"
AZURE_OPENAI_CHAT_MODEL_NAME="gpt-4o-mini"
AZURE_OPENAI_EMBEDDINGS_MODEL_NAME="text-embedding-3-small"
AZURE_OPENAI_EMBEDDINGS_DIMENSIONS="1536"
```

## Ollama (local models)

Use locally-hosted models via [Ollama](https://ollama.com/). This is useful for development and testing without cloud API costs.

For more information:

- [Ollama documentation](https://github.com/ollama/ollama/blob/main/README.md)
- [Ollama model library](https://ollama.com/library)
- [Ollama OpenAI compatibility](https://github.com/ollama/ollama/blob/main/docs/openai.md)
- [Tips for Ollama-compatible RAG apps](https://blog.pamelafox.org/2024/08/making-ollama-compatible-rag-app.html)

### Setup

1. Install and run Ollama by following the instructions at [ollama.com/download](https://ollama.com/download).
2. Pull the models you want to use:

    ```bash
    ollama pull llama3.2
    ollama pull nomic-embed-text
    ```

3. Configure the environment variables:

    ```env
    CHAT_MODEL_HOST="ollama"
    EMBED_MODEL_HOST="ollama"
    OLLAMA_ENDPOINT="http://localhost:11434/v1"
    AZURE_OPENAI_CHAT_MODEL_NAME="llama3.2"
    AZURE_OPENAI_EMBEDDINGS_MODEL_NAME="nomic-embed-text"
    AZURE_OPENAI_EMBEDDINGS_DIMENSIONS="768"
    ```

### Embedding dimensions

Different embedding models produce different dimension sizes (e.g., `nomic-embed-text` uses 768 dimensions vs. `text-embedding-3-small` at 1536). Set `AZURE_OPENAI_EMBEDDINGS_DIMENSIONS` to match your model's output dimensions. You may need to recreate your vector search index if switching between models with different dimension sizes.
