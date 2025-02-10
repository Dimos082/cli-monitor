import unittest
import subprocess

class TestCliMonitorBasic(unittest.TestCase):
    """Tests the most basic functionality of cli_monitor.py."""

    def test_echo_command(self):
        """Verify 'echo Hello' runs without errors and prints 'Hello'."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo Hello",
            "--timer", "2"  # short run
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Hello", result.stdout)

    def test_invalid_frequency(self):
        """Frequency outside allowed range should cause an error exit."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo Hello",
            "--frequency", "999999999"  # way too large
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Expecting a non-zero exit code due to frequency validation
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Frequency must be between", result.stderr)

if __name__ == "__main__":
    unittest.main()
