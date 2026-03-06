import json
import networkx as nx
from pathlib import Path
from typing import Dict, Union, Any


class GraphManager:
    def __init__(self, base_path: Union[str, Path]):
        self.base_path = Path(base_path)
        self.graphs: Dict[str, nx.Graph] = {}  # Cache graphs: city_name -> nx.Graph
        self.city_data: Dict[str, Dict] = {}  # Cache raw data: city_name -> dict

    def _load_graph(self, city_name: str) -> nx.Graph:
        if city_name in self.graphs:
            return self.graphs[city_name]

        graph_path = self.base_path / city_name / "graph.json"
        if not graph_path.exists():
            raise FileNotFoundError(
                f"City '{city_name}' not found or has no graph data at {graph_path}."
            )

        with open(graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.city_data[city_name] = data

        G = nx.Graph()
        for node in data.get("nodes", []):
            G.add_node(node["id"], **node)

        for edge in data.get("edges", []):
            G.add_edge(
                edge["source"],
                edge["target"],
                weight=edge["weight"],
                hidden=edge.get("hidden", False),
                description=edge.get("description", ""),
            )

        self.graphs[city_name] = G
        return G

    def list_locations(self, city_name: str) -> Dict[str, Any]:
        """
        Returns structure with city metadata and locations list.
        """
        try:
            G = self._load_graph(city_name)
            data = self.city_data.get(city_name, {})

            locations = []
            for node_id, node_data in G.nodes(data=True):
                locations.append(
                    {
                        "id": node_id,
                        "name": node_data.get("name", node_id),
                        "summary": node_data.get("summary", ""),
                        "type": node_data.get("type", "Unknown"),
                    }
                )

            return {
                "city_name": data.get("city_name", city_name),
                "city_hook": data.get("city_hook", ""),
                "factions": data.get("factions", []),
                "locations": locations,
            }
        except FileNotFoundError:
            return {"error": f"City '{city_name}' not found."}

    def get_location_info(self, city_name: str, location_name: str) -> str:
        # First try to find the location ID from the name in the graph
        try:
            G = self._load_graph(city_name)
            target_node_name = None

            # Simple name matching
            for node_id, data in G.nodes(data=True):
                if data.get("name") == location_name or node_id == location_name:
                    target_node_name = data.get("name")
                    break

            if not target_node_name:
                return f"Location '{location_name}' not found in city '{city_name}'."

            # Construct path to info.md
            # Structure: map_data/city/location_name/info.md
            info_path = self.base_path / city_name / target_node_name / "info.md"

            if not info_path.exists():
                return f"No detailed information available for '{location_name}'."

            with open(info_path, "r", encoding="utf-8") as f:
                return f.read()

        except FileNotFoundError:
            return f"City '{city_name}' not found."

    def get_shortest_path(
        self, city_name: str, start_location: str, target_location: str
    ) -> Union[Dict[str, Any], str]:
        try:
            G = self._load_graph(city_name)

            start_node = None
            target_node = None

            # Resolve names to IDs
            for node_id, data in G.nodes(data=True):
                if data.get("name") == start_location or node_id == start_location:
                    start_node = node_id
                if data.get("name") == target_location or node_id == target_location:
                    target_node = node_id

            if not start_node:
                return f"Start location '{start_location}' not found."
            if not target_node:
                return f"Target location '{target_location}' not found."

            try:
                # Use standard weight for calculation
                path = nx.shortest_path(
                    G, source=start_node, target=target_node, weight="weight"
                )
                length = nx.shortest_path_length(
                    G, source=start_node, target=target_node, weight="weight"
                )

                # Format output with edge descriptions
                steps_info = []
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    edge_data = G.get_edge_data(u, v)
                    steps_info.append(
                        {
                            "from": G.nodes[u]["name"],
                            "to": G.nodes[v]["name"],
                            "description": edge_data.get("description", "A path."),
                            "hidden": edge_data.get("hidden", False),
                        }
                    )

                path_names = [G.nodes[node]["name"] for node in path]

                return {
                    "path": path_names,
                    "total_distance": length,
                    "steps_count": len(path) - 1,
                    "journey_details": steps_info,
                }
            except nx.NetworkXNoPath:
                return (
                    f"No path found between '{start_location}' and '{target_location}'."
                )

        except FileNotFoundError:
            return f"City '{city_name}' not found."
