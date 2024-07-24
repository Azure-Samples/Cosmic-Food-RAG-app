import { AIChatCompletion, AIChatCompletionDelta, AIChatCompletionOperationOptions } from "@microsoft/ai-chat-protocol";

export const enum RetrievalMode {
    Hybrid = "rag",
    Vectors = "vector",
    Text = "keyword"
}

export type ChatAppRequestOverrides = {
    retrieval_mode?: RetrievalMode;
    top?: number;
    temperature?: number;
    score_threshold?: number;
};

export type ChatAppRequestContext = {
    overrides: ChatAppRequestOverrides;
};

export interface ChatAppRequestOptions extends AIChatCompletionOperationOptions {
    context: ChatAppRequestContext;
}

export type Thought = {
    title: string;
    description: string;
};

export type DataPoint = {
    name: string;
    description: string;
    price: string;
    category: string;
    collection: string;
};

export type ResponseContext = {
    data_points: DataPoint[];
    thoughts: Thought[];
};

export interface ChatCompletionResponse extends AIChatCompletion {
    context: ResponseContext;
}

export interface ChatCompletionDeltaResponse extends AIChatCompletionDelta {
    context: ResponseContext;
}
