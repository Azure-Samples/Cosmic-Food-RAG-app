# Playwright Tests

This directory contains end-to-end tests for the Cosmic Food RAG App using Playwright.

## Test Files

- `test_playwright.py` - Main Playwright test file containing UI tests

## Test Coverage

The tests cover the following functionality:

1. **Home Page Test** (`test_home`)
   - Verifies the application loads correctly
   - Checks the page title

2. **Basic Chat Test** (`test_chat`)
   - Tests basic chat functionality with streaming responses
   - Mocks the chat/stream endpoint
   - Verifies chat input, submission, and response display
   - Tests clear chat functionality

3. **Chat Customization Test** (`test_chat_customization`)
   - Tests opening developer settings
   - Verifies chat works with non-streaming responses

4. **Non-streaming Chat Test** (`test_chat_nonstreaming`)
   - Tests chat with mocked non-streaming responses
   - Uses the /chat endpoint instead of /chat/stream

## Mock Data

Mock response data is stored in `tests/snapshots/test_playwright/`:

- `test_chat_flow/chat_flow_response.json` - Non-streaming chat response
- `test_chat_streaming_flow/chat_streaming_flow_response.jsonlines` - Streaming chat response
- `test_simple_chat_flow/simple_chat_flow_response.json` - Simple chat response

## Running Tests

### Prerequisites

- Python dependencies: `pytest`, `playwright`, `pytest-playwright`
- Chromium browser installed via Playwright

### Running All Playwright Tests

```bash
python -m pytest tests/test_playwright.py -v --browser chromium
```

### Running Individual Tests

```bash
# Home page test
python -m pytest tests/test_playwright.py::test_home -v --browser chromium

# Chat tests
python -m pytest tests/test_playwright.py::test_chat -v --browser chromium
```

### Test Server

The tests use a test server that:
- Runs the Quart application in test mode
- Bypasses OpenAI and Cosmos DB connections
- Uses mock responses for chat functionality
- Automatically starts and stops for each test

## Implementation Notes

- Tests run in headless mode by default
- The server runs on a random available port for each test session
- Mock responses are intercepted at the network level using Playwright's route mocking
- Tests are designed to be independent and can run in any order