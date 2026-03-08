import json
import sys
import os
import re
from collections import Counter


def validate_loot(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
        sys.exit(1)

    errors = []
    warnings = []

    # ---------------------------------------------------------
    # 1. Schema Validation - Root
    # ---------------------------------------------------------
    required_keys = [
        "city_name",
        "difficulty",
        "base_dc",
        "level_tier",
        "loot_narrative",
        "loot_tables",
    ]
    for key in required_keys:
        if key not in data:
            errors.append(f"Root: Missing required key '{key}'.")

    # Difficulty and Base DC check
    difficulty_map = {
        "轻轻松松": 5,
        "简单": 10,
        "中等": 15,
        "困难": 18,
        "几乎不可能成功": 20,
    }

    if "difficulty" in data and "base_dc" in data:
        diff = data["difficulty"]
        dc = data["base_dc"]
        if diff not in difficulty_map:
            errors.append(
                f"Root: Invalid difficulty '{diff}'. Must be one of {list(difficulty_map.keys())}."
            )
        elif difficulty_map[diff] != dc:
            errors.append(
                f"Root: base_dc {dc} does not match difficulty '{diff}' (expected {difficulty_map[diff]})."
            )

    valid_tiers = ["1-4", "5-10", "11-16", "17-20"]
    if "level_tier" in data and data["level_tier"] not in valid_tiers:
        errors.append(
            f"Root: Invalid 'level_tier': {data['level_tier']}. Must be one of {valid_tiers}"
        )

    # ---------------------------------------------------------
    # 2. Loot Narrative Validation
    # ---------------------------------------------------------
    if "loot_narrative" in data:
        narrative = data["loot_narrative"]
        if not isinstance(narrative, dict):
            errors.append("Root: 'loot_narrative' must be an object.")
        else:
            # Clue Chains
            if "clue_chains" not in narrative or not isinstance(
                narrative["clue_chains"], list
            ):
                errors.append("Narrative: 'clue_chains' must be a list.")
            else:
                for i, chain in enumerate(narrative["clue_chains"]):
                    for key in ["name", "description", "steps"]:
                        if key not in chain:
                            errors.append(
                                f"Narrative: clue_chains[{i}] missing '{key}'."
                            )
                    if "steps" in chain and isinstance(chain["steps"], list):
                        for j, step in enumerate(chain["steps"]):
                            for step_key in [
                                "location_id",
                                "item",
                                "prerequisite",
                                "unlocks",
                            ]:
                                if step_key not in step:
                                    errors.append(
                                        f"Narrative: clue_chains[{i}].steps[{j}] missing '{step_key}'."
                                    )

            # Faction Artifacts
            if "faction_artifacts" not in narrative or not isinstance(
                narrative["faction_artifacts"], list
            ):
                errors.append("Narrative: 'faction_artifacts' must be a list.")
            else:
                for i, artifact in enumerate(narrative["faction_artifacts"]):
                    for key in ["faction", "item", "located_at", "why_it_matters"]:
                        if key not in artifact:
                            errors.append(
                                f"Narrative: faction_artifacts[{i}] missing '{key}'."
                            )

            # Prerequisite Map
            if "prerequisite_map" in narrative:
                if not isinstance(narrative["prerequisite_map"], list):
                    errors.append("Narrative: 'prerequisite_map' must be a list.")
                else:
                    for i, p_map in enumerate(narrative["prerequisite_map"]):
                        for key in [
                            "item",
                            "location_id",
                            "requires",
                            "source_locations",
                        ]:
                            if key not in p_map:
                                errors.append(
                                    f"Narrative: prerequisite_map[{i}] missing '{key}'."
                                )
                        if "requires" in p_map and not isinstance(
                            p_map["requires"], list
                        ):
                            errors.append(
                                f"Narrative: prerequisite_map[{i}] 'requires' must be a list."
                            )
                        if "source_locations" in p_map and not isinstance(
                            p_map["source_locations"], list
                        ):
                            errors.append(
                                f"Narrative: prerequisite_map[{i}] 'source_locations' must be a list."
                            )

    # ---------------------------------------------------------
    # 3. Loot Tables Validation
    # ---------------------------------------------------------
    if "loot_tables" not in data or not isinstance(data["loot_tables"], list):
        errors.append("Root: 'loot_tables' must be a list.")
    else:
        # Load graph.json for ID validation (reusing existing logic)
        graph_path = os.path.join(os.path.dirname(file_path), "graph.json")
        valid_node_ids = set()
        graph_loaded = False
        if os.path.exists(graph_path):
            try:
                with open(graph_path, "r", encoding="utf-8") as gf:
                    graph_data = json.load(gf)
                    for node in graph_data.get("nodes", []):
                        valid_node_ids.add(node["id"])
                graph_loaded = True
            except Exception:
                print(
                    "Warning: Could not load graph.json. Skipping exact Node ID validation."
                )

        valid_location_types = [
            "commerce",
            "power",
            "mystery",
            "danger",
            "haven",
            "liminal",
            "hidden_edge",
        ]
        valid_rarities = ["Common", "Uncommon", "Rare", "Very Rare", "Legendary"]
        valid_item_tiers = ["surface", "hidden", "secret"]
        valid_narrative_tags = ["clue", "access", "quest_hook", "cursed", None]
        valid_discovery_types = ["check", "prerequisite"]
        valid_prerequisite_types = [
            "item",
            "knowledge",
            "npc_relationship",
            "event",
            "multi_location",
            "combination",
        ]

        location_tier_expectations = {
            "commerce": {"expected": ["surface"], "optional": ["hidden"]},
            "power": {"expected": ["surface"], "optional": ["hidden", "secret"]},
            "mystery": {
                "expected": ["hidden"],
                "optional": ["secret", "surface"],
            },
            "danger": {"expected": ["surface"], "optional": ["hidden", "secret"]},
            "haven": {"expected": ["surface"], "optional": ["secret"]},
            "liminal": {"expected": ["hidden"], "optional": ["secret", "surface"]},
            "hidden_edge": {"expected": ["secret"], "optional": []},
        }

        rarity_counts = Counter()
        tag_counts = Counter()
        faction_items_count = 0
        total_items = 0

        for i, table in enumerate(data["loot_tables"]):
            # Table fields
            for key in ["location_id", "location_name", "type", "loot"]:
                if key not in table:
                    errors.append(f"Table[{i}]: Missing '{key}'.")
                    continue

            if "type" in table and table["type"] not in valid_location_types:
                errors.append(f"Table[{i}]: Invalid type '{table['type']}'.")

            # ID Validation
            if graph_loaded and "location_id" in table and "type" in table:
                loc_id = table["location_id"]
                loc_type = table["type"]
                if loc_type != "hidden_edge":
                    if loc_id not in valid_node_ids:
                        errors.append(
                            f"Table[{i}]: Location ID '{loc_id}' not found in graph.json."
                        )
                elif loc_type == "hidden_edge":
                    if not loc_id.startswith("edge_"):
                        warnings.append(
                            f"Table[{i}]: Hidden edge ID '{loc_id}' should start with 'edge_'."
                        )

            # Items
            if "loot" in table and isinstance(table["loot"], list):
                present_tiers = set()
                for j, item in enumerate(table["loot"]):
                    # Item fields
                    required_item_keys = [
                        "item",
                        "description",
                        "rarity",
                        "tier",
                        "discovery",
                        "discovery_type",
                        "prerequisites",
                        "value",
                        "quantity",
                        "faction",
                        "narrative_tag",
                    ]
                    for key in required_item_keys:
                        if key not in item:
                            errors.append(f"Table[{i}].Item[{j}]: Missing '{key}'.")
                            continue

                    if "rarity" in item and item["rarity"] not in valid_rarities:
                        errors.append(
                            f"Table[{i}].Item[{j}]: Invalid rarity '{item['rarity']}'."
                        )

                    if "tier" in item:
                        if item["tier"] not in valid_item_tiers:
                            errors.append(
                                f"Table[{i}].Item[{j}]: Invalid tier '{item['tier']}'."
                            )
                        else:
                            present_tiers.add(item["tier"])

                    # Narrative Tag & Discovery Validation
                    n_tag = item.get("narrative_tag")
                    d_type = item.get("discovery_type")
                    prereqs = item.get("prerequisites")
                    discovery_text = item.get("discovery", "")

                    if n_tag not in valid_narrative_tags:
                        errors.append(
                            f"Table[{i}].Item[{j}]: Invalid narrative_tag '{n_tag}'."
                        )

                    if d_type not in valid_discovery_types:
                        errors.append(
                            f"Table[{i}].Item[{j}]: Invalid discovery_type '{d_type}'."
                        )

                    # Logic: Narrative Tag -> Prerequisite
                    if n_tag is not None:
                        if d_type != "prerequisite":
                            errors.append(
                                f"Table[{i}].Item[{j}]: Narrative item must have discovery_type 'prerequisite'."
                            )
                        if not isinstance(prereqs, dict):
                            errors.append(
                                f"Table[{i}].Item[{j}]: Narrative item must have 'prerequisites' object."
                            )
                        else:
                            # Validate prerequisites object
                            if (
                                "type" not in prereqs
                                or prereqs["type"] not in valid_prerequisite_types
                            ):
                                errors.append(
                                    f"Table[{i}].Item[{j}]: Invalid/missing prerequisite type."
                                )
                            if "details" not in prereqs:
                                errors.append(
                                    f"Table[{i}].Item[{j}]: Missing prerequisite details."
                                )
                            if "sources" not in prereqs or not isinstance(
                                prereqs["sources"], list
                            ):
                                errors.append(
                                    f"Table[{i}].Item[{j}]: Missing/invalid prerequisite sources list."
                                )

                        # Check for DC in discovery text for narrative items (Forbidden)
                        if re.search(r"DC\s*\d+", discovery_text, re.IGNORECASE):
                            errors.append(
                                f"Table[{i}].Item[{j}]: Narrative item discovery MUST NOT use DC checks."
                            )

                    else:
                        # Non-narrative
                        if d_type == "check":
                            if prereqs is not None:
                                errors.append(
                                    f"Table[{i}].Item[{j}]: Non-narrative check item must have null prerequisites."
                                )
                        elif d_type == "prerequisite":
                            errors.append(
                                f"Table[{i}].Item[{j}]: Non-narrative item cannot have discovery_type 'prerequisite' (must be 'check')."
                            )

                    # Stats
                    total_items += 1
                    rarity_counts[item.get("rarity")] += 1
                    if n_tag:
                        tag_counts[n_tag] += 1
                    if item.get("faction"):
                        faction_items_count += 1

                # Check expected tiers
                if "type" in table and table["type"] in location_tier_expectations:
                    expectations = location_tier_expectations[table["type"]]
                    for exp in expectations["expected"]:
                        if exp not in present_tiers:
                            warnings.append(
                                f"Location '{table.get('location_id')}' ({table.get('type')}) is missing expected tier '{exp}'."
                            )

    # ---------------------------------------------------------
    # 4. Global Stats Checks
    # ---------------------------------------------------------
    # Narrative Tags counts
    required_tags = {"clue": 2, "access": 1, "quest_hook": 1, "cursed": 1}
    for tag, count in required_tags.items():
        if tag_counts[tag] < count:
            errors.append(
                f"Narrative: Found {tag_counts[tag]} '{tag}' items. Required: >= {count}."
            )

    # Rarity and Faction stats (Warnings)
    if total_items >= 10:
        rarity_pct = {k: (v / total_items) * 100 for k, v in rarity_counts.items()}

        def check_pct(rarity, min_p, max_p, tolerance=10):
            pct = rarity_pct.get(rarity, 0)
            if pct < (min_p - tolerance) or pct > (max_p + tolerance):
                warnings.append(
                    f"Balance: {rarity} items are {pct:.1f}% (Target: {min_p}-{max_p}%)."
                )

        check_pct("Common", 35, 45)
        check_pct("Uncommon", 25, 35)
        check_pct("Rare", 15, 20)
        # check_pct("Very Rare", 3, 8) # Optional

        faction_pct = (faction_items_count / total_items) * 100
        if faction_pct < 30:
            warnings.append(
                f"Faction: Only {faction_pct:.1f}% of items are faction-tagged (Target: >= 30%)."
            )

    # ---------------------------------------------------------
    # 5. Report
    # ---------------------------------------------------------
    if warnings:
        print("\n=== Warnings (Best Practice Violations) ===")
        for w in warnings:
            print(f"- {w}")

    if errors:
        print("\n=== Errors (Schema/Rule Violations) ===")
        for e in errors:
            print(f"- {e}")
        print("\nValidation FAILED.")
        sys.exit(1)

    print("\nValidation PASSED. JSON is valid and follows design principles.")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_loot.py <path_to_loot.json>")
        sys.exit(1)

    validate_loot(sys.argv[1])
