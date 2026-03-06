import json
import sys
import networkx as nx
from pathlib import Path


def validate_city(city_path_str: str):
    city_path = Path(city_path_str)

    # 1. Check if city directory exists
    if not city_path.exists():
        print(f"Error: City directory '{city_path}' does not exist.")
        sys.exit(1)

    # 2. Check graph.json
    graph_path = city_path / "graph.json"
    if not graph_path.exists():
        print(f"Error: 'graph.json' missing in '{city_path}'.")
        sys.exit(1)

    try:
        with open(graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in 'graph.json': {e}")
        sys.exit(1)

    # Validate new top-level fields
    if "city_name" not in data:
        print("Warning: Missing top-level 'city_name' field.")
    if "city_hook" not in data:
        print("Warning: Missing top-level 'city_hook' field.")
    if "factions" not in data:
        print("Warning: Missing top-level 'factions' field.")

    # Build Graph
    G = nx.Graph()
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    node_ids = set()
    for node in nodes:
        node_id = node.get("id")
        node_name = node.get("name")
        if not node_id:
            print("Error: Node found without 'id'.")
            continue
        if not node_name:
            print(f"Error: Node '{node_id}' missing 'name'.")

        G.add_node(node_id, **node)
        node_ids.add(node_id)

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_ids:
            print(f"Error: Edge references unknown source node '{source}'.")
        if target not in node_ids:
            print(f"Error: Edge references unknown target node '{target}'.")

        # Check new edge fields
        if "description" not in edge:
            print(f"Warning: Edge from {source} to {target} missing 'description'.")

        G.add_edge(source, target)

    # 3. Check for isolated nodes
    isolated_nodes = list(nx.isolates(G))
    if isolated_nodes:
        print(
            f"Warning: Found {len(isolated_nodes)} isolated nodes (not connected to any other location):"
        )
        for node in isolated_nodes:
            print(f"  - {node} ({G.nodes[node].get('name', 'Unknown')})")
    else:
        print("Graph Check: All nodes are connected.")

    # Check faction locations validity
    factions = data.get("factions", [])
    for faction in factions:
        for loc in faction.get("locations", []):
            if loc not in node_ids:
                print(
                    f"Error: Faction '{faction.get('name')}' references unknown location '{loc}'."
                )

    # 4. Check for missing markdown files
    missing_files = []
    for node in nodes:
        node_name = node.get("name")
        if not node_name:
            continue

        # Structure: city_path / node_name / info.md
        info_path = city_path / node_name / "info.md"
        if not info_path.exists():
            missing_files.append(f"{node_name} (Expected at: {info_path})")

    if missing_files:
        print(
            f"Error: Found {len(missing_files)} locations with missing 'info.md' files:"
        )
        for missing in missing_files:
            print(f"  - {missing}")
    else:
        print("File Check: All locations have corresponding markdown files.")

    if isolated_nodes or missing_files:
        sys.exit(1)

    print("Validation Successful!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_city.py <path_to_city_directory>")
        sys.exit(1)

    validate_city(sys.argv[1])
