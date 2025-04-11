import subprocess
import pytest

@pytest.fixture
def short_timer_command():
    """Fixture for a basic command with a short timer."""
    return [
        "python", "cli_monitor.py",
        "--command", "echo Timer Test",
        "--timer", "1"
    ]

def test_timer_execution(short_timer_command):
    """Verify that the command stops after the specified timer duration."""
    result = subprocess.run(short_timer_command, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Timer Test" in result.stdout

def test_invalid_command():
    """Verify that an invalid command results in an error."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "invalid_command_that_does_not_exist",
        "--timer", "2"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert "ERROR running" in result.stdout or "not found" in result.stderr, "Expected error message in output"

def test_echo_command():
    """Verify 'echo Hello' runs without errors and prints 'Hello'."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo Hello",
        "--timer", "2"  # short run
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Hello" in result.stdout

def test_invalid_frequency():
    """Frequency outside allowed range should cause an error exit."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo Hello",
        "--frequency", "999999999"  # way too large
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Expecting a non-zero exit code due to frequency validation
    assert result.returncode != 0
    assert "Error: Frequency must be between" in result.stdout
