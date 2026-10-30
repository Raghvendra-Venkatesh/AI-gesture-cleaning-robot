import unittest

from src.motion_controller import MotionController


class FakeWifi:
    last_error = None

    def __init__(self):
        self.commands = []

    def send_command(self, command):
        self.commands.append(command)
        return True


class MotionControllerTests(unittest.TestCase):
    def test_dry_run_accepts_stop(self):
        controller = MotionController(None, dry_run=True)
        self.assertTrue(controller.stop())
        self.assertEqual(controller.current_command, "STOP")

    def test_sends_changed_command_once(self):
        wifi = FakeWifi()
        controller = MotionController(wifi, dry_run=False, heartbeat_seconds=100)
        self.assertTrue(controller.send("FORWARD"))
        self.assertTrue(controller.send("FORWARD"))
        self.assertEqual(wifi.commands, ["FORWARD"])

    def test_force_stop_is_sent(self):
        wifi = FakeWifi()
        controller = MotionController(wifi, dry_run=False, heartbeat_seconds=100)
        controller.stop(force=True)
        self.assertEqual(wifi.commands, ["STOP"])

    def test_non_forced_stop_sends_transition_only_once(self):
        wifi = FakeWifi()
        controller = MotionController(wifi, dry_run=False, heartbeat_seconds=100)
        controller.send("FORWARD")
        controller.stop(force=False)
        controller.stop(force=False)
        self.assertEqual(wifi.commands, ["FORWARD", "STOP"])


if __name__ == "__main__":
    unittest.main()
