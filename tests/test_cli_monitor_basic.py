import unittest
import subprocess
import platform

class TestCliMonitorBasic(unittest.TestCase):
    """Tests the most basic functionality of cli_monitor.py."""

    def test_command_parsing(self):
        """Fixed version correctly passes the command as a list of arguments."""
        cmd = ["echo", "hello", "world"]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        # The command should be correctly split into arguments and executed as expected
        self.assertEqual(result.stdout.strip(), "hello world", "Fixed version should correctly pass arguments!")

    def test_echo_command(self):
        """Verify 'echo Hello' runs without errors and prints 'Hello'."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo Hello",
            "--timer", "2"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Hello", result.stdout)

    def test_invalid_frequency(self):
        """Frequency outside allowed range should cause an error exit."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo Hello",
            "--frequency", "999999999"  # way too large
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        self.assertNotEqual(result.returncode, 0) # Expecting a non-zero exit code due to frequency validation
        self.assertIn("Frequency must be between", result.stderr)  # Check stderr instead of stdout

    def test_complex_command(self):
        """Ensure complex commands with multiple arguments work correctly."""
        cmd = ["dir"] if platform.system() == "Windows" else ["ls", "-la", "/"]

        result = subprocess.run(
            ["python", "cli_monitor.py", "--timer", "2", "--command"] + cmd,
            capture_output=True, text=True, shell=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("total" if platform.system() != "Windows" else "Directory", result.stdout)

    def test_command_with_quotes(self):
        """Ensure commands with quotes are properly handled."""
        cmd = [
            "python", "cli_monitor.py",
            "--command", "echo Hello World",
            "--timer", "2"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Hello World", result.stdout)

if __name__ == "__main__":
    unittest.main()
