# DND Dice MCP Service

A simple Python-based MCP server providing a DND-style dice rolling simulation.

## Features

- **Left-skewed Randomness**: Simulates a D20 roll with a left-skewed distribution (mode 18) to favor success and reduce frustration.
- **Difficulty Levels**: Supports various difficulty levels with dynamic check values.
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
uv run server.py
```

#### SSE (Server-Sent Events)

To run the server in SSE mode, use the `--transport sse` flag. You can also specify host and port.

```bash
uv run server.py --transport sse --port 8000
```

- **SSE Endpoint**: `http://localhost:8000/sse`
- **Messages Endpoint**: `http://localhost:8000/messages/`

### Tools

#### `roll_for_success`

Simulates a DND skill check.

- **Input**: `difficulty` (string) - one of:
    - "轻轻松松" (Check Range: 1-5)
    - "简单" (Check Range: 6-10)
    - "中等" (Check Range: 11-13)
    - "困难" (Check Range: 14-17)
    - "几乎不可能成功" (Check Range: 18-20)
- **Output**: JSON object with check details.

## Configuration

### Claude Desktop Configuration

To use this MCP server with Claude Desktop, add the following configuration to your `claude_desktop_config.json` file (typically located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows or `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS).

Make sure to replace `ABSOLUTE_PATH_TO_PROJECT` with the actual absolute path to this project directory.

```json
{
  "mcpServers": {
    "dnd-dice-roller": {
      "command": "uv",
      "args": [
        "--directory",
        "ABSOLUTE_PATH_TO_PROJECT/dnd_dice_mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

**Note**: Using `uv --directory ... run server.py` ensures that `uv` runs in the correct project context regardless of where Claude starts the process.

## Development

Run tests:

```bash
uv run test_server.py
```

Check code quality:

```bash
uv run ruff check .
uv run pyright .
```
