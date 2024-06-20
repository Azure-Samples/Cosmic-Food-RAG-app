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

export type ResponseMessage = {
    content: string;
    role: string;
};

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

export type ChatAppResponseOrError = {
    message: ResponseMessage;
    context: ResponseContext;
    session_state: string;
    error?: string;
};

export type ChatAppResponse = {
    message: ResponseMessage;
    context: ResponseContext;
    session_state: string | null;
};

export type ChatAppRequestContext = {
    overrides?: ChatAppRequestOverrides;
};

export type ChatAppRequest = {
    messages: ResponseMessage[];
    context?: ChatAppRequestContext;
    session_state: string | null;
};
