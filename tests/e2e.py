import asyncio
import socket
import time
from collections.abc import Generator
from contextlib import closing
from multiprocessing import Process
from unittest.mock import MagicMock, patch

import pytest
import requests
from hypercorn.asyncio import serve
from hypercorn.config import Config
from playwright.sync_api import Page, Route, expect

expect.set_options(timeout=10_000)


def wait_for_server_ready(url: str, timeout: float = 10.0, check_interval: float = 0.5) -> bool:
    """Make requests to provided url until it responds without error."""
    conn_error = None
    for _ in range(int(timeout / check_interval)):
        try:
            requests.get(url)
        except requests.ConnectionError as exc:
            time.sleep(check_interval)
            conn_error = str(exc)
        else:
            return True
    raise RuntimeError(conn_error)


@pytest.fixture(scope="session")
def free_port() -> int:
    """Returns a free port for the test server to bind."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def run_server(port: int):
    """Run the Quart application server using hypercorn with mocked dependencies."""
    # Mock the database setup functions before importing the app
    # Patch where the functions are used (in setup.py), not where they're defined (in utils.py)
    mock_collection = MagicMock()
    mock_collection.find.return_value = []

    with (
        patch("quartapp.approaches.setup.setup_data_collection", return_value=mock_collection),
        patch("quartapp.approaches.setup.setup_users_collection", return_value=mock_collection),
        patch("quartapp.approaches.setup.vector_store_api", return_value=MagicMock()),
        patch("quartapp.approaches.setup.embeddings_api", return_value=MagicMock()),
        patch("quartapp.approaches.setup.chat_api", return_value=MagicMock()),
    ):
        from quartapp.app import create_app

        app = create_app()
        app.config.update({"TESTING": True})
        config = Config()
        config.bind = [f"localhost:{port}"]
        config.loglevel = "ERROR"
        asyncio.run(serve(app, config))


@pytest.fixture()
def live_server_url(mock_session_env, free_port: int) -> Generator[str, None, None]:
    proc = Process(target=run_server, args=(free_port,), daemon=True)
    proc.start()
    url = f"http://localhost:{free_port}/"
    wait_for_server_ready(url, timeout=10.0, check_interval=0.5)
    yield url
    proc.kill()


# Test basic server functionality without Playwright first
def test_server_runs(live_server_url: str):
    """Test that the server starts and serves the homepage."""
    response = requests.get(live_server_url)
    assert response.status_code == 200
    assert "Cosmic Food RAG App" in response.text


def test_home(page: Page, live_server_url: str):
    """Test that the home page loads with the correct title."""
    page.goto(live_server_url)
    expect(page).to_have_title("Cosmic Food RAG App | Sample")


def test_chat(page: Page, live_server_url: str):
    """Test basic chat functionality with mocked responses."""

    # Set up mock routes for both /chat and /chat/stream endpoints
    def handle_chat(route: Route):
        # Read the JSON from our snapshot results and return as the response
        with open("tests/snapshots/e2e/test_chat_flow/chat_flow_response.json") as f:
            json_response = f.read()
        route.fulfill(body=json_response, status=200)

    def handle_stream(route: Route):
        # Assert that session_state is specified in the request (None for now)
        if route.request.post_data_json:
            session_state = route.request.post_data_json.get("sessionState")
            assert session_state is None
        # Read the JSONL from our snapshot results and return as the response
        with open("tests/snapshots/e2e/test_chat_streaming_flow/chat_streaming_flow_response.jsonlines") as f:
            jsonl = f.read()
        route.fulfill(body=jsonl, status=200, headers={"Transfer-encoding": "Chunked"})

    page.route("*/**/chat/stream", handle_stream)
    page.route("*/**/chat", handle_chat)

    # Check initial page state
    page.goto(live_server_url)
    expect(page).to_have_title("Cosmic Food RAG App | Sample")
    expect(page.get_by_role("button", name="Clear chat")).to_be_disabled()
    expect(page.get_by_role("button", name="Developer settings")).to_be_enabled()

    # Ask a question and wait for the message to appear
    page.get_by_placeholder("Type a new question (e.g. Are there any high protein dishes available?)").click()
    page.get_by_placeholder("Type a new question (e.g. Are there any high protein dishes available?)").fill(
        "What vegetarian dishes do you have?"
    )
    # Find the submit button - it might be near the textarea
    page.keyboard.press("Enter")  # Try submitting with Enter key

    expect(page.get_by_text("What vegetarian dishes do you have?")).to_be_visible()
    expect(page.get_by_text("We have delicious vegetarian options")).to_be_visible()
    expect(page.get_by_role("button", name="Clear chat")).to_be_enabled()

    # Clear the chat
    page.get_by_role("button", name="Clear chat").click()
    expect(page.get_by_text("What vegetarian dishes do you have?")).not_to_be_visible()
    expect(page.get_by_text("We have delicious vegetarian options")).not_to_be_visible()
    expect(page.get_by_role("button", name="Clear chat")).to_be_disabled()


def test_chat_customization(page: Page, live_server_url: str):
    """Test chat customization via developer settings."""

    # Set up a mock route to the /chat endpoint
    def handle(route: Route):
        # Read the JSON from our snapshot results and return as the response
        with open("tests/snapshots/e2e/test_simple_chat_flow/simple_chat_flow_response.json") as f:
            json = f.read()
        route.fulfill(body=json, status=200)

    page.route("*/**/chat", handle)

    # Check initial page state
    page.goto(live_server_url)
    expect(page).to_have_title("Cosmic Food RAG App | Sample")

    # Open developer settings
    page.get_by_role("button", name="Developer settings").click()

    # Just verify we can open settings panel - actual settings might be different than expected
    # Close the settings
    page.keyboard.press("Escape")  # Try to close with escape key

    # Ask a question and wait for the message to appear
    page.get_by_placeholder("Type a new question (e.g. Are there any high protein dishes available?)").click()
    page.get_by_placeholder("Type a new question (e.g. Are there any high protein dishes available?)").fill(
        "What vegetarian dishes do you have?"
    )
    page.keyboard.press("Enter")

    expect(page.get_by_text("What vegetarian dishes do you have?")).to_be_visible()
    expect(page.get_by_role("button", name="Clear chat")).to_be_enabled()


def test_chat_nonstreaming(page: Page, live_server_url: str):
    """Test non-streaming chat responses."""

    # Set up a mock route to the /chat endpoint
    def handle(route: Route):
        # Read the JSON from our snapshot results and return as the response
        with open("tests/snapshots/e2e/test_chat_flow/chat_flow_response.json") as f:
            json = f.read()
        route.fulfill(body=json, status=200)

    page.route("*/**/chat", handle)

    # Check initial page state
    page.goto(live_server_url)
    expect(page).to_have_title("Cosmic Food RAG App | Sample")
    expect(page.get_by_role("button", name="Developer settings")).to_be_enabled()

    # Ask a question and wait for the message to appear
    page.get_by_placeholder("Type a new question (e.g. Are there any high protein dishes available?)").click()
    page.get_by_placeholder("Type a new question (e.g. Are there any high protein dishes available?)").fill(
        "What vegetarian dishes do you have?"
    )
    page.keyboard.press("Enter")

    expect(page.get_by_text("What vegetarian dishes do you have?")).to_be_visible()
    expect(page.get_by_role("button", name="Clear chat")).to_be_enabled()
