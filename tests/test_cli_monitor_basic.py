import subprocess
import pytest

@pytest.fixture
def base_command():
    return ["python", "cli_monitor.py"]

@pytest.mark.parametrize("extra_args, expected_output, should_fail", [
    (["--command", "echo Hello", "--timer", "2"], "Hello", False),
    (["--command", "echo Timer Test", "--timer", "1"], "Timer Test", False),
    (["--command", "invalid_command_that_does_not_exist", "--timer", "2"], "ERROR", True),
])
def test_varied_command_runs(base_command, extra_args, expected_output, should_fail):
    """Verify that the command runs correctly with various arguments."""
    cmd = base_command + extra_args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if should_fail:
        assert (
            "ERROR running" in result.stdout or
            "CRITICAL ERROR" in result.stdout or
            "not recognized" in result.stdout or
            "not found" in result.stdout
        )
    else:
        assert result.returncode == 0
        assert expected_output in result.stdout

def test_invalid_frequency(base_command):
    """Test invalid frequency values."""
    cmd = base_command + [
        "--command", "echo Hello",
        "--frequency", "999999999"  # too large
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Frequency must be between" in result.stderr