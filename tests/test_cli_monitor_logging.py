import unittest
import os
import subprocess

class TestLogPruning(unittest.TestCase):
    """Tests log pruning logic for different max-log-size values."""

    def setUp(self):
        """Create a temporary log file for testing."""
        self.log_file = "test_log.txt"

    def tearDown(self):
        """Clean up the test log file after each test."""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_log_pruning_1KB(self):
        """Ensure pruning works correctly when max-log-size is 1KB."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo", "TestLogLine",
            "--output-file", self.log_file,
            "--max-log-size", "1",  # 1 KB
            "--timer", "2",
            "--frequency", "0.1"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

        # Ensure log file is pruned correctly
        self.assertTrue(os.path.exists(self.log_file))
        file_size = os.path.getsize(self.log_file)
        self.assertLessEqual(file_size, 1024, f"Log file exceeded 1KB, actual: {file_size} bytes")

    def test_log_pruning_10KB(self):
        """Ensure pruning works correctly when max-log-size is 10KB."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo", "TestLogLine",
            "--output-file", self.log_file,
            "--max-log-size", "10",  # 10 KB
            "--timer", "3",
            "--frequency", "0.1"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

        # Ensure log file is pruned correctly
        self.assertTrue(os.path.exists(self.log_file))
        file_size = os.path.getsize(self.log_file)
        self.assertLessEqual(file_size, 10 * 1024, f"Log file exceeded 10KB, actual: {file_size} bytes")

    def test_log_pruning_100KB(self):
        """Ensure pruning works correctly when max-log-size is 100KB."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo", "TestLogLine",
            "--output-file", self.log_file,
            "--max-log-size", "100",  # 100 KB
            "--timer", "5",
            "--frequency", "0.1"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)

        # Ensure log file is pruned correctly
        self.assertTrue(os.path.exists(self.log_file))
        file_size = os.path.getsize(self.log_file)
        self.assertLessEqual(file_size, 100 * 1024, f"Log file exceeded 100KB, actual: {file_size} bytes")

    def test_log_pruning_min_size(self):
        """Test with the smallest allowed log size (1KB)."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo", "TestLogLine",
            "--output-file", self.log_file,
            "--max-log-size", "1",  # 1 KB (Minimum)
            "--timer", "2"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(self.log_file))
        file_size = os.path.getsize(self.log_file)
        self.assertLessEqual(file_size, 1024, f"Log file exceeded 1KB, actual: {file_size} bytes")

    def test_log_pruning_large_size(self):
        """Test with a very large log size (10MB) to check if it still works."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo", "TestLogLine",
            "--output-file", self.log_file,
            "--max-log-size", "10240",  # 10MB
            "--timer", "2"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(self.log_file))
        file_size = os.path.getsize(self.log_file)
        self.assertLessEqual(file_size, 10 * 1024 * 1024, f"Log file exceeded 10MB, actual: {file_size} bytes")

    def test_negative_log_size(self):
        """Ensure negative log size is rejected."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo", "TestLogLine",
            "--output-file", self.log_file,
            "--max-log-size", "-5"  # Negative values should not be allowed
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)  # Should fail
        self.assertIn("error", result.stderr.lower())  # Expect an error message

    def test_zero_log_size(self):
        """Ensure zero log size is rejected."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo", "TestLogLine",
            "--output-file", self.log_file,
            "--max-log-size", "0"  # Zero is invalid
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)  # Should fail
        self.assertIn("error", result.stderr.lower())  # Expect an error message

    def test_non_integer_log_size(self):
        """Ensure non-integer values for max-log-size are rejected."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo", "TestLogLine",
            "--output-file", self.log_file,
            "--max-log-size", "ABC"  # Invalid string
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)  # Should fail
        self.assertIn("invalid", result.stderr.lower())  # Expect an error message

    def test_max_log_size_without_output_file(self):
        """Ensure using --max-log-size without --output-file prints a warning but does not fail."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo", "TestLogLine",
            "--max-log-size", "10",  # ✅ Should trigger a warning but not an error
            "--timer", "1"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        warning_message = "Warning: --max-log-size is ignored since --output-file is not set.".lower()
        self.assertTrue( # Check for the warning in both stdout and stderr
            warning_message in result.stderr.lower() or warning_message in result.stdout.lower(),
            f"Expected warning not found. Output received:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )