
# DND Dice MCP Service

A simple Python-based MCP server providing a DND-style dice rolling simulation.

## Features

- **Left-skewed Randomness**: Simulates a D20 roll with a left-skewed distribution (mode 18) to favor success and reduce frustration.
- **Difficulty Levels**: "轻轻松松", "简单", "中等", "困难", "几乎不可能成功".
- **Structured Output**: Returns check value, roll result, success status, and a human-readable message.

## Usage

### Prerequisites

- Python 3.10+
- `uv` package manager (recommended)

### Installation

```bash
uv sync
```

### Running the Server

#### Standard IO (Default)

This mode is used by MCP clients like Claude Desktop or Cursor.

```bash
uv run python server.py
```

#### SSE (Server-Sent Events)

To run the server in SSE mode, use the `--transport sse` flag. You can also specify host and port.

```bash
uv run python server.py --transport sse --port 8000
```

- **SSE Endpoint**: `http://localhost:8000/sse`
- **Messages Endpoint**: `http://localhost:8000/messages/`

### Tools

#### `roll_for_success`

Simulates a DND skill check.

- **Input**: `difficulty` (string) - one of:
    - "轻轻松松" (Check: 5)
    - "简单" (Check: 10)
    - "中等" (Check: 15)
    - "困难" (Check: 18)
    - "几乎不可能成功" (Check: 20)
- **Output**: JSON object with check details.

## Development

Run tests:

```bash
uv run python test_server.py
```

Check code quality:

```bash
uv run ruff check .
uv run pyright .
```
