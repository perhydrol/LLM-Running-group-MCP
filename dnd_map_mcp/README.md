# D&D Map MCP Server

An MCP (Model Context Protocol) server for managing and navigating D&D city maps. It provides graph-based pathfinding, location details, loot generation, and narrative hooks for LLMs acting as Dungeon Masters or Player Aides.

## Features

- **Graph-Based Navigation**: Diverse routes between locations with varying weights (distance/danger).
- **Rich Metadata**: Cities have central tensions, factions, and hooks.
- **Hidden Paths**: Support for secret edges that can be discovered.
- **Markdown Integration**: Detailed location descriptions stored in standard Markdown files.
- **Loot Tables**: JSON-based loot tables for locations.
- **Validation**: Tools to ensure map data integrity.

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

#### `list_locations`

Get a list of all major locations in a city with their summaries, plus city metadata.

- **Input**: `city_name` (string)
- **Output**: JSON object with city details (hook, factions) and a list of locations.

#### `get_location_info`

Get detailed information about a specific location.

- **Input**: `city_name` (string), `location_name` (string)
- **Output**: Markdown string with location description, NPCs, and secrets.

#### `get_location_loot`

Get loot table for a specific location.

- **Input**: `city_name` (string), `location_name` (string)
- **Output**: JSON object with loot items (name, quantity, description, rarity).

#### `get_shortest_path`

Calculate the shortest path between two locations.

- **Input**: `city_name` (string), `start_location` (string), `target_location` (string)
- **Output**: JSON object with path steps, total distance, and narrative descriptions.

## Configuration

### Claude Desktop Configuration

To use this MCP server with Claude Desktop, add the following configuration to your `claude_desktop_config.json` file (typically located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows or `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS).

Make sure to replace `ABSOLUTE_PATH_TO_PROJECT` with the actual absolute path to this project directory.

```json
{
  "mcpServers": {
    "dnd-map-server": {
      "command": "uv",
      "args": [
        "--directory",
        "ABSOLUTE_PATH_TO_PROJECT/dnd_map_mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

**Note**: Using `uv --directory ... run server.py` ensures that `uv` runs in the correct project context regardless of where Claude starts the process.

## Data Structure

Map data is stored in `map_data/<CityName>/`.

### `graph.json`
Defines the city's structure, factions, and connections.

```json
{
  "city_name": "City Name",
  "city_hook": "Central tension driving the narrative",
  "factions": [
    { "name": "Faction Name", "locations": ["loc_id_1"] }
  ],
  "nodes": [
    { 
      "id": "loc_id", 
      "name": "Display Name", 
      "type": "haven|commerce|power|danger|mystery|liminal",
      "summary": "Short description"
    }
  ],
  "edges": [
    { 
      "source": "loc_id_1", 
      "target": "loc_id_2", 
      "weight": 5, 
      "hidden": false, 
      "description": "Narrative description of the path" 
    }
  ]
}
```

### `loot.json`
Defines loot tables for locations.

```json
{
  "city_name": "City Name",
  "difficulty": "简单",
  "base_dc": 10,
  "level_tier": "1-4",
  "loot_tables": [
    {
      "location_id": "loc_id",
      "location_name": "Location Name",
      "loot": [
        {
          "item": "Item Name",
          "quantity": "1d4",
          "description": "Item description",
          "rarity": "common"
        }
      ]
    }
  ]
}
```

### Location Files
Each node ID must have a corresponding folder and `info.md` file:
`map_data/<CityName>/<node_id>/info.md`

## Skills

### City Builder Skill

This project includes a powerful **City Builder Skill** (`dnd-city-builder`) located in `.trae/skills/dnd-city-builder/SKILL.md`. 

This skill is designed to guide an LLM (like Claude or GPT) to act as an expert World Builder. It ensures that any generated city follows a strict schema and balances gameplay.

**When creating a new city, always refer to or load the context from `.trae/skills/dnd-city-builder/SKILL.md`.**

### Loot Generator Skill

This project also includes a **Loot Generator Skill** (`dnd-loot-generator`) located in `.trae/skills/dnd-loot-generator/SKILL.md`.

This skill generates loot tables for valuable (Commerce, Power) and unknown (Mystery, Danger, Hidden Edges) locations based on dnd-city-builder maps.

## Development

Run validation scripts to check data integrity:

```bash
# Validate city graph
uv run python .trae/skills/dnd-city-builder/validate_city.py map_data/<CityName>

# Validate loot tables
uv run python .trae/skills/dnd-loot-generator/validate_loot.py map_data/<CityName>/loot.json
```
