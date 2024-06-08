const BACKEND_URI = "";

import { ChatAppRequest, ChatAppResponse, ChatAppResponseOrError } from "./models";

export async function chatApi(request: ChatAppRequest): Promise<ChatAppResponse> {
    const response = await fetch(`${BACKEND_URI}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request)
    });
    if (!response.body) {
        throw Error("No response body");
    }
    const parsedResponse: ChatAppResponseOrError = await response.json();

    if (response.status > 299 || !response.ok) {
        throw Error(parsedResponse.error || "Unknown error");
    }
    return parsedResponse as ChatAppResponse;
}

export async function chatStreamApi(request: ChatAppRequest): Promise<Response> {
    return await fetch(`${BACKEND_URI}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request)
    });
}
