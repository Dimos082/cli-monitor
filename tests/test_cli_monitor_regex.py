import unittest
import subprocess

class TestCliMonitorRegex(unittest.TestCase):
    """Tests regex matching and triggered command execution."""

    def test_regex_trigger(self):
        """Should detect 'ERROR' and run the triggered command."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo ERROR OCCURRED",
            "--regex", "ERROR",
            "--regex-execute", "echo 'Trigger ran!'",
            "--timer", "2"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("ERROR OCCURRED", result.stdout)      # Main command output
        self.assertIn("Trigger ran!", result.stdout)        # Triggered command output

    def test_no_regex_no_trigger(self):
        """No triggered command should run if no regex is provided."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo Hello Again",
            "--timer", "2"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Hello Again", result.stdout)
        # Ensure we DON'T see "Trigger ran!"
        self.assertNotIn("Trigger ran!", result.stdout)

if __name__ == "__main__":
    unittest.main()
