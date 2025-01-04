import unittest
import subprocess
import os

class TestCliMonitorLogging(unittest.TestCase):
    """Tests output-file logging and log pruning."""

    def setUp(self):
        self.log_file = "test_log_output.txt"
        # Remove log file if it exists
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def tearDown(self):
        # Clean up log file
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_log_pruning(self):
        """Check that log file pruning occurs once it exceeds max size."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo TestLogLine",
            "--output-file", self.log_file,
            "--max-log-size", "1",  # 1KB to force quick pruning
            "--timer", "3"          # run a few iterations
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        # We expect the log file to exist, but be under or ~1KB
        self.assertTrue(os.path.exists(self.log_file))
        file_size = os.path.getsize(self.log_file)
        self.assertLessEqual(file_size, 1024, "Log file should be pruned to <= 1KB")

if __name__ == "__main__":
    unittest.main()