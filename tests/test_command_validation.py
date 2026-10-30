import unittest

from src.commands import is_valid_command, normalize_command


class CommandValidationTests(unittest.TestCase):
    def test_valid_commands_are_normalized(self):
        self.assertEqual(normalize_command(" forward "), "FORWARD")
        self.assertEqual(normalize_command("STOP"), "STOP")

    def test_invalid_command_rejected(self):
        self.assertFalse(is_valid_command("SPIN"))
        with self.assertRaises(ValueError):
            normalize_command("SPIN")


if __name__ == "__main__":
    unittest.main()
