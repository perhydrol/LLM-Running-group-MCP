import unittest
import numpy as np
from server import get_check_value, roll_skewed_d20, roll_for_success


class TestDNDDiceRoller(unittest.TestCase):
    def test_difficulty_mapping(self):
        self.assertEqual(get_check_value("轻轻松松"), 5)
        self.assertEqual(get_check_value("简单"), 10)
        self.assertEqual(get_check_value("中等"), 15)
        self.assertEqual(get_check_value("困难"), 18)
        self.assertEqual(get_check_value("几乎不可能成功"), 20)
        self.assertEqual(get_check_value("Unknown"), 10)  # Default

    def test_roll_distribution(self):
        # Run many times to check range and mean
        rolls = [roll_skewed_d20() for _ in range(1000)]
        self.assertTrue(all(1 <= r <= 20 for r in rolls))
        mean_val = np.mean(rolls)
        # With mode 18, mean should be high, around 13-14 for triangular(1, 18, 21)
        # Triangular mean = (a + b + c) / 3 = (1 + 21 + 18) / 3 = 40 / 3 = 13.33
        print(f"Mean roll value: {mean_val}")
        self.assertGreater(mean_val, 12)

    def test_roll_for_success_tool(self):
        # This assumes the decorated function can be called directly
        # If FastMCP wraps it, we might need to access .fn or similar, but let's try direct call
        result = roll_for_success("简单")
        self.assertIn("check_value", result)
        self.assertIn("roll_result", result)
        self.assertIn("success", result)
        self.assertIn("message", result)
        self.assertEqual(result["check_value"], 10)
        self.assertEqual(result["success"], result["roll_result"] >= 10)


if __name__ == "__main__":
    unittest.main()
