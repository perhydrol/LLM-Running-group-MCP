from mcp.server.fastmcp import FastMCP
import numpy as np
from typing import Literal
import argparse

# Initialize FastMCP server
mcp = FastMCP("dnd-dice-roller")

# Define difficulty levels as a Literal type for clear schema
Difficulty = Literal["轻轻松松", "简单", "中等", "困难", "几乎不可能成功"]


def get_check_value(difficulty: str) -> int:
    """
    Maps difficulty level to a target check value (DC) with some randomness.
    """
    # Define ranges for each difficulty level (low inclusive, high exclusive)
    ranges = {
        "轻轻松松": (1, 8),  # 1-7
        "简单": (8, 13),  # 8-12
        "中等": (13, 17),  # 13-16
        "困难": (17, 20),  # 17-19
        "几乎不可能成功": (20, 21),  # 20
    }

    low, high = ranges.get(difficulty, (8, 13))  # Default to '简单'
    return np.random.randint(low, high)


def roll_skewed_d20() -> int:
    """
    Simulates a D20 roll with a left-skewed distribution (favoring higher numbers).
    Uses a triangular distribution with mode 18 to minimize frustration.
    Range: [1, 20]
    """
    # Triangular distribution: low=1, high=21 (exclusive), mode=18
    # We use 21 as high because we cast to int, so 20.99 becomes 20.
    # The mode is 18, meaning most rolls will be around 18.
    roll = int(np.random.triangular(1, 18, 21))
    return max(1, min(20, roll))  # Clamp between 1 and 20


@mcp.tool()
def roll_for_success(difficulty: Difficulty) -> dict:
    """
    Perform a DND-style dice roll check based on the given difficulty.

    Use this tool when the user attempts an action with a chance of failure,
    such as persuading a stranger, climbing a wall, or attacking an enemy.

    IMPORTANT: You must use this tool whenever a random outcome or check is required.

    Args:
        difficulty: The difficulty of the task. Options: "轻轻松松", "简单", "中等", "困难", "几乎不可能成功".

    Returns:
        A dictionary containing:
        - check_value: The target number to beat.
        - roll_result: The result of the dice roll (1-20).
        - success: Boolean indicating if the roll was successful (roll >= check).
        - message: A human-readable description of the result.
    """
    check_value = get_check_value(difficulty)
    roll_result = roll_skewed_d20()
    is_success = roll_result >= check_value

    result_text = "成功" if is_success else "失败"

    return {
        "check_value": check_value,
        "roll_result": roll_result,
        "success": is_success,
        "message": f"难度: {difficulty} (目标: {check_value}), 投掷: {roll_result}, 结果: {result_text}",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DND Dice MCP Server")
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
