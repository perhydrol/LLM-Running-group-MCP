# D&D Map MCP Server

An MCP (Model Context Protocol) server for managing and navigating D&D city maps. It provides graph-based pathfinding, location details, and narrative hooks for LLMs acting as Dungeon Masters or Player Aides.

## Features

- **Graph-Based Navigation**: Diverse routes between locations with varying weights (distance/danger).
- **Rich Metadata**: Cities have central tensions, factions, and hooks.
- **Hidden Paths**: Support for secret edges that can be discovered.
- **Markdown Integration**: Detailed location descriptions stored in standard Markdown files.
- **Validation**: Tools to ensure map data integrity.

## Installation

This project uses `uv` for dependency management.

```bash
# Install dependencies
uv sync
```

## City Builder Skill

This project includes a powerful **City Builder Skill** (`dnd-city-builder`) located in `.trae/skills/dnd-city-builder/SKILL.md`. 

This skill is designed to guide an LLM (like Claude or GPT) to act as an expert World Builder. It ensures that any generated city:
1.  **Follows the Strict Schema**: Generates valid `graph.json` structures with all required fields (`city_hook`, `factions`, `edges` with weights/descriptions).
2.  **Balances Gameplay**: Ensures a mix of location types (Haven, Danger, Mystery, etc.) and non-linear graph topology.
3.  **Creates Narrative Depth**: Enforces the creation of central tensions, faction conflicts, and cross-location secrets.
4.  **Auto-Validation**: Requires running the `validate_city.py` script to guarantee data integrity.

**When creating a new city, always refer to or load the context from `.trae/skills/dnd-city-builder/SKILL.md`.**

## Usage

Start the MCP server:

```bash
# Run with stdio transport (default)
uv run server.py

# Run with SSE transport
uv run server.py --transport sse
```

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

### Location Files
Each node ID must have a corresponding folder and `info.md` file:
`map_data/<CityName>/<node_id>/info.md`

## Tools Available

1. **`list_locations(city_name)`**
   - Returns city metadata (hook, factions) and a list of all locations.
   - Use this first to understand the city context.

2. **`get_location_info(city_name, location_name)`**
   - Returns detailed Markdown description of a specific location.
   - Includes NPCs, secrets, and atmosphere.

3. **`get_shortest_path(city_name, start_location, target_location)`**
   - Calculates routes between locations.
   - Returns path steps, total distance, and narrative descriptions of the journey.

## Development

A validation script is provided to check map data integrity (isolated nodes, missing files, schema validation):

```bash
python .trae/skills/dnd-city-builder/validate_city.py map_data/<CityName>
```
