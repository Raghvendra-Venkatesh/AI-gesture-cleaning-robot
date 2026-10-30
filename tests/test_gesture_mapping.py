import unittest

from src.gesture_mapping import GestureMapping


class GestureMappingTests(unittest.TestCase):
    def test_unmapped_gesture_stops(self):
        mapping = GestureMapping({"palm": "STOP"})
        self.assertEqual(mapping.command_for("unknown"), "STOP")
        self.assertEqual(mapping.command_for(None), "STOP")

    def test_mapped_gesture_returns_command(self):
        mapping = GestureMapping({"like": "FORWARD"})
        self.assertEqual(mapping.command_for("like"), "FORWARD")

    def test_yolo_labels_are_normalized_for_matching(self):
        mapping = GestureMapping({"Thumbs up": "FORWARD", "Stop": "STOP"})
        self.assertEqual(mapping.command_for("thumbs up"), "FORWARD")
        self.assertEqual(mapping.command_for("STOP"), "STOP")


if __name__ == "__main__":
    unittest.main()
