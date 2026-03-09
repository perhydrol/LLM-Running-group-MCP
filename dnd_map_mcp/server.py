from mcp.server.fastmcp import FastMCP
from graph_manager import GraphManager
import os
import argparse
from typing import Dict, Any, Union

# Initialize FastMCP server
mcp = FastMCP("dnd-map-server")

# Initialize GraphManager
# Assuming map_data is relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_DATA_DIR = os.path.join(BASE_DIR, "map_data")
graph_manager = GraphManager(MAP_DATA_DIR)


@mcp.tool()
def list_locations(city_name: str) -> Dict[str, Any]:
    """
    Get a list of all major locations in a city with their summaries, plus city metadata.

    Use this tool FIRST when the user arrives in a new city or wants to explore the area.
    It provides the necessary location names for other tools.

    When to use:
    - User asks "Where am I?" or "What's in this city?"
    - User wants to know available destinations.
    - User is exploring a new map area.

    Examples:
    - "What can I see in Bree?"
    - "List all locations in Waterdeep."
    - "Where can I go from here?" (if city is known context)

    Returns:
    A dictionary containing:
    - city_name: Name of the city.
    - city_hook: The central tension or theme.
    - factions: List of factions and their goals.
    - locations: List of location objects (id, name, summary, type).

    Args:
        city_name: The name of the city (e.g., "布理").
    """
    return graph_manager.list_locations(city_name)


@mcp.tool()
def get_location_info(city_name: str, location_name: str) -> str:
    """
    Get detailed information about a specific location.

    Use this tool SECOND, after obtaining a location name from `list_locations`,
    or when the user specifically asks about a known place.

    When to use:
    - User asks for details about a specific place.
    - User wants to know about NPCs, secrets, or atmosphere of a location.
    - User enters a building or area.

    Examples:
    - "Tell me about the Prancing Pony."
    - "Who is at the Blacksmith?"
    - "What does the West Gate look like?"
    - "Look at the Town Hall."

    Returns:
    A Markdown string containing:
    - Description of the location.
    - Key NPCs.
    - Atmosphere/Vibe.
    - Secrets or hidden details (if applicable).

    Args:
        city_name: The name of the city.
        location_name: The name or ID of the location (must match a location from list_locations).
    """
    return graph_manager.get_location_info(city_name, location_name)


@mcp.tool()
def get_location_loot(city_name: str, location_name: str) -> Dict[str, Any]:
    """
    Get loot table for a specific location.

    Use this tool when the user wants to know what items can be found in a location.

    Args:
        city_name: The name of the city.
        location_name: The name of the location.

    Returns:
        A dictionary containing the location name and a list of items with their quantity, description, and rarity.
    """
    return graph_manager.get_location_loot(city_name, location_name)


@mcp.tool()
def get_shortest_path(
    city_name: str, start_location: str, target_location: str
) -> Union[Dict[str, Any], str]:
    """
    Calculate the shortest path between two locations.

    Use this tool when the user wants to travel between two specific points.
    Ensure you have valid start and target location names (preferably from `list_locations`).

    When to use:
    - User asks for directions.
    - User wants to know the distance between two places.
    - User says "I go to [Place] from [Place]".
    - User asks "How far is it to [Place]?"

    Examples:
    - "How do I get from the West Gate to the Prancing Pony?"
    - "Calculate the distance between the Town Hall and the Blacksmith."
    - "Show me the way to the Inn."

    Returns:
    A dictionary containing:
    - path: List of location names in order.
    - total_distance: Total distance/weight of the path.
    - steps_count: Number of steps/hops.
    - journey_details: List of steps with descriptions and hidden status.

    Args:
        city_name: The name of the city.
        start_location: The starting location name.
        target_location: The destination location name.
    """
    return graph_manager.get_shortest_path(city_name, start_location, target_location)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DND Map MCP Server")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse"],
        help="Transport protocol to use",
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (SSE only)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (SSE only)"
    )
    args = parser.parse_args()

    mcp.settings.host = args.host
    mcp.settings.port = args.port

    if args.transport == "sse":
        print(f"Starting SSE server at http://{args.host}:{args.port}/sse")
        print(f"Messages endpoint: http://{args.host}:{args.port}/messages/")

    mcp.run(transport=args.transport)
