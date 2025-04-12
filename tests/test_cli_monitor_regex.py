import subprocess
import pytest

@pytest.fixture
def base_regex_cmd():
    return [
        "python", "cli_monitor.py",
        "--timer", "2"
    ]

@pytest.mark.parametrize("command, regex, regex_exec, expected_trigger", [
    ("echo ERROR OCCURRED", "ERROR", "echo 'Trigger ran!'", True),
    ("echo Hello Again", "", "", False),
    ("echo No Match Here", "NonMatchingPattern", "echo 'Should Not Trigger'", False),
])
def test_regex_triggering(base_regex_cmd, command, regex, regex_exec, expected_trigger):
    """Test various regex triggering scenarios."""
    cmd = base_regex_cmd + ["--command", command]
    if regex:
        cmd += ["--regex", regex]
    if regex_exec:
        cmd += ["--regex-execute", regex_exec]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert command.split()[1] in result.stdout  # Basic command output check
    if expected_trigger:
        assert "Trigger ran!" in result.stdout
    else:
        assert "Trigger ran!" not in result.stdout

def test_invalid_regex():
    """Expect failure from invalid regex pattern."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo Regex Test",
        "--regex", "[InvalidRegex",  # bad pattern
        "--regex-execute", "echo 'Regex Triggered!'",
        "--timer", "2"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0
    assert "CRITICAL ERROR" in result.stderr or "CRITICAL ERROR" in result.stdout
    assert "unterminated character set" in result.stderr or "unterminated character set" in result.stdout