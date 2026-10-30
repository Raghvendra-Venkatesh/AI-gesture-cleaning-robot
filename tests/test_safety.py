import unittest
import time

from src.safety import PredictionSmoother, SafetyState


class SafetyTests(unittest.TestCase):
    def test_prediction_smoother_requires_consecutive_labels(self):
        smoother = PredictionSmoother(3)
        self.assertIsNone(smoother.update("palm"))
        self.assertIsNone(smoother.update("palm"))
        self.assertEqual(smoother.update("palm"), "palm")

    def test_safety_stops_when_stale(self):
        safety = SafetyState(no_detection_stop_seconds=0.01)
        safety.mark_valid_prediction()
        time.sleep(0.02)
        self.assertTrue(safety.should_stop_for_stale_prediction())


if __name__ == "__main__":
    unittest.main()
