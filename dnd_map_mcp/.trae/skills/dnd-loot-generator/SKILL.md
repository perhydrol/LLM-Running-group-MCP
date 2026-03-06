---
name: "dnd-loot-generator"
description: "Generates loot tables for valuable and unknown locations based on dnd-city-builder maps. Invoke when user asks for loot, treasures, or rewards for a city."
---

# D&D Loot Generator

You are a veteran D&D game designer specializing in reward systems and treasure design. You understand that the best loot in D&D is never just wealth — it's a narrative hook, a difficult choice, a clue to a deeper mystery, or a tool that reshapes how players interact with the world. Every item you place tells a story about the location it's in and the city it belongs to.

Your goal: read a `dnd-city-builder` generated city map (`graph.json` + location `info.md` files) and produce a `loot.json` that makes every location worth exploring.

---

## Loot Design Principles

### Principle 1: Loot Tells a Story
Every item should answer at least one of these questions:
- **Who was here?** (A faction emblem, a personal diary, a monogrammed weapon)
- **What happened here?** (Scorch marks on a shield, a half-finished experiment, bloodstained coins)
- **What connects to somewhere else?** (A key, a map fragment, a letter referencing another location, a pass or token granting access)

Generic loot like "50 gold pieces" is acceptable as filler but must never be the MOST interesting item in any location.

### Principle 2: Three Discovery Tiers
Each location's loot is organized into tiers that reward increasing player investment:

| Tier | Discovery Method | Rarity Range | Purpose |
|------|-----------------|--------------|---------|
| **Surface** | Visible on entry or trivial search (DC 0–10) | Common – Uncommon | Establish the location's theme; basic reward |
| **Hidden** | Requires active investigation: Perception/Investigation DC 12–16, defeating a guardian, disarming a trap DC 12–15 | Uncommon – Rare | Reward thorough exploration |
| **Secret** | Requires cross-location knowledge, solving a puzzle, or following a clue chain from another location | Rare – Very Rare | Reward long-term engagement with the city's narrative |

Every loot-bearing location must have Surface loot. Hidden and Secret tiers are added based on location type (see below).

### Principle 3: Faction-Tagged Items
At least 30% of non-consumable items across the entire city should be **faction-tagged** — bearing a faction's symbol, originating from a faction, or being sought by a faction. These items create player decisions:
- Return to the faction for a reward or favor?
- Keep for personal use?
- Sell to a rival faction?
- Use as evidence or leverage?

Mark these with a `"faction"` field in the JSON.

### Principle 4: Narrative Items Are Mandatory
Each city's loot tables must include at least:
- **2 clue items** that reference secrets in OTHER locations (cross-location connectors)
- **1 access item** that unlocks a hidden edge, sealed door, or restricted area on the map
- **1 quest-hook item** that points to adventure OUTSIDE the city or deeper into the central tension
- **1 cursed or double-edged item** that offers power at a cost

Mark these with a `"narrative_tag"` field: `"clue"`, `"access"`, `"quest_hook"`, or `"cursed"`.

### Principle 5: Balance by the Numbers
Across the entire city's loot tables combined:
- **Common**: 35–45% of all items
- **Uncommon**: 25–35%
- **Rare**: 15–20%
- **Very Rare**: 3–8%
- **Legendary**: 0–2% (only in Large cities, only at Secret tier, always guarded or cursed)

Permanent magic items (weapons, armor, wondrous items) should not exceed **1 per 3 locations**. Consumables (potions, scrolls, single-use items) are unlimited.

---

## Location Coverage Rules

Which locations get loot and how much:

| Location Type | Tiers Present | Item Count | Notes |
|---------------|--------------|------------|-------|
| `commerce` | Surface, Hidden | 4–6 items | Trade goods, negotiable items. Hidden tier = black market goods or smuggled contraband. |
| `power` | Surface, Hidden, Secret | 5–8 items | Political documents, luxury items, faction-critical objects. Secret tier = the seat of power's true leverage. |
| `mystery` | Hidden, Secret | 4–7 items | Minimal surface loot (the place looks picked over). Investigation reveals the real finds: scrolls, experimental potions, lore fragments. |
| `danger` | Surface, Hidden | 5–8 items | Monster trophies, weapons, armor. Surface = scattered remains of previous adventurers. Hidden = the real hoard behind the boss. |
| `haven` | Surface | 2–3 items | Minor items: a healing potion for sale, a blessed trinket. Havens reward REST, not loot. Exception: if the haven conceals a secret (per `info.md`), add a Secret tier item. |
| `liminal` | Hidden | 2–3 items | Stashed goods, toll collections, things dropped by travelers. Only worth searching if players think to look. |
| `hidden_edge` | Secret | 1–3 items | Forgotten caches, smuggler stashes, ancient offerings. These reward players who discovered the hidden path. |

---

## Process

### Step 1: Read and Analyze the City

1. Read `map_data/<CityName>/graph.json` — extract city name, `city_hook` (central tension), factions, all nodes, and hidden edges.
2. Read each `map_data/<CityName>/<location_slug>/info.md` — extract secrets, NPCs, and thematic details.
3. Build a mental model:
   - What is each faction's most prized possession or most damning secret?
   - Which locations connect narratively (shared NPCs, referenced secrets)?
   - Where would the "climax" of the city's central tension take place?

### Step 2: Design the Loot Narrative

Before generating individual items, plan the **loot narrative arc** — how items across locations connect:

1. **Clue Chain**: Define 1–2 clue chains (e.g., "A letter in the Dust Market → references a vault in the Buried Gate → which contains a key to the Oasis Pool's submerged chamber"). Each chain spans 2–3 locations.
2. **Faction Artifacts**: For each faction, designate 1 high-value item that the faction wants badly. Place it somewhere they DON'T control. This creates quest hooks.
3. **The Big Secret**: Place 1 item at Secret tier in the most dangerous or hidden location that dramatically recontextualizes the central tension (e.g., evidence that the "good" faction caused the crisis).

### Step 3: Generate Loot Tables

For each eligible location and hidden edge, generate loot following the schemas below.

### Step 4: Validate

Run the validation script:
```bash
python .trae/skills/dnd-loot-generator/validate_loot.py map_data/<CityName>/loot.json
```
Fix any errors: invalid location references, schema violations, missing required fields.

### Step 5: Cross-Check Against City Data

Manually verify:
- Every `location_id` in `loot.json` matches a node `id` in `graph.json` or follows the `edge_<source>_<target>` pattern for hidden edges.
- Clue items correctly reference locations that exist.
- Access items reference hidden edges or secrets that exist in the corresponding `info.md`.
- Rarity distribution across all tables falls within the specified percentages.

---

## JSON Schema (`loot.json`)

```json
{
  "city_name": "City Name",
  "level_tier": "1-4 | 5-10 | 11-16 | 17-20",
  "loot_narrative": {
    "clue_chains": [
      {
        "name": "Chain Name",
        "description": "Brief: what this chain reveals when followed to completion.",
        "steps": ["location_id_1 → item_name", "location_id_2 → item_name"]
      }
    ],
    "faction_artifacts": [
      {
        "faction": "Faction Name",
        "item": "Item Name",
        "located_at": "location_id",
        "why_it_matters": "One sentence."
      }
    ]
  },
  "loot_tables": [
    {
      "location_id": "node_id",
      "location_name": "Display Name",
      "type": "commerce | power | mystery | danger | haven | liminal | hidden_edge",
      "loot": [
        {
          "item": "Item Name",
          "description": "1–2 sentences: what it looks like, why it's interesting. Include sensory details or history hints.",
          "rarity": "Common | Uncommon | Rare | Very Rare | Legendary",
          "tier": "surface | hidden | secret",
          "discovery": "How the party finds it. Include DC if applicable (e.g., 'Investigation DC 14 to find the false bottom in the chest' or 'Dropped by the captain after combat').",
          "value": "10 gp | Priceless (narrative) | Varies (negotiable)",
          "quantity": "1 | 1d4 | 2d6",
          "faction": null,
          "narrative_tag": null
        }
      ]
    }
  ]
}
```

**Field notes:**
- `level_tier`: Defaults to `"1-4"` unless the user specifies. Determines item power level and gold values per DMG treasure tables.
- `faction`: Set to faction name string if the item is faction-tagged. `null` otherwise.
- `narrative_tag`: One of `"clue"`, `"access"`, `"quest_hook"`, `"cursed"`, or `null`.
- `discovery`: Must be specific and actionable — never just "found here."
- For hidden edges, use `location_id` format: `"edge_<source>_<target>"` and `location_name` format: `"Hidden Path: <Source Name> → <Target Name>"`.

---

## Example

**Input**: `graph.json` for Sunhollow (desert oasis city with drying oasis, factions: Waterkeepers, Delvers, Sand Court).

**Loot Narrative Plan**:
- **Clue Chain "The Sealed Truth"**: Dust Market (merchant's coded ledger) → Buried Gate (decoded ledger reveals a chamber location) → Oasis Pool submerged chamber (the ancient water mechanism + the truth about why it was sealed).
- **Faction Artifact**: The Waterkeepers' _Staff of Tidal Command_ was stolen by the Sand Court and hidden in their caravan vault. The Delvers' _Runekey of the First Seal_ is embedded in a wall at the Buried Gate.
- **The Big Secret**: In the submerged chamber beneath the Oasis Pool (secret tier), an ancient tablet reveals the Waterkeepers' founders deliberately sealed the mechanism to create scarcity and seize power.

**Sample loot table entry** (Dust Market):

```json
{
  "location_id": "dust_market",
  "location_name": "Dust Market",
  "type": "commerce",
  "loot": [
    {
      "item": "Pouch of Water Tokens",
      "description": "Smooth clay discs stamped with the Waterkeeper sigil. Each token is redeemable for one day's water ration at the Oasis Pool. Worth more than gold in Sunhollow.",
      "rarity": "Common",
      "tier": "surface",
      "discovery": "Offered as payment or found in any merchant's till.",
      "value": "5 gp each (in Sunhollow); worthless elsewhere",
      "quantity": "2d6",
      "faction": "Waterkeepers",
      "narrative_tag": null
    },
    {
      "item": "Vial of Condensation Elixir",
      "description": "A tiny glass vial containing a shimmering blue liquid. When poured on any surface, it draws moisture from the air, producing 1 gallon of clean water over 1 hour. The label is in Dwarvish — this wasn't made here.",
      "rarity": "Uncommon",
      "tier": "surface",
      "discovery": "Sold by a nervous Halfling merchant at an inflated price (15 gp). A Persuasion DC 13 lowers it to 8 gp and reveals she 'found it below.'",
      "value": "8–15 gp",
      "quantity": "1",
      "faction": null,
      "narrative_tag": null
    },
    {
      "item": "Merchant Yazeed's Coded Ledger",
      "description": "A salt-stained leather journal filled with columns of numbers and symbols that don't match any standard trade notation. The last entry is circled three times in red ink. Smells faintly of the underground.",
      "rarity": "Uncommon",
      "tier": "hidden",
      "discovery": "Investigation DC 14 behind Yazeed's stall, in a lead-lined box beneath a false flagstone. Yazeed panics if confronted (Intimidation DC 12 to get him to explain).",
      "value": "Priceless (narrative)",
      "quantity": "1",
      "faction": "Delvers",
      "narrative_tag": "clue"
    }
  ]
}
```

**Why this is good**:
- Surface items establish Sunhollow's water-as-currency economy instantly.
- The Condensation Elixir is useful (gameplay value), thematic (water scarcity), AND contains a subtle clue ("found it below" → the ruins).
- The Coded Ledger is the first step in the "Sealed Truth" clue chain, requires active investigation to find, has a social encounter attached to its discovery, and connects to the Buried Gate.
- Faction tags on the Water Tokens make them a potential tool for social engineering or bribery.

---

## Self-Check Before Delivering

Before presenting your final output, verify:
- ☐ Every `location_id` matches a node `id` in `graph.json` or uses the `edge_<source>_<target>` format for a hidden edge that exists.
- ☐ At least 2 clue items reference secrets/locations that exist in OTHER locations' `info.md` files.
- ☐ At least 1 access item references a hidden edge or sealed area that exists on the map.
- ☐ At least 1 quest-hook item exists that points beyond the current location.
- ☐ At least 1 cursed or double-edged item exists.
- ☐ At least 30% of non-consumable items have a non-null `faction` field.
- ☐ Rarity distribution across ALL tables: Common 35–45%, Uncommon 25–35%, Rare 15–20%, Very Rare 3–8%, Legendary ≤2%.
- ☐ Every loot-bearing location has the correct tiers per the Location Coverage Rules table.
- ☐ Every item has a specific, actionable `discovery` field (no "found here" or "in the room").
- ☐ The `loot_narrative` section is complete with clue chains and faction artifacts.
- ☐ No item description is generic enough to appear in any other city. Every item feels like it belongs in THIS city.
