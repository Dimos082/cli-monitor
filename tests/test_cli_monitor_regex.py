import subprocess
import pytest

@pytest.fixture
def regex_command():
    """Fixture for a command with regex matching."""
    return [
        "python", "cli_monitor.py",
        "--command", "echo Regex Test",
        "--regex", "Regex",
        "--regex-execute", "echo 'Regex Triggered!'",
        "--timer", "2"
    ]

@pytest.fixture
def no_regex_command():
    """Fixture for a command without regex matching."""
    return [
        "python", "cli_monitor.py",
        "--command", "echo Hello Again",
        "--timer", "2"
    ]

@pytest.fixture
def invalid_regex_command():
    """Fixture for a command with an invalid regex pattern."""
    return [
        "python", "cli_monitor.py",
        "--command", "echo Regex Test",
        "--regex", "[InvalidRegex",  # Malformed regex
        "--regex-execute", "echo 'Regex Triggered!'",
        "--timer", "2"
    ]

@pytest.fixture
def no_match_regex_command():
    """Fixture for a command with a regex that does not match."""
    return [
        "python", "cli_monitor.py",
        "--command", "echo No Match Here",
        "--regex", "NonMatchingPattern",
        "--regex-execute", "echo 'Should Not Trigger'",
        "--timer", "2"
    ]

def test_regex_trigger(regex_command):
    """Should detect 'ERROR' and run the triggered command."""
    regex_command[regex_command.index("--command") + 1] = "echo ERROR OCCURRED"
    regex_command[regex_command.index("--regex") + 1] = "ERROR"
    regex_command[regex_command.index("--regex-execute") + 1] = "echo 'Trigger ran!'"
    result = subprocess.run(regex_command, capture_output=True, text=True)
    assert result.returncode == 0
    assert "ERROR OCCURRED" in result.stdout      # Main command output
    assert "Trigger ran!" in result.stdout        # Triggered command output

def test_no_regex_no_trigger(no_regex_command):
    """No triggered command should run if no regex is provided."""
    result = subprocess.run(no_regex_command, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Hello Again" in result.stdout
    # Ensure we DON'T see "Trigger ran!"
    assert "Trigger ran!" not in result.stdout

def test_regex_no_match(no_match_regex_command):
    """Verify that no trigger occurs when the regex does not match."""
    result = subprocess.run(no_match_regex_command, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Should Not Trigger" not in result.stdout

def test_invalid_regex(invalid_regex_command):
    """Verify that an invalid regex pattern results in an error."""
    result = subprocess.run(invalid_regex_command, capture_output=True, text=True)
    # Check for the critical error message in stderr
    assert result.returncode != 0, "Expected non-zero return code for invalid regex"
    assert "CRITICAL ERROR" in result.stderr, "Expected critical error message in stderr"
    assert "unterminated character set" in result.stderr, "Expected regex error message in stderr"