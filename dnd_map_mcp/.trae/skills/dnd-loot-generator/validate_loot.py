import json
import sys
import os
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

    # ---------------------------------------------------------
    # 1. Schema Validation
    # ---------------------------------------------------------
    required_keys = ["city_name", "level_tier", "loot_narrative", "loot_tables"]
    for key in required_keys:
        if key not in data:
            print(f"Error: Missing required key '{key}' in root object.")
            sys.exit(1)

    valid_tiers = ["1-4", "5-10", "11-16", "17-20"]
    if data["level_tier"] not in valid_tiers:
        print(
            f"Error: Invalid 'level_tier': {data['level_tier']}. Must be one of {valid_tiers}"
        )
        sys.exit(1)

    # Validate loot_narrative
    narrative = data["loot_narrative"]
    if not isinstance(narrative, dict):
        print("Error: 'loot_narrative' must be an object.")
        sys.exit(1)

    if "clue_chains" not in narrative or not isinstance(narrative["clue_chains"], list):
        print("Error: 'loot_narrative.clue_chains' must be a list.")
        sys.exit(1)

    for i, chain in enumerate(narrative["clue_chains"]):
        for key in ["name", "description", "steps"]:
            if key not in chain:
                print(f"Error: Missing key '{key}' in loot_narrative.clue_chains[{i}].")
                sys.exit(1)
        if not isinstance(chain["steps"], list):
            print(f"Error: 'steps' in loot_narrative.clue_chains[{i}] must be a list.")
            sys.exit(1)

    if "faction_artifacts" not in narrative or not isinstance(
        narrative["faction_artifacts"], list
    ):
        print("Error: 'loot_narrative.faction_artifacts' must be a list.")
        sys.exit(1)

    for i, artifact in enumerate(narrative["faction_artifacts"]):
        for key in ["faction", "item", "located_at", "why_it_matters"]:
            if key not in artifact:
                print(
                    f"Error: Missing key '{key}' in loot_narrative.faction_artifacts[{i}]."
                )
                sys.exit(1)

    if not isinstance(data["loot_tables"], list):
        print("Error: 'loot_tables' must be a list.")
        sys.exit(1)

    # ---------------------------------------------------------
    # 2. Logical & Statistical Validation
    # ---------------------------------------------------------

    # Load graph.json if available for ID validation
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

    # Location Coverage Rules (Based on SKILL.md table)
    # Define expected tiers for each location type
    location_tier_expectations = {
        "commerce": {"expected": ["surface"], "optional": ["hidden"]},
        "power": {"expected": ["surface"], "optional": ["hidden", "secret"]},
        "mystery": {
            "expected": ["hidden"],
            "optional": ["secret", "surface"],
        },  # Surface is 'minimal' but allowed
        "danger": {"expected": ["surface"], "optional": ["hidden", "secret"]},
        "haven": {"expected": ["surface"], "optional": ["secret"]},
        "liminal": {"expected": ["hidden"], "optional": ["secret", "surface"]},
        "hidden_edge": {"expected": ["secret"], "optional": []},
    }

    rarity_counts = Counter()
    tag_counts = Counter()
    faction_items_count = 0
    total_items = 0

    errors = []
    warnings = []

    for i, table in enumerate(data["loot_tables"]):
        # Basic field checks
        for key in ["location_id", "location_name", "type", "loot"]:
            if key not in table:
                print(f"Error: Missing required key '{key}' in loot_table[{i}].")
                sys.exit(1)

        loc_type = table["type"]
        loc_id = table["location_id"]

        if loc_type not in valid_location_types:
            errors.append(f"Loot Table [{i}]: Invalid type '{loc_type}'.")

        # ID Validation
        if graph_loaded and loc_type != "hidden_edge":
            if loc_id not in valid_node_ids:
                errors.append(
                    f"Loot Table [{i}]: Location ID '{loc_id}' not found in graph.json."
                )

        if loc_type == "hidden_edge":
            if not loc_id.startswith("edge_"):
                warnings.append(
                    f"Loot Table [{i}]: Hidden edge ID '{loc_id}' should start with 'edge_'."
                )

        # Tier Validation
        if not isinstance(table["loot"], list):
            print(f"Error: 'loot' must be a list in loot_table[{i}].")
            sys.exit(1)

        present_tiers = set()

        for j, item in enumerate(table["loot"]):
            # Item fields
            for key in [
                "item",
                "description",
                "rarity",
                "tier",
                "discovery",
                "value",
                "quantity",
                "faction",
                "narrative_tag",
            ]:
                if key not in item:
                    print(f"Error: Missing key '{key}' in loot_table[{i}].loot[{j}].")
                    sys.exit(1)

            if item["rarity"] not in valid_rarities:
                errors.append(
                    f"Item '{item['item']}': Invalid rarity '{item['rarity']}'."
                )
            if item["tier"] not in valid_item_tiers:
                errors.append(f"Item '{item['item']}': Invalid tier '{item['tier']}'.")
            if item["narrative_tag"] not in valid_narrative_tags:
                errors.append(
                    f"Item '{item['item']}': Invalid narrative_tag '{item['narrative_tag']}'."
                )

            present_tiers.add(item["tier"])

            # Stats
            total_items += 1
            rarity_counts[item["rarity"]] += 1
            if item["narrative_tag"]:
                tag_counts[item["narrative_tag"]] += 1
            if item["faction"]:
                faction_items_count += 1

        # Check expected tiers
        if loc_type in location_tier_expectations:
            expectations = location_tier_expectations[loc_type]
            for exp in expectations["expected"]:
                if exp not in present_tiers:
                    warnings.append(
                        f"Location '{loc_id}' ({loc_type}) is missing expected tier '{exp}'."
                    )

    # ---------------------------------------------------------
    # 3. Global Stats Checks
    # ---------------------------------------------------------

    # Narrative Tags
    if tag_counts["clue"] < 2:
        errors.append(
            f"Narrative: Found {tag_counts['clue']} 'clue' items. Required: >= 2."
        )
    if tag_counts["access"] < 1:
        errors.append(
            f"Narrative: Found {tag_counts['access']} 'access' items. Required: >= 1."
        )
    if tag_counts["quest_hook"] < 1:
        errors.append(
            f"Narrative: Found {tag_counts['quest_hook']} 'quest_hook' items. Required: >= 1."
        )
    if tag_counts["cursed"] < 1:
        errors.append(
            f"Narrative: Found {tag_counts['cursed']} 'cursed' items. Required: >= 1."
        )

    # Rarity Distribution (Only check if we have enough items for stats to mean anything)
    if total_items >= 10:
        rarity_pct = {k: (v / total_items) * 100 for k, v in rarity_counts.items()}

        # Targets: Common 35-45, Uncommon 25-35, Rare 15-20, Very Rare 3-8, Legendary 0-2
        # We use wider tolerance for warnings to avoid being too annoying on small samples
        def check_pct(rarity, min_p, max_p, tolerance=10):
            pct = rarity_pct.get(rarity, 0)
            if pct < (min_p - tolerance) or pct > (max_p + tolerance):
                warnings.append(
                    f"Balance: {rarity} items are {pct:.1f}% (Target: {min_p}-{max_p}%)."
                )

        check_pct("Common", 35, 45)
        check_pct("Uncommon", 25, 35)
        # Rare/Very Rare often fluctuate more in small sets, use defaults

        # Faction Percentage
        faction_pct = (faction_items_count / total_items) * 100
        if faction_pct < 30:
            warnings.append(
                f"Faction: Only {faction_pct:.1f}% of items are faction-tagged (Target: >= 30%)."
            )

    # ---------------------------------------------------------
    # 4. Report
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
