from pathlib import Path
from typing import Any

from quart import Quart, Response, jsonify, request, send_file, send_from_directory

from quartapp.approaches.schemas import RetrievalResponse
from quartapp.config import AppConfig


def create_app(app_config: AppConfig, test_config: dict[str, Any] | None = None) -> Quart:
    app = Quart(__name__, static_folder="static")

    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)

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

        # Get the request message, session_state, context from the request body
        messages: list = body.get("messages", [])
        session_state = body.get("session_state", None)
        context = body.get("context", {})

        # Get the overrides from the context
        override = context.get("overrides", {})
        retrieval_mode: str = override.get("retrieval_mode", "vector")
        temperature: float = override.get("temperature", 0.3)
        top: int = override.get("top", 3)
        score_threshold: float = override.get("score_threshold", 0.5)

        if retrieval_mode == "vector":
            vector_answer: list[RetrievalResponse] = await app_config.run_vector(
                session_state=session_state,
                messages=messages,
                temperature=temperature,
                limit=top,
                score_threshold=score_threshold,
            )
            return jsonify({"choices": vector_answer})

        elif retrieval_mode == "rag":
            rag_answer: list[RetrievalResponse] = await app_config.run_rag(
                session_state=session_state,
                messages=messages,
                temperature=temperature,
                limit=top,
                score_threshold=score_threshold,
            )
            return jsonify({"choices": rag_answer})

        elif retrieval_mode == "keyword":
            keyword_answer: list[RetrievalResponse] = await app_config.run_keyword(
                session_state=session_state,
                messages=messages,
                temperature=temperature,
                limit=top,
                score_threshold=score_threshold,
            )
            return jsonify({"choices": keyword_answer})

        else:
            return jsonify({"error": "Not Implemented!"}), 501

    return app


# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 50505))
    app.run(host='0.0.0.0', port=port)
"""
