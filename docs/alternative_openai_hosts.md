# Alternative OpenAI hosts

In addition to Azure OpenAI, this project supports using other OpenAI-compatible hosts for both chat and embeddings models. Configure the host using the `OPENAI_CHAT_HOST` and `OPENAI_EMBED_HOST` environment variables.

Supported values: `azure` (default), `openai`, `github`, `ollama`

You can mix hosts — for example, use Azure for embeddings and Ollama for chat.

## OpenAI.com

Use models directly from [OpenAI.com](https://platform.openai.com/):

```env
OPENAI_CHAT_HOST="openai"
OPENAI_EMBED_HOST="openai"
AZURE_OPENAI_API_KEY="<YOUR-OPENAI-COM-API-KEY>"
AZURE_OPENAI_CHAT_MODEL_NAME="gpt-4o-mini"
AZURE_OPENAI_EMBEDDINGS_MODEL_NAME="text-embedding-3-small"
AZURE_OPENAI_EMBEDDINGS_DIMENSIONS="1536"
```

## GitHub Models

Use models from [GitHub Models](https://github.com/marketplace/models):

```env
OPENAI_CHAT_HOST="github"
OPENAI_EMBED_HOST="github"
AZURE_OPENAI_API_KEY="<YOUR-GITHUB-TOKEN>"
AZURE_OPENAI_CHAT_MODEL_NAME="gpt-4o-mini"
AZURE_OPENAI_EMBEDDINGS_MODEL_NAME="text-embedding-3-small"
AZURE_OPENAI_EMBEDDINGS_DIMENSIONS="1536"
```

## Ollama (local models)

Use locally-hosted models via [Ollama](https://ollama.com/):

1. Install and run Ollama.
2. Pull the models you want to use:

    ```bash
    ollama pull llama3.2
    ollama pull nomic-embed-text
    ```

3. Configure the environment variables:

    ```env
    OPENAI_CHAT_HOST="ollama"
    OPENAI_EMBED_HOST="ollama"
    AZURE_OPENAI_ENDPOINT="http://localhost:11434/v1"
    AZURE_OPENAI_CHAT_MODEL_NAME="llama3.2"
    AZURE_OPENAI_EMBEDDINGS_MODEL_NAME="nomic-embed-text"
    AZURE_OPENAI_EMBEDDINGS_DIMENSIONS="768"
    ```

> **Note:** Different embedding models produce different dimension sizes (e.g., `nomic-embed-text` uses 768 dimensions vs. `text-embedding-3-small` at 1536). Set `AZURE_OPENAI_EMBEDDINGS_DIMENSIONS` to match your model's output dimensions. You may need to recreate your vector search index if switching between models with different dimension sizes.
