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

export type JSONDataPoint = {
    name: string;
    description: string;
    price: string;
    category: string;
    collection: string;
};

export type Thoughts = {
    title: string;
    description: any; // It can be any output from the api
    props?: { [key: string]: string };
};

export type DataPoint = {
    json: JSONDataPoint[];
};

export type ResponseContext = {
    data_points: DataPoint;
    thoughts: Thoughts[];
};

export type ResponseChoice = {
    index: number;
    message: ResponseMessage;
    context: ResponseContext;
    session_state: string;
};

export type ChatAppResponseOrError = {
    choices?: ResponseChoice[];
    error?: string;
};

export type ChatAppResponse = {
    choices: ResponseChoice[];
};

export type ChatAppRequestContext = {
    overrides?: ChatAppRequestOverrides;
};

export type ChatAppRequest = {
    messages: ResponseMessage[];
    context?: ChatAppRequestContext;
    session_state: string | null;
};
