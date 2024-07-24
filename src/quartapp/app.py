import logging
from collections.abc import AsyncGenerator
from json import dumps
from pathlib import Path
from typing import Any

from quart import Quart, Response, jsonify, make_response, request, send_file, send_from_directory

from quartapp.approaches.schemas import RetrievalResponse, RetrievalResponseDelta
from quartapp.config import AppConfig

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def format_as_ndjson(r: AsyncGenerator[RetrievalResponseDelta, None]) -> AsyncGenerator[str, None]:
    """
    Format the response as NDJSON
    """
    try:
        async for event in r:
            yield dumps(event.to_dict(), ensure_ascii=False) + "\n"
    except Exception as error:
        logging.exception("Exception while generating response stream: %s", error)
        yield dumps({"error": str(error)}, ensure_ascii=False) + "\n"


def create_app(test_config: dict[str, Any] | None = None) -> Quart:
    app_config = AppConfig()

    app = Quart(__name__, static_folder="static")

    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    available_approaches = {
        "vector": app_config.run_vector,
        "rag": app_config.run_rag,
        "keyword": app_config.run_keyword,
    }

    @app.route("/")
    async def index() -> Any:
        return await send_file(Path(__file__).resolve().parent / "static/index.html")

    @app.route("/favicon.ico")
    async def favicon() -> Any:
        return await send_file(Path(__file__).resolve().parent / "static/favicon.ico")

    @app.route("/assets/<path:path>")
    async def assets(path: str) -> Any:
        if (Path(__file__).resolve().parent / "static" / "assets" / path).exists():
            return await send_from_directory(Path(__file__).resolve().parent / "static" / "assets", path)
        return jsonify({"error": "Not Found"}), 404

    @app.route("/hello", methods=["GET"])
    async def hello() -> Response:
        return jsonify({"answer": "Hello, World!"})

    @app.route("/chat", methods=["POST"])
    async def chat() -> Any:
        if not request.is_json:
            return jsonify({"error": "request must be json"}), 415

        # Get the request body
        body = await request.get_json()

        if not body:
            return jsonify({"error": "request body is empty"}), 400

        # Get the request message
        messages: list = body.get("messages", [])

        if not messages and len(messages) == 0:
            return jsonify({"error": "request must have a message"}), 400

        # Get the request session_state, context from the request body
        session_state = body.get("sessionState", None)
        context = body.get("context", {})

        # Get the overrides from the context
        override = context.get("overrides", {})
        retrieval_mode: str = override.get("retrieval_mode", "vector")
        temperature: float = override.get("temperature", 0.3)
        top: int = override.get("top", 3)
        score_threshold: float = override.get("score_threshold", 0.5)

        if approach := available_approaches.get(retrieval_mode):
            response: RetrievalResponse = await approach(
                session_state=session_state,
                messages=messages,
                temperature=temperature,
                limit=top,
                score_threshold=score_threshold,
            )
            return jsonify(response)
        return jsonify({"error": "Not Implemented!"}), 501

    @app.route("/chat/stream", methods=["POST"])
    async def stream_chat() -> Any:
        if not request.is_json:
            return jsonify({"error": "request must be json"}), 415

        # Get the request body
        body = await request.get_json()

        if not body:
            return jsonify({"error": "request body is empty"}), 400

        # Get the request message
        messages: list = body.get("messages", [])

        if not messages and len(messages) == 0:
            return jsonify({"error": "request must have a message"}), 400

        # Get the request session_state, context from the request body
        session_state = body.get("session_state", None)
        context = body.get("context", {})

        # Get the overrides from the context
        override = context.get("overrides", {})
        retrieval_mode: str = override.get("retrieval_mode", "vector")
        temperature: float = override.get("temperature", 0.3)
        top: int = override.get("top", 3)
        score_threshold: float = override.get("score_threshold", 0.5)

        if retrieval_mode == "rag":
            result: AsyncGenerator[RetrievalResponseDelta, None] = app_config.run_rag_stream(
                session_state=session_state,
                messages=messages,
                temperature=temperature,
                limit=top,
                score_threshold=score_threshold,
            )
            response = await make_response(format_as_ndjson(result))
            response.mimetype = "application/x-ndjson"
            return response
        return jsonify({"error": "Not Implemented!"}), 501

    return app


# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 50505))
    app.run(host='0.0.0.0', port=port)
"""
